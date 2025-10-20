import requests
from typing import Optional, Dict, Any, List
import logging
from util.GoogleShoppingUtil import search_google_shopping
from util.AmazonUtil import search_amazon_by_name
from util.GoogleImageUtil import search_google_images

logger = logging.getLogger(__name__)


class OpenFoodFactsLookup:
    """
    Utility class for looking up products using Open Food Facts API.
    Integrates with store utilities to get pricing and availability.
    """

    def __init__(self):
        self.base_url = "https://world.openfoodfacts.org/api/v2"
        self.headers = {
            'User-Agent': 'IzzyMart/1.0 (Product Lookup Service)',
        }

    def lookup_by_upc(self, upc: str, include_stores: bool = True) -> Optional[Dict[str, Any]]:
        """
        Look up a product by UPC using Open Food Facts.
        Optionally search stores for pricing and availability.

        Args:
            upc: Universal Product Code
            include_stores: Whether to search stores for additional info

        Returns:
            Complete product information dictionary or None
        """
        try:
            logger.info(f"Looking up UPC {upc} on Open Food Facts")

            # Query Open Food Facts API
            url = f"{self.base_url}/product/{upc}.json"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code != 200:
                logger.warning(f"Open Food Facts returned status {response.status_code} for UPC {upc}")
                return None

            data = response.json()

            if data.get('status') != 1:
                logger.warning(f"Product not found in Open Food Facts: {upc}")
                return None

            # Extract product information
            product_data = self._extract_product_data(data.get('product', {}), upc)

            # If we have a product name and stores should be included, search them
            if include_stores and product_data.get('name'):
                # Get the stores mentioned in OpenFoodFacts metadata
                stores_mentioned = product_data.get('metadata', {}).get('stores_mentioned', '')
                product_data['stores'] = self._search_stores(product_data['name'], stores_mentioned)

            return product_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from Open Food Facts for UPC {upc}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Open Food Facts lookup: {str(e)}")
            return None

    def _extract_product_data(self, product: Dict, upc: str) -> Dict[str, Any]:
        """Extract and format product data from Open Food Facts response."""
        product_data = {
            'upc': upc,
            'name': product.get('product_name') or product.get('product_name_en'),
            'brand': product.get('brands'),
            'description': product.get('generic_name') or product.get('generic_name_en'),
            'ingredients': product.get('ingredients_text') or product.get('ingredients_text_en'),
            'tags': [],
            'metadata': {}
        }

        # Extract categories as tags
        if product.get('categories_tags'):
            product_data['tags'] = [cat.replace('en:', '') for cat in product.get('categories_tags', [])]

        # Extract allergens
        allergens = product.get('allergens_tags', [])
        if allergens:
            product_data['allergens'] = [a.replace('en:', '') for a in allergens]

        # Extract nutrition information
        nutriments = product.get('nutriments', {})
        if nutriments:
            product_data['nutrition'] = self._extract_nutrition(nutriments, product)

        # Extract image URL
        if product.get('image_url'):
            product_data['image_url'] = product['image_url']
        elif product.get('image_front_url'):
            product_data['image_url'] = product['image_front_url']

        # Add additional metadata
        product_data['metadata']['openfoodfacts_id'] = product.get('_id')
        product_data['metadata']['ecoscore_grade'] = product.get('ecoscore_grade')
        product_data['metadata']['nova_group'] = product.get('nova_group')
        product_data['metadata']['packaging'] = product.get('packaging')

        # Store information from Open Food Facts (if available)
        if product.get('stores'):
            product_data['metadata']['stores_mentioned'] = product['stores']

        return product_data

    def _extract_nutrition(self, nutriments: Dict, product: Dict) -> Dict[str, Any]:
        """Extract nutrition information from nutriments data."""
        nutrition = {}

        # Serving size
        nutrition['serving_size'] = product.get('serving_size')

        # Energy (calories) - convert from kJ if needed
        if 'energy-kcal_100g' in nutriments:
            nutrition['calories'] = nutriments.get('energy-kcal_100g')
        elif 'energy_100g' in nutriments:
            # Convert kJ to kcal (1 kcal = 4.184 kJ)
            nutrition['calories'] = nutriments.get('energy_100g') / 4.184

        # Macronutrients (per 100g)
        nutrition['fat'] = nutriments.get('fat_100g')
        nutrition['saturated_fat'] = nutriments.get('saturated-fat_100g')
        nutrition['trans_fat'] = nutriments.get('trans-fat_100g')
        nutrition['cholesterol'] = nutriments.get('cholesterol_100g')
        nutrition['sodium'] = nutriments.get('sodium_100g')
        nutrition['carbohydrates'] = nutriments.get('carbohydrates_100g')
        nutrition['fiber'] = nutriments.get('fiber_100g')
        nutrition['sugars'] = nutriments.get('sugars_100g')
        nutrition['protein'] = nutriments.get('proteins_100g')

        # Nutrition grade (A-E score)
        nutrition['nutrition_grade'] = product.get('nutrition_grade_fr') or product.get('nutriscore_grade')

        # Remove None values
        nutrition = {k: v for k, v in nutrition.items() if v is not None}

        return nutrition

    def _search_stores(self, product_name: str, stores_mentioned: str = None) -> List[Dict[str, Any]]:
        """
        Search stores for the product.
        First tries Google Shopping, then falls back to Amazon if needed.
        Uses stores mentioned in OpenFoodFacts as preferred stores.

        Args:
            product_name: Name of the product to search for
            stores_mentioned: Comma-separated string of stores from OpenFoodFacts

        Returns:
            List with single store information dictionary, or empty list
        """
        logger.info(f"Searching for product: {product_name}")

        if stores_mentioned:
            logger.info(f"Stores mentioned in OpenFoodFacts: {stores_mentioned}")

        # Build list of preferred stores from OpenFoodFacts data
        preferred_stores = []
        if stores_mentioned:
            # Normalize and extract store names
            stores_lower = stores_mentioned.lower()

            # Common store mappings
            if 'publix' in stores_lower:
                preferred_stores.append('publix')
            if 'target' in stores_lower:
                preferred_stores.append('target')
            if 'costco' in stores_lower:
                preferred_stores.append('costco')
            if 'walmart' in stores_lower:
                preferred_stores.append('walmart')
            if 'amazon' in stores_lower:
                preferred_stores.append('amazon')
            if 'kroger' in stores_lower:
                preferred_stores.append('kroger')

        # Try Google Shopping first (often blocked by bot detection)
        try:
            logger.info("Trying Google Shopping...")
            result = search_google_shopping(product_name, preferred_stores if preferred_stores else None)
            if result:
                logger.info(f"Found product at {result.get('store_name', 'Unknown')}: {result.get('name')} - ${result.get('price', 'N/A')}")
                return [result]
            else:
                logger.info("No Google Shopping results found, trying Amazon fallback...")
        except Exception as e:
            logger.warning(f"Google Shopping failed: {str(e)}, trying Amazon fallback...")

        # Fallback to Amazon search
        try:
            logger.info("Searching Amazon...")
            result = search_amazon_by_name(product_name)
            if result:
                logger.info(f"Found product on Amazon: {result.get('name')} - ${result.get('price', 'N/A')}")

                # If Amazon didn't provide an image, try Google Images
                if not result.get('image_url'):
                    logger.info("No image from Amazon, trying Google Images...")
                    try:
                        image_urls = search_google_images(product_name, max_results=1)
                        if image_urls and len(image_urls) > 0:
                            result['image_url'] = image_urls[0]
                            logger.info(f"Got image from Google Images")
                    except Exception as e:
                        logger.warning(f"Google Images failed: {str(e)}")

                return [result]
            else:
                logger.warning(f"No Amazon results found for: {product_name}")

                # Last resort: Try to at least get an image from Google Images
                logger.info("Trying Google Images for product image...")
                try:
                    image_urls = search_google_images(product_name, max_results=1)
                    if image_urls and len(image_urls) > 0:
                        # Return a minimal result with just the image
                        return [{
                            'store_name': 'Google Images',
                            'name': product_name,
                            'image_url': image_urls[0],
                            'available': True
                        }]
                except Exception as e:
                    logger.warning(f"Google Images failed: {str(e)}")

                return []
        except Exception as e:
            logger.error(f"Error searching Amazon: {str(e)}")
            return []


# Global instance
openfoodfacts_lookup = OpenFoodFactsLookup()


def lookup_product_by_upc(upc: str, include_stores: bool = True) -> Optional[Dict[str, Any]]:
    """
    Convenience function to lookup a product by UPC using Open Food Facts.

    Args:
        upc: Universal Product Code
        include_stores: Whether to search stores for pricing info

    Returns:
        Complete product information or None
    """
    return openfoodfacts_lookup.lookup_by_upc(upc, include_stores=include_stores)
