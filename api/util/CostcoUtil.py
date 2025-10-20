import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
import re
import json
from urllib.parse import quote_plus
import logging

logger = logging.getLogger(__name__)


class CostcoLookup:
    """Utility for searching Costco products."""

    def __init__(self):
        self.base_url = "https://www.costco.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

    def search_by_name(self, product_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for a product on Costco by name.

        Args:
            product_name: Product name to search for

        Returns:
            Dictionary with product details or None
        """
        try:
            logger.info(f"Searching Costco for: {product_name}")
            search_url = f"{self.base_url}/s?dept=All&keyword={quote_plus(product_name)}"

            response = requests.get(search_url, headers=self.headers, timeout=10)

            if response.status_code != 200:
                logger.error(f"Costco search failed with status {response.status_code}")
                return None

            soup = BeautifulSoup(response.text, 'html.parser')

            # Try to find JSON-LD structured data
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get('@type') == 'Product':
                        product = self._extract_from_json_ld(data)
                        if product:
                            return product
                except (json.JSONDecodeError, AttributeError):
                    continue

            # Fallback: Parse HTML
            first_product = soup.select_one('div.product') or \
                          soup.select_one('div[automation-id="productList"] > div')

            if first_product:
                product = {
                    'store_name': 'Costco',
                    'available': True
                }

                # Extract product name
                name_elem = first_product.select_one('span.description a, .product-title')
                if name_elem:
                    product['name'] = name_elem.get_text(strip=True)

                # Extract price
                price_elem = first_product.select_one('div.price, span.price')
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                    if price_match:
                        try:
                            product['price'] = float(price_match.group().replace(',', ''))
                        except ValueError:
                            pass

                # Extract image
                image_elem = first_product.select_one('img')
                if image_elem and image_elem.get('src'):
                    img_src = image_elem['src']
                    product['image_url'] = img_src if img_src.startswith('http') else self.base_url + img_src

                # Extract product URL
                link_elem = first_product.select_one('a.description, a.product-title')
                if link_elem and link_elem.get('href'):
                    href = link_elem['href']
                    product['url'] = href if href.startswith('http') else self.base_url + href

                if 'name' in product or 'price' in product:
                    return product

            logger.warning(f"No Costco products found for: {product_name}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching Costco: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Costco search: {str(e)}")
            return None

    def _extract_from_json_ld(self, data: Dict) -> Optional[Dict[str, Any]]:
        """Extract product info from JSON-LD structured data."""
        product = {
            'store_name': 'Costco',
            'available': True
        }

        product['name'] = data.get('name', '')

        # Extract price
        if 'offers' in data:
            offers = data['offers']
            if isinstance(offers, dict):
                price_str = offers.get('price', '')
                try:
                    product['price'] = float(price_str) if price_str else None
                except (ValueError, TypeError):
                    pass
            elif isinstance(offers, list) and len(offers) > 0:
                price_str = offers[0].get('price', '')
                try:
                    product['price'] = float(price_str) if price_str else None
                except (ValueError, TypeError):
                    pass

        # Extract image
        if 'image' in data:
            image = data['image']
            if isinstance(image, str):
                product['image_url'] = image
            elif isinstance(image, list) and len(image) > 0:
                product['image_url'] = image[0]

        # Extract URL
        if 'url' in data:
            product['url'] = data['url']

        return product if product.get('name') else None


# Global instance
costco_lookup = CostcoLookup()


def search_costco(product_name: str) -> Optional[Dict[str, Any]]:
    """
    Search Costco for a product by name.

    Args:
        product_name: Name of the product

    Returns:
        Product details or None
    """
    try:
        return costco_lookup.search_by_name(product_name)
    except Exception as e:
        logger.error(f"Error searching Costco for {product_name}: {str(e)}")
        return None
