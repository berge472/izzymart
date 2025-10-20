import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.http import Request
from typing import Optional, Dict, Any, List
import re
import json
from urllib.parse import quote_plus
import logging
from crochet import setup, wait_for
from twisted.internet import reactor
import time
import requests
from bs4 import BeautifulSoup

# Initialize crochet for using Scrapy in a synchronous context
setup()

logger = logging.getLogger(__name__)


class AmazonProductSpider(scrapy.Spider):
    """
    Scrapy spider for extracting product information from Amazon.
    """
    name = 'amazon_product'

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,  # Be polite, wait 2 seconds between requests
        'COOKIES_ENABLED': True,
        'RETRY_TIMES': 3,
        'REDIRECT_ENABLED': True,
        'HTTPERROR_ALLOWED_CODES': [404, 503],
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    }

    def __init__(self, upc=None, asin=None, search_mode='upc', *args, **kwargs):
        super(AmazonProductSpider, self).__init__(*args, **kwargs)
        self.upc = upc
        self.asin = asin
        self.search_mode = search_mode
        self.results = []
        self.base_url = "https://www.amazon.com"

    def start_requests(self):
        """Generate the initial request based on search mode."""
        if self.search_mode == 'upc' and self.upc:
            search_url = f"{self.base_url}/s?k={quote_plus(self.upc)}"
            yield Request(url=search_url, callback=self.parse_search_results, dont_filter=True)
        elif self.search_mode == 'asin' and self.asin:
            product_url = f"{self.base_url}/dp/{self.asin}"
            yield Request(url=product_url, callback=self.parse_product_page, dont_filter=True)

    def parse_search_results(self, response):
        """Parse Amazon search results page."""
        logger.info(f"Parsing search results from {response.url}")

        # Try to extract product data from JSON-LD
        json_ld_scripts = response.css('script[type="application/ld+json"]::text').getall()

        for json_str in json_ld_scripts:
            try:
                data = json.loads(json_str)
                if isinstance(data, dict) and data.get('@type') == 'Product':
                    product = self._extract_from_json_ld(data)
                    if product:
                        self.results.append(product)
                        return
            except json.JSONDecodeError:
                continue

        # Fallback: Parse HTML directly using CSS selectors
        # Find the first search result
        first_result = response.css('div[data-component-type="s-search-result"]').first()

        if first_result:
            product = self._parse_search_result_item(first_result)
            if product:
                self.results.append(product)
        else:
            logger.warning(f"No search results found for UPC: {self.upc}")

    def parse_product_page(self, response):
        """Parse Amazon product detail page."""
        logger.info(f"Parsing product page from {response.url}")

        product = {
            'metadata': {'asin': self.asin}
        }

        # Extract product title
        title = response.css('#productTitle::text').get()
        if title:
            product['name'] = title.strip()

        # Extract price - try multiple selectors
        price_whole = response.css('span.a-price-whole::text').get() or \
                     response.css('#priceblock_ourprice::text').get() or \
                     response.css('#priceblock_dealprice::text').get()

        if price_whole:
            try:
                price_str = price_whole.replace(',', '').replace('$', '').strip()
                product['price'] = float(price_str)
            except (ValueError, AttributeError):
                product['price'] = None

        # Extract main image
        image_url = response.css('#landingImage::attr(src)').get() or \
                   response.css('#imgBlkFront::attr(src)').get()
        if image_url:
            product['image_url'] = image_url

        # Extract description from feature bullets
        feature_bullets = response.css('#feature-bullets span.a-list-item::text').getall()
        if feature_bullets:
            description_parts = [f.strip() for f in feature_bullets if f.strip()]
            product['description'] = ' '.join(description_parts)

        # Extract brand
        brand = response.css('#bylineInfo::text').get()
        if brand:
            brand_clean = brand.strip().replace('Visit the ', '').replace(' Store', '').replace('Brand: ', '')
            product['metadata']['brand'] = brand_clean

        # Extract rating
        rating = response.css('span.a-icon-alt::text').get()
        if rating:
            rating_match = re.search(r'([\d.]+)\s*out of', rating)
            if rating_match:
                product['metadata']['rating'] = rating_match.group(1)

        # Extract review count
        review_count = response.css('#acrCustomerReviewText::text').get()
        if review_count:
            count_match = re.search(r'([\d,]+)', review_count)
            if count_match:
                product['metadata']['review_count'] = count_match.group(1).replace(',', '')

        product['amazon_url'] = f"{self.base_url}/dp/{self.asin}"

        if 'name' in product:
            self.results.append(product)
        else:
            logger.warning(f"Could not extract product name for ASIN: {self.asin}")

    def _parse_search_result_item(self, item):
        """Parse a single search result item."""
        product = {
            'upc': self.upc,
            'metadata': {}
        }

        # Extract product title
        title = item.css('h2 span.a-text-normal::text').get() or \
               item.css('h2 a span::text').get()
        if title:
            product['name'] = title.strip()
        else:
            return None

        # Extract price
        price_whole = item.css('span.a-price-whole::text').get()
        if price_whole:
            try:
                price_str = price_whole.replace(',', '').replace('$', '').strip()
                product['price'] = float(price_str)
            except (ValueError, AttributeError):
                product['price'] = None

        # Extract image URL
        image_url = item.css('img.s-image::attr(src)').get()
        if image_url:
            product['image_url'] = image_url

        # Extract product URL and ASIN
        product_link = item.css('h2 a.a-link-normal::attr(href)').get()
        if product_link:
            if product_link.startswith('/'):
                product['amazon_url'] = self.base_url + product_link
            else:
                product['amazon_url'] = product_link

            # Extract ASIN from URL
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', product['amazon_url'])
            if asin_match:
                product['metadata']['asin'] = asin_match.group(1)

        # Extract brand
        brand = item.css('span.a-size-base-plus::text').get()
        if brand and brand.strip() and not brand.strip().startswith('$'):
            product['metadata']['brand'] = brand.strip()

        # Extract rating
        rating = item.css('span.a-icon-alt::text').get()
        if rating:
            rating_match = re.search(r'([\d.]+)\s*out of', rating)
            if rating_match:
                product['metadata']['rating'] = rating_match.group(1)

        return product

    def _extract_from_json_ld(self, data):
        """Extract product information from JSON-LD structured data."""
        product = {
            'name': data.get('name', ''),
            'description': data.get('description', ''),
            'upc': self.upc,
            'metadata': {}
        }

        # Extract price
        if 'offers' in data:
            offers = data['offers']
            if isinstance(offers, dict):
                price_str = offers.get('price', '')
                try:
                    product['price'] = float(price_str) if price_str else None
                except (ValueError, TypeError):
                    product['price'] = None
            elif isinstance(offers, list) and len(offers) > 0:
                price_str = offers[0].get('price', '')
                try:
                    product['price'] = float(price_str) if price_str else None
                except (ValueError, TypeError):
                    product['price'] = None

        # Extract image URL
        if 'image' in data:
            image = data['image']
            if isinstance(image, str):
                product['image_url'] = image
            elif isinstance(image, list) and len(image) > 0:
                product['image_url'] = image[0]

        # Extract product URL
        if 'url' in data:
            product['amazon_url'] = data['url']

        # Store additional metadata
        if isinstance(data.get('brand'), dict):
            product['metadata']['brand'] = data['brand'].get('name', '')
        else:
            product['metadata']['brand'] = data.get('brand', '')

        product['metadata']['sku'] = data.get('sku', '')

        if 'aggregateRating' in data:
            rating = data['aggregateRating']
            product['metadata']['rating'] = rating.get('ratingValue', '')
            product['metadata']['review_count'] = rating.get('reviewCount', '')

        return product if product.get('name') else None


