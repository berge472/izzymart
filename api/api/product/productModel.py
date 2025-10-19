from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class productModel(BaseModel):
    id: Optional[str] = Field(title="Product ID", description="Unique identifier for the product", default=None)
    name: Optional[str] = Field(title="Product Name", description="Name of the product", default=None)
    description: Optional[str] = Field(title="Product Description", description="Detailed description of the product", default=None)
    upc: Optional[str] = Field(title="Product UPC", description="Universal Product Code", default=None)
    price: Optional[float] = Field(title="Product Price", description="Price of the product", default=None)
    tags: Optional[List[str]] = Field(title="Product Tags", description="List of tags associated with the product", default=None)
    metadata: Optional[Dict[str, Any]] = Field(title="Product Metadata", description="Additional metadata for the product", default=None)
    images: Optional[List[str]] = Field(title="Product Images", description="List of image IDs for the product", default=None)