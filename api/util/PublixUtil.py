import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
import re
import json
from urllib.parse import quote_plus
import logging

logger = logging.getLogger(__name__)


class PublixLookup:
    """Utility for searching Publix products."""

    def __init__(self):
        self.base_url = "https://www.publix.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

    def search_by_name(self, product_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for a product on Publix by name.

        Args:
            product_name: Product name to search for

        Returns:
            Dictionary with product details or None
        """
        try:
            logger.info(f"Searching Publix for: {product_name}")
            search_url = f"{self.base_url}/shop/search?query={quote_plus(product_name)}"

            response = requests.get(search_url, headers=self.headers, timeout=10)

            if response.status_code != 200:
                logger.error(f"Publix search failed with status {response.status_code}")
                return None

            soup = BeautifulSoup(response.text, 'html.parser')

            # Try to find product data in JSON scripts
            script_tags = soup.find_all('script', type='application/json')
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        product = self._extract_from_json(data)
                        if product:
                            return product
                except (json.JSONDecodeError, AttributeError):
                    continue

            # Fallback: Parse HTML
            first_product = soup.select_one('div[data-testid="product-card"]') or \
                          soup.select_one('div.product-item')

            if first_product:
                product = {
                    'store_name': 'Publix',
                    'available': True
                }

                # Extract product name
                name_elem = first_product.select_one('h2, .product-name')
                if name_elem:
                    product['name'] = name_elem.get_text(strip=True)

                # Extract price
                price_elem = first_product.select_one('span[data-testid="product-price"], .price')
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price_match = re.search(r'[\d.]+', price_text)
                    if price_match:
                        try:
                            product['price'] = float(price_match.group())
                        except ValueError:
                            pass

                # Extract image
                image_elem = first_product.select_one('img')
                if image_elem and image_elem.get('src'):
                    product['image_url'] = image_elem['src']

                # Extract product URL
                link_elem = first_product.select_one('a')
                if link_elem and link_elem.get('href'):
                    href = link_elem['href']
                    product['url'] = href if href.startswith('http') else self.base_url + href

                if 'name' in product or 'price' in product:
                    return product

            logger.warning(f"No Publix products found for: {product_name}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching Publix: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Publix search: {str(e)}")
            return None

    def _extract_from_json(self, data: Dict) -> Optional[Dict[str, Any]]:
        """Extract product info from JSON data."""
        product = {
            'store_name': 'Publix',
            'available': True
        }

        # Try to find product info in nested structures
        if 'product' in data:
            prod = data['product']
            product['name'] = prod.get('name')

            price_data = prod.get('price', {})
            if isinstance(price_data, dict):
                product['price'] = price_data.get('amount')
            elif isinstance(price_data, (int, float)):
                product['price'] = float(price_data)

            image_data = prod.get('image', {})
            if isinstance(image_data, dict):
                product['image_url'] = image_data.get('url')
            elif isinstance(image_data, str):
                product['image_url'] = image_data

            product['url'] = prod.get('url')

            return product if product.get('name') or product.get('price') else None

        return None


# Global instance
publix_lookup = PublixLookup()


def search_publix(product_name: str) -> Optional[Dict[str, Any]]:
    """
    Search Publix for a product by name.

    Args:
        product_name: Name of the product

    Returns:
        Product details or None
    """
    try:
        return publix_lookup.search_by_name(product_name)
    except Exception as e:
        logger.error(f"Error searching Publix for {product_name}: {str(e)}")
        return None