class AmazonProductLookup:
    """
    Main utility class for looking up products on Amazon using Scrapy.
    Uses crochet to run Scrapy in a synchronous context (compatible with FastAPI).
    """

    def __init__(self):
        self.runner = CrawlerRunner()

    @wait_for(timeout=30.0)
    def search_by_upc(self, upc: str) -> Optional[Dict[str, Any]]:
        """
        Search for a product on Amazon by UPC code.

        Args:
            upc: The Universal Product Code to search for

        Returns:
            Dictionary containing product details if found, None otherwise
        """
        logger.info(f"Starting Scrapy search for UPC: {upc}")

        # Create spider instance
        spider = AmazonProductSpider(upc=upc, search_mode='upc')

        # Run the spider
        deferred = self.runner.crawl(spider)

        # Wait for spider to complete and return results
        deferred.addCallback(lambda _: spider.results[0] if spider.results else None)

        return deferred

    @wait_for(timeout=30.0)
    def get_product_details_by_asin(self, asin: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed product information by ASIN (Amazon Standard Identification Number).

        Args:
            asin: Amazon Standard Identification Number

        Returns:
            Dictionary containing product details if found, None otherwise
        """
        logger.info(f"Starting Scrapy search for ASIN: {asin}")

        # Create spider instance
        spider = AmazonProductSpider(asin=asin, search_mode='asin')

        # Run the spider
        deferred = self.runner.crawl(spider)

        # Wait for spider to complete and return results
        deferred.addCallback(lambda _: spider.results[0] if spider.results else None)

        return deferred


# Global instance
amazon_lookup = AmazonProductLookup()


def lookup_product_by_upc(upc: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function to lookup a product by UPC on Amazon.

    Args:
        upc: Universal Product Code

    Returns:
        Product details dictionary or None if not found
    """
    try:
        return amazon_lookup.search_by_upc(upc)
    except Exception as e:
        logger.error(f"Error looking up product by UPC {upc}: {str(e)}")
        return None


def lookup_product_by_asin(asin: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function to lookup a product by ASIN on Amazon.

    Args:
        asin: Amazon Standard Identification Number

    Returns:
        Product details dictionary or None if not found
    """
    try:
        return amazon_lookup.get_product_details_by_asin(asin)
    except Exception as e:
        logger.error(f"Error looking up product by ASIN {asin}: {str(e)}")
        return None


def search_amazon_by_name(product_name: str) -> Optional[Dict[str, Any]]:
    """
    Search Amazon for a product by name using requests (no Scrapy).
    Returns price and image URL for the first result.

    Args:
        product_name: Name of the product to search for

    Returns:
        Dictionary with store_name, name, price, image_url, url or None
    """
    try:
        logger.info(f"Searching Amazon for: {product_name}")

        base_url = "https://www.amazon.com"
        search_url = f"{base_url}/s?k={quote_plus(product_name)}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

        response = requests.get(search_url, headers=headers, timeout=10)

        if response.status_code != 200:
            logger.error(f"Amazon search failed with status {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find first search result
        first_result = soup.select_one('div[data-component-type="s-search-result"]')

        if not first_result:
            logger.warning(f"No Amazon results found for: {product_name}")
            return None

        product = {
            'store_name': 'Amazon',
            'available': True
        }

        # Extract product title
        title_elem = first_result.select_one('h2 span')
        if title_elem:
            product['name'] = title_elem.get_text(strip=True)

        # Extract price
        price_whole = first_result.select_one('span.a-price-whole')
        if price_whole:
            price_text = price_whole.get_text(strip=True).replace(',', '').replace('$', '')
            try:
                product['price'] = float(price_text)
            except ValueError:
                pass

        # Extract image
        image_elem = first_result.select_one('img.s-image')
        if image_elem and image_elem.get('src'):
            product['image_url'] = image_elem['src']

        # Extract product URL
        link_elem = first_result.select_one('h2 a')
        if link_elem and link_elem.get('href'):
            href = link_elem['href']
            product['url'] = href if href.startswith('http') else base_url + href

        if 'name' in product or 'price' in product:
            logger.info(f"Found Amazon product: {product.get('name', 'Unknown')} - ${product.get('price', 'N/A')}")
            return product

        return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching Amazon: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in Amazon search: {str(e)}")
        return None
