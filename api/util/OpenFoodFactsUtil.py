import requests
from typing import Optional, Dict, Any, List
import logging

try:
    from util.AmazonUtil import AmazonUtil
except ImportError:
    from .AmazonUtil import AmazonUtil


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

        self.amazon_util = AmazonUtil()

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

            # Only search Amazon if include_stores is True

            amazonResults = self.amazon_util.search_by_name(product_data['name'])

            # Use Amazon price if found, otherwise set a default
            if amazonResults.price is not None:
                product_data['price'] = amazonResults.price
            else:
                product_data['price'] = 4.04  # Default price when not found

            # Use Amazon image if found and we don't already have one
            if amazonResults.image_url is not None:
                product_data['image_url'] = amazonResults.image_url


            return product_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from Open Food Facts for UPC {upc}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Open Food Facts lookup: {str(e)}")
            return None

    async def lookup_by_upc_async(self, upc: str, include_stores: bool = True) -> Optional[Dict[str, Any]]:
        """
        Async version of lookup_by_upc for use in FastAPI and other async contexts.

        Args:
            upc: Universal Product Code
            include_stores: Whether to search stores for additional info

        Returns:
            Complete product information dictionary or None
        """
        try:
            logger.info(f"Looking up UPC {upc} on Open Food Facts (async)")

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

            # Only search Amazon if include_stores is True
            if include_stores:
                # Use async version of Amazon search

                search_name = product_data['brand'] + " " + product_data['name']

                amazonResults = await self.amazon_util.search_by_name_async(search_name)

                # Use Amazon price if found, otherwise set a default
                if amazonResults.price is not None:
                    product_data['price'] = amazonResults.price
                else:
                    product_data['price'] = 4.04  # Default price when not found

                # Use Amazon image if found and we don't already have one
                if amazonResults.image_url is not None:
                    product_data['image_url'] = amazonResults.image_url
            else:
                # Set default price when not using store lookups
                product_data['price'] = 4.04

            return product_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from Open Food Facts for UPC {upc}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Open Food Facts lookup (async): {str(e)}")
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
