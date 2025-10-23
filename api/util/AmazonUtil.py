import logging
from typing import Optional
from urllib.parse import quote_plus
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright, TimeoutError as AsyncPlaywrightTimeoutError

# Thread pool for running sync Playwright in async context
_thread_pool = ThreadPoolExecutor(max_workers=5, thread_name_prefix="amazon_search")


class AmazonSearchResult:
    """Class to hold Amazon search result information."""
    def __init__(self):
        self.price = None
        self.image_url = None
        self.title = None
        self.asin = None
        self.url = None


class AmazonUtil:
    """
    Utility class for searching Amazon products and extracting pricing/images.
    Uses Playwright to handle Amazon's dynamic content.

    Provides both sync and async methods:
    - search_by_name(): Synchronous search for use in non-async code
    - search_by_name_async(): Async search for use in FastAPI and async contexts

    The async version runs Playwright in a thread pool to avoid blocking the event loop.
    """

    def __init__(self):
        self.base_url = "https://www.amazon.com"

    def search_by_name(self, product_name: str) -> AmazonSearchResult:
        """
        Search for a product by name on Amazon and return the first result.

        Note: This is a synchronous wrapper. When called from async context,
        it runs the search in a thread pool to avoid blocking the event loop.

        Args:
            product_name: The product name to search for

        Returns:
            AmazonSearchResult object with price and image_url (may be None if not found)
        """
        result = AmazonSearchResult()

        if not product_name:
            logger.warning("Empty product name provided")
            return result

        # Check if we're running inside an asyncio event loop
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context - this is a blocking call but unavoidable
            # The caller should use search_by_name_async() for true async behavior
            logger.warning("search_by_name() called from async context - use search_by_name_async() for better performance")
            future = loop.run_in_executor(_thread_pool, self._search_sync, product_name)
            # This creates a future but we need to return synchronously
            # This is not ideal - callers in async context should use the async version
            return asyncio.run_coroutine_threadsafe(
                asyncio.wrap_future(future),
                loop
            ).result(timeout=120)
        except RuntimeError:
            # No event loop running, use sync version directly
            pass
        except Exception as e:
            logger.error(f"Error running Amazon search: {e}")
            return result

        return self._search_sync(product_name)

    async def search_by_name_async(self, product_name: str) -> AmazonSearchResult:
        """
        Async version of search_by_name for use in async contexts.
        Runs the sync Playwright code in a thread pool executor.

        Args:
            product_name: The product name to search for

        Returns:
            AmazonSearchResult object with price and image_url (may be None if not found)
        """
        if not product_name:
            logger.warning("Empty product name provided")
            return AmazonSearchResult()

        try:
            loop = asyncio.get_running_loop()
            logger.info("Running Amazon search in thread pool (async)")
            result = await loop.run_in_executor(_thread_pool, self._search_sync, product_name)
            return result
        except Exception as e:
            logger.error(f"Error in async Amazon search: {e}")
            return AmazonSearchResult()

    def _search_sync(self, product_name: str) -> AmazonSearchResult:
        """Synchronous version of Amazon search using sync Playwright API."""
        result = AmazonSearchResult()
        search_url = f"{self.base_url}/s?k={quote_plus(product_name)}"

        try:
            with sync_playwright() as p:
                # Launch browser with anti-detection measures
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                    ]
                )

                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080},
                    locale='en-US',
                    timezone_id='America/New_York'
                )

                # Set additional headers
                context.set_extra_http_headers({
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                })

                page = context.new_page()

                logger.info(f"Searching Amazon for: {product_name}")

                try:
                    page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                except PlaywrightTimeoutError:
                    logger.warning("Amazon page load timed out, continuing anyway")

                # Wait for search results to load
                page.wait_for_timeout(3000)

                # Try to find the first product result
                # Amazon uses various selectors for product cards
                product_selectors = [
                    '[data-component-type="s-search-result"]',
                    '.s-result-item[data-asin]',
                    'div[data-component-type="s-search-result"]',
                    '.s-result-item',
                ]

                first_product = None
                for selector in product_selectors:
                    try:
                        page.wait_for_selector(selector, timeout=5000)
                        # Get all matching elements and find the first valid one
                        elements = page.query_selector_all(selector)
                        for elem in elements:
                            # Skip sponsored results if possible
                            asin = elem.get_attribute('data-asin')
                            if asin and asin != '':
                                first_product = elem
                                result.asin = asin
                                logger.info(f"Found product with ASIN: {asin}")
                                break
                        if first_product:
                            break
                    except PlaywrightTimeoutError:
                        continue

                if not first_product:
                    logger.warning("No product found in Amazon search results")
                    browser.close()
                    return result

                # Extract price
                price_selectors = [
                    '.a-price .a-offscreen',
                    'span.a-price-whole',
                    '.a-price span[aria-hidden="true"]',
                    'span[data-a-color="price"]',
                    '.a-color-price',
                ]

                for price_sel in price_selectors:
                    price_elem = first_product.query_selector(price_sel)
                    if price_elem:
                        price_text = price_elem.inner_text().strip()
                        # Extract numeric value (e.g., "$12.99" -> 12.99 or "12 99" -> 12.99)
                        price_match = re.search(r'[\$]?\s*(\d+)[.,\s]?(\d{0,2})', price_text)
                        if price_match:
                            dollars = price_match.group(1)
                            cents = price_match.group(2) if price_match.group(2) else '00'
                            # Pad cents to 2 digits
                            cents = cents.ljust(2, '0')
                            result.price = float(f"{dollars}.{cents}")
                            logger.info(f"Found price: ${result.price}")
                            break

                # Extract image URL
                img_selectors = [
                    'img.s-image',
                    'img[data-image-latency="s-product-image"]',
                    '.s-product-image-container img',
                    'img',
                ]

                for img_sel in img_selectors:
                    img_elem = first_product.query_selector(img_sel)
                    if img_elem:
                        # Try different image attributes
                        img_url = (img_elem.get_attribute('src') or
                                  img_elem.get_attribute('data-src') or
                                  img_elem.get_attribute('srcset'))

                        if img_url:
                            # If srcset, take the first URL
                            if ',' in img_url:
                                img_url = img_url.split(',')[0].strip().split(' ')[0]

                            # Skip placeholder images
                            if 'data:image' not in img_url and 'transparent-pixel' not in img_url:
                                result.image_url = img_url
                                logger.info(f"Found image URL: {img_url[:80]}...")
                                break

                # Extract title
                title_selectors = [
                    'h2 a span',
                    'h2 span',
                    '.a-size-medium.a-color-base.a-text-normal',
                ]

                for title_sel in title_selectors:
                    title_elem = first_product.query_selector(title_sel)
                    if title_elem:
                        result.title = title_elem.inner_text().strip()
                        logger.info(f"Found title: {result.title[:60]}...")
                        break

                # Extract product URL
                link_elem = first_product.query_selector('h2 a, a.a-link-normal')
                if link_elem:
                    href = link_elem.get_attribute('href')
                    if href:
                        # Make URL absolute
                        if href.startswith('/'):
                            result.url = self.base_url + href
                        else:
                            result.url = href

                browser.close()

                if not result.price and not result.image_url:
                    logger.warning("Could not extract price or image from Amazon result")

                return result

        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout while searching Amazon: {e}")
            return result
        except Exception as e:
            logger.error(f"Error searching Amazon: {e}")
            return result


if __name__ == "__main__":
    # Test the AmazonUtil
    import sys
    import os

    # Enable logging
    logging.basicConfig(level=logging.INFO)

    amazon = AmazonUtil()

    # Test search
    test_products = ["goldfish crackers", "organic milk", "iPhone"]

    for product in test_products:
        print(f"\n{'='*60}")
        print(f"Searching for: {product}")
        print('='*60)

        result = amazon.search_by_name(product)

        if result.price or result.image_url:
            print(f"✓ Result found:")
            if result.title:
                print(f"  Title: {result.title}")
            if result.price:
                print(f"  Price: ${result.price}")
            if result.image_url:
                print(f"  Image: {result.image_url[:100]}...")
            if result.asin:
                print(f"  ASIN: {result.asin}")
            if result.url:
                print(f"  URL: {result.url[:100]}...")
        else:
            print("✗ No result found")
