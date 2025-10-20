from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import Stealth
from typing import Optional, Dict, Any, List
import re
from urllib.parse import quote_plus
import logging
import random
import time

logger = logging.getLogger(__name__)


class GoogleShoppingLookup:
    """
    Utility for searching Google Shopping to find product prices and images.
    Uses Playwright with stealth techniques to avoid bot detection.
    """

    def __init__(self):
        self.base_url = "https://www.google.com/search"

    def search_product(self, product_name: str, preferred_stores: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Search Google Shopping for a product by name using Playwright.

        Args:
            product_name: Name of the product to search for
            preferred_stores: List of preferred store names (e.g., ['publix', 'target', 'costco'])

        Returns:
            Dictionary with product details from the best matching store, or None
        """
        try:
            logger.info(f"Searching Google Shopping for: {product_name}")

            # Build the search URL with Google Shopping parameters
            search_url = f"{self.base_url}?q={quote_plus(product_name)}&tbm=shop&hl=en&gl=us"

            with sync_playwright() as p:
                # Launch browser in headless mode
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-gpu',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process',
                    ]
                )

                # Create a new browser context with realistic viewport
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    locale='en-US',
                    timezone_id='America/New_York',
                )

                page = context.new_page()

                # Apply stealth techniques to avoid detection
                stealth = Stealth()
                stealth.apply_stealth_sync(page)

                # Add random delay to mimic human behavior
                time.sleep(random.uniform(0.5, 1.5))

                # Navigate to the search URL
                logger.info(f"Navigating to: {search_url}")
                page.goto(search_url, wait_until='networkidle', timeout=30000)

                # Random delay after page load
                time.sleep(random.uniform(1, 2))

                # Check if we got blocked by CAPTCHA
                page_content = page.content()

                # Save page for debugging
                try:
                    with open('/tmp/playwright_google_response.html', 'w', encoding='utf-8') as f:
                        f.write(page_content)
                    logger.info("Saved page content to /tmp/playwright_google_response.html")
                except Exception as e:
                    logger.debug(f"Could not save debug HTML: {str(e)}")

                if 'detected unusual traffic' in page_content.lower() or 'captcha' in page_content.lower():
                    logger.error("Google is showing CAPTCHA or blocking message")
                    browser.close()
                    return None

                # Wait for shopping results to load
                try:
                    # Try to wait for shopping results container
                    page.wait_for_selector('div[data-hveid]', timeout=5000)
                except PlaywrightTimeoutError:
                    logger.warning("Shopping results container not found within timeout")

                # Parse the results
                shopping_results = self._parse_shopping_results(page)

                browser.close()

                if not shopping_results:
                    logger.warning(f"No Google Shopping results found for: {product_name}")
                    return None

                # If we have preferred stores, try to find a match
                if preferred_stores:
                    preferred_stores_lower = [s.lower() for s in preferred_stores]
                    for result in shopping_results:
                        store_name = result.get('store_name', '').lower()
                        # Check if any preferred store is in the store name
                        for preferred in preferred_stores_lower:
                            if preferred in store_name:
                                logger.info(f"Found preferred store match: {result.get('store_name')}")
                                return result

                # If no preferred store match, return the first result
                logger.info(f"Using first result from: {shopping_results[0].get('store_name', 'Unknown')}")
                return shopping_results[0]

        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout error searching Google Shopping: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Google Shopping search: {str(e)}")
            return None

    def _parse_shopping_results(self, page) -> List[Dict[str, Any]]:
        """
        Parse Google Shopping results from the page using Playwright.

        Returns:
            List of product dictionaries
        """
        results = []

        # Google Shopping uses several different layouts, try them all
        selectors_to_try = [
            'div.sh-dgr__content',           # Standard shopping grid
            'div[data-docid]',               # Alternative layout
            'div.KZmu8e',                    # Older layout
            'div.sh-np__product-grid-item',  # Product grid item
            'div.xcR77',                     # Another variant
            'div[data-hveid]',               # Generic result container
        ]

        product_cards = []
        for selector in selectors_to_try:
            product_cards = page.query_selector_all(selector)
            if product_cards:
                logger.info(f"Found {len(product_cards)} product cards using selector: {selector}")
                break

        if not product_cards:
            logger.warning("No product cards found with any known selector")
            return results

        for card in product_cards[:10]:  # Check first 10 cards
            try:
                product = self._extract_product_from_card(card)
                if product and product.get('price'):  # Only include results with a price
                    logger.info(f"Successfully parsed product: {product.get('name', 'Unknown')[:50]}... at ${product.get('price')}")
                    results.append(product)
            except Exception as e:
                logger.debug(f"Error parsing product card: {str(e)}")
                continue

        return results

    def _extract_product_from_card(self, card) -> Optional[Dict[str, Any]]:
        """
        Extract product information from a Google Shopping result card using Playwright.

        Returns:
            Dictionary with product details or None
        """
        product = {
            'available': True
        }

        # Extract product title - try multiple selectors
        title_selectors = [
            'h3', 'h4',
            'div[role="heading"]',
            'div.tAxDx',
            'a[title]',
            'span.translate-content',
        ]

        title_text = None
        for selector in title_selectors:
            title_elem = card.query_selector(selector)
            if title_elem:
                title_text = title_elem.inner_text().strip()
                if title_text:
                    product['name'] = title_text
                    break

        # If no title found, try getting title attribute from link
        if not title_text:
            link = card.query_selector('a[title]')
            if link:
                title = link.get_attribute('title')
                if title:
                    product['name'] = title

        # Extract price - try multiple approaches
        price_selectors = [
            'span.a8Pemb',
            'span[aria-label*="$"]',
            'div.a8Pemb',
            'b',
            'span.HRLxBb',
        ]

        price_text = None
        for selector in price_selectors:
            price_elem = card.query_selector(selector)
            if price_elem:
                price_text = price_elem.inner_text().strip()
                if price_text:
                    break

        # If no price element found, search all text for price pattern
        if not price_text:
            card_text = card.inner_text()
            price_match = re.search(r'\$[\d,]+\.?\d*', card_text)
            if price_match:
                price_text = price_match.group(0)

        if price_text:
            # Extract numeric price - be flexible with format
            price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
            if price_match:
                try:
                    price_str = price_match.group(1).replace(',', '')
                    product['price'] = float(price_str)
                except (ValueError, AttributeError):
                    pass

        # Extract store name - try multiple approaches
        store_selectors = [
            'div.aULzUe',
            'div.IuHnof',
            'span.E5ocAb',
            'div.a1B3Mb',
            'span.dD8iuc',
        ]

        store_text = None
        for selector in store_selectors:
            store_elem = card.query_selector(selector)
            if store_elem:
                store_text = store_elem.inner_text().strip()
                if store_text:
                    break

        if store_text:
            # Clean up store name
            product['store_name'] = store_text.replace('from ', '').replace('From ', '').replace('at ', '')
        else:
            # Try to find store in link URL
            link = card.query_selector('a[href]')
            if link:
                href = link.get_attribute('href')
                if href:
                    # Try to extract domain from URL
                    domain_match = re.search(r'https?://(?:www\.)?([^/?.]+)', href)
                    if domain_match:
                        domain = domain_match.group(1)
                        # Clean up domain to get store name
                        store_name = domain.split('.')[0]
                        product['store_name'] = store_name.capitalize()

        # Extract image - try multiple sources
        img_elem = card.query_selector('img')
        if img_elem:
            # Google uses various attributes for images
            img_url = (img_elem.get_attribute('data-src') or
                      img_elem.get_attribute('src') or
                      img_elem.get_attribute('data-lazy-src'))

            if img_url:
                # Skip tiny placeholder images
                if img_url.startswith('http') and 'base64' not in img_url:
                    product['image_url'] = img_url
                elif img_url.startswith('//'):
                    product['image_url'] = 'https:' + img_url

        # Extract product URL
        link_elem = card.query_selector('a[href]')
        if link_elem:
            href = link_elem.get_attribute('href')
            if href:
                product['url'] = href

        # Only return if we have at least name and price
        if product.get('name') and product.get('price'):
            return product

        return None


# Global instance
google_shopping = GoogleShoppingLookup()


def search_google_shopping(product_name: str, preferred_stores: List[str] = None) -> Optional[Dict[str, Any]]:
    """
    Search Google Shopping for a product.

    Args:
        product_name: Name of the product
        preferred_stores: List of preferred store names (e.g., ['publix', 'target', 'costco'])

    Returns:
        Product details from Google Shopping or None
    """
    try:
        return google_shopping.search_product(product_name, preferred_stores)
    except Exception as e:
        logger.error(f"Error in Google Shopping search for {product_name}: {str(e)}")
        return None
