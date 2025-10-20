from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import Stealth
from typing import Optional, List
import logging
import random
import time
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class GoogleImageLookup:
    """
    Utility for searching Google Images to find product images.
    Uses Playwright with stealth techniques to avoid bot detection.
    """

    def __init__(self):
        self.base_url = "https://www.google.com/search"

    def search_product_images(self, product_name: str, max_results: int = 5) -> Optional[List[str]]:
        """
        Search Google Images for a product by name.

        Args:
            product_name: Name of the product to search for
            max_results: Maximum number of image URLs to return (default 5)

        Returns:
            List of image URLs, or None if search fails
        """
        try:
            logger.info(f"Searching Google Images for: {product_name}")

            # Build the search URL with Google Images parameters
            search_url = f"{self.base_url}?q={quote_plus(product_name)}&tbm=isch&hl=en"

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
                    ]
                )

                # Create a new browser context with realistic viewport
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    locale='en-US',
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
                if 'detected unusual traffic' in page_content.lower() or 'captcha' in page_content.lower():
                    logger.error("Google is showing CAPTCHA or blocking message")
                    browser.close()
                    return None

                # Wait for images to load
                try:
                    # Try to wait for image results
                    page.wait_for_selector('img', timeout=5000)
                except PlaywrightTimeoutError:
                    logger.warning("Image results not found within timeout")

                # Parse the image results
                image_urls = self._extract_image_urls(page, max_results)

                browser.close()

                if not image_urls:
                    logger.warning(f"No Google Image results found for: {product_name}")
                    return None

                logger.info(f"Found {len(image_urls)} image URLs")
                return image_urls

        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout error searching Google Images: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Google Images search: {str(e)}")
            return None

    def _extract_image_urls(self, page, max_results: int) -> List[str]:
        """
        Extract image URLs from Google Images results page.

        Returns:
            List of image URL strings
        """
        image_urls = []

        # Google Images uses several different selectors
        selectors_to_try = [
            'div[data-id] img',     # Main image container
            'img.rg_i',             # Result grid images
            'img.yWs4tf',           # Alternative layout
            'img[data-src]',        # Images with data-src
        ]

        image_elements = []
        for selector in selectors_to_try:
            image_elements = page.query_selector_all(selector)
            if image_elements:
                logger.info(f"Found {len(image_elements)} images using selector: {selector}")
                break

        if not image_elements:
            logger.warning("No image elements found with any known selector")
            return image_urls

        # Extract URLs from image elements
        for img in image_elements[:max_results * 2]:  # Get extra in case some are invalid
            if len(image_urls) >= max_results:
                break

            try:
                # Try multiple attributes where image URLs might be stored
                src = (img.get_attribute('src') or
                       img.get_attribute('data-src') or
                       img.get_attribute('data-iurl'))

                if src:
                    # Filter out invalid URLs
                    # Skip base64 encoded images
                    if 'data:image' in src or 'base64' in src:
                        continue

                    # Skip tiny placeholder/logo images
                    if any(x in src.lower() for x in ['logo', 'icon', '1x1', 'pixel']):
                        continue

                    # Only include HTTP/HTTPS URLs
                    if src.startswith('http'):
                        if src not in image_urls:  # Avoid duplicates
                            image_urls.append(src)
                            logger.debug(f"Found image URL: {src[:100]}...")
                    elif src.startswith('//'):
                        # Handle protocol-relative URLs
                        full_url = 'https:' + src
                        if full_url not in image_urls:
                            image_urls.append(full_url)
                            logger.debug(f"Found image URL: {full_url[:100]}...")

            except Exception as e:
                logger.debug(f"Error extracting image URL: {str(e)}")
                continue

        return image_urls


# Global instance
google_image_lookup = GoogleImageLookup()


def search_google_images(product_name: str, max_results: int = 5) -> Optional[List[str]]:
    """
    Search Google Images for a product and return image URLs.

    Args:
        product_name: Name of the product
        max_results: Maximum number of image URLs to return (default 5)

    Returns:
        List of image URLs or None
    """
    try:
        return google_image_lookup.search_product_images(product_name, max_results)
    except Exception as e:
        logger.error(f"Error in Google Images search for {product_name}: {str(e)}")
        return None
