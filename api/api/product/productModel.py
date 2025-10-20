from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import date


class NutritionInfo(BaseModel):
    """Nutrition information for a product"""
    serving_size: Optional[str] = Field(title="Serving Size", default=None)
    calories: Optional[float] = Field(title="Calories", default=None)
    fat: Optional[float] = Field(title="Total Fat (g)", default=None)
    saturated_fat: Optional[float] = Field(title="Saturated Fat (g)", default=None)
    trans_fat: Optional[float] = Field(title="Trans Fat (g)", default=None)
    cholesterol: Optional[float] = Field(title="Cholesterol (mg)", default=None)
    sodium: Optional[float] = Field(title="Sodium (mg)", default=None)
    carbohydrates: Optional[float] = Field(title="Carbohydrates (g)", default=None)
    fiber: Optional[float] = Field(title="Fiber (g)", default=None)
    sugars: Optional[float] = Field(title="Sugars (g)", default=None)
    protein: Optional[float] = Field(title="Protein (g)", default=None)
    nutrition_grade: Optional[str] = Field(title="Nutrition Grade", description="A-E nutrition score", default=None)


class Product(BaseModel):
    """Base product model with common fields"""
    id: Optional[str] = Field(title="Product ID", description="Unique identifier for the product", default=None)
    product_type: str = Field(title="Product Type", description="Type of product (food, book, etc.)", default="generic")
    name: Optional[str] = Field(title="Product Name", description="Name of the product", default=None)
    description: Optional[str] = Field(title="Product Description", description="Detailed description of the product", default=None)
    upc: Optional[str] = Field(title="Product UPC", description="Universal Product Code or ISBN", default=None)
    price: Optional[float] = Field(title="Product Price", description="Price of the product", default=None)
    price_source: Optional[str] = Field(title="Price Source", description="Store where the price was obtained", default=None)
    tags: Optional[List[str]] = Field(title="Product Tags", description="List of tags associated with the product", default=None)
    metadata: Optional[Dict[str, Any]] = Field(title="Product Metadata", description="Additional metadata for the product", default=None)
    images: Optional[List[str]] = Field(title="Product Images", description="List of image IDs for the product", default=None)
    image_source: Optional[str] = Field(title="Image Source", description="Store where the images were obtained", default=None)
    brand: Optional[str] = Field(title="Brand", description="Product brand name", default=None)


class FoodProduct(Product):
    """Food product model with nutrition information"""
    product_type: Literal["food"] = "food"
    nutrition: Optional[NutritionInfo] = Field(title="Nutrition Information", description="Nutritional information for the product", default=None)
    ingredients: Optional[str] = Field(title="Ingredients", description="Product ingredients list", default=None)
    allergens: Optional[List[str]] = Field(title="Allergens", description="List of allergens in the product", default=None)


class BookProduct(Product):
    """Book product model with book-specific information"""
    product_type: Literal["book"] = "book"
    isbn: Optional[str] = Field(title="ISBN", description="International Standard Book Number", default=None)
    author: Optional[str] = Field(title="Author", description="Book author(s)", default=None)
    publisher: Optional[str] = Field(title="Publisher", description="Book publisher", default=None)
    publication_date: Optional[str] = Field(title="Publication Date", description="Date the book was published", default=None)
    page_count: Optional[int] = Field(title="Page Count", description="Number of pages in the book", default=None)
    language: Optional[str] = Field(title="Language", description="Language the book is written in", default=None)
    categories: Optional[List[str]] = Field(title="Categories", description="Book categories or genres", default=None)


# Legacy alias for backward compatibility
productModel = Product