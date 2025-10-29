from bson import ObjectId
from fastapi import status, Depends, File, UploadFile, HTTPException, Form
from typing import Annotated, List, Optional, Any
from util.authUtil import get_current_user
from fastapi import APIRouter
from config.db import db, fs
from api.users.userModels import UserModel
from api.product.productModel import productModel, NutritionInfo, Product, FoodProduct, BookProduct
import hashlib
from typing import Dict, Union
import json
import logging
from util.OpenFoodFactsUtil import openfoodfacts_lookup
from util.BookLookupUtil import lookup_book_by_isbn
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

productRoutes = APIRouter()


async def _download_and_store_image(image_url: str, filename: str, owner_id: Optional[str] = None) -> Optional[str]:
    """
    Download an image from a URL and store it in GridFS.

    Args:
        image_url: URL of the image to download
        filename: Name to give the file
        owner_id: ID of the user who owns this file (optional, defaults to 'system')

    Returns:
        File ID string if successful, None otherwise
    """
    try:
        logger.info(f"Downloading image from: {image_url}")
        response = requests.get(image_url, timeout=10)

        if response.status_code != 200:
            logger.error(f"Failed to download image: HTTP {response.status_code}")
            return None

        image_data = response.content

        # Calculate MD5 hash for deduplication
        md5_hash = hashlib.md5(image_data).hexdigest()

        # Check if file already exists
        existing = db.files.find_one({"md5": md5_hash})

        if existing is not None:
            logger.info(f"Image already exists with MD5: {md5_hash}")
            return str(existing['_id'])

        # Store in GridFS
        gridfs_file_id = fs.put(
            image_data,
            filename=filename,
            owner=owner_id or 'system',
            content_type=response.headers.get('Content-Type', 'image/jpeg')
        )

        # Create file metadata entry
        new_fs_file = {
            "name": filename,
            "md5": md5_hash,
            "fileId": str(gridfs_file_id),
            "references": []
        }

        inserted = db.files.insert_one(new_fs_file)
        file_id = str(inserted.inserted_id)

        logger.info(f"Image stored in GridFS with ID: {file_id}")
        return file_id

    except Exception as e:
        logger.error(f"Error downloading and storing image: {str(e)}")
        return None


def calculate_md5(file):
    """Calculates the MD5 hash of the uploaded file."""
    md5_hash = hashlib.md5()
    for chunk in iter(lambda: file.read(4096), b""):
        md5_hash.update(chunk)
    file.seek(0)  # Reset the file pointer after reading
    return md5_hash.hexdigest()


def add_fsFile_reference(fsFileId: str, refId: str):
    """Adds a reference to the fsFileModel."""
    file = db.files.find_one({"_id": ObjectId(fsFileId)})
    if file is not None:
        references = file.get("references", [])
        if refId not in references:
            references.append(refId)
            db.files.update_one({"_id": ObjectId(fsFileId)}, {"$set": {"references": references}})


@productRoutes.post("")
async def create_product(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    upc: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    tags: Optional[str] = Form(None),  # JSON string of tags array
    metadata: Optional[str] = Form(None),  # JSON string of metadata dict
    images: List[UploadFile] = File(None),
    current_user: Annotated[UserModel, Depends(get_current_user('user'))] = None
):
    """
    Create a new product with details and image files.
    Images are stored in GridFS and their IDs are added to the product.
    """

    # Process uploaded images and store in GridFS
    image_ids = []

    if images:
        for image_file in images:
            # Calculate MD5 hash for deduplication
            md5 = calculate_md5(image_file.file)

            # Check if file already exists
            existing = db.files.find_one({"md5": md5})

            if existing is not None:
                # File already exists, use existing file ID
                file_id = existing['_id']
            else:
                # Upload new file to GridFS
                gridfs_file_id = fs.put(
                    image_file.file.read(),
                    filename=image_file.filename,
                    owner=current_user.id,
                    content_type=image_file.content_type
                )

                # Create file metadata entry
                new_fs_file = {
                    "name": image_file.filename,
                    "md5": md5,
                    "fileId": str(gridfs_file_id),
                    "references": []
                }

                inserted = db.files.insert_one(new_fs_file)
                file_id = inserted.inserted_id

            # Add file ID to image_ids list
            image_ids.append(str(file_id))

    # Parse tags and metadata from JSON strings if provided
    parsed_tags = None
    if tags:
        try:
            parsed_tags = json.loads(tags)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON format for tags"
            )

    parsed_metadata = None
    if metadata:
        try:
            parsed_metadata = json.loads(metadata)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON format for metadata"
            )

    # Create product document
    product_dict = {
        "name": name,
        "description": description,
        "upc": upc,
        "price": price,
        "tags": parsed_tags,
        "metadata": parsed_metadata,
        "images": image_ids,
        "last_modified": datetime.utcnow()
    }

    # Remove None values
    product_dict = {k: v for k, v in product_dict.items() if v is not None}

    # Insert product into database
    result = db.products.insert_one(product_dict)
    product_id = str(result.inserted_id)

    # Add product reference to each image file
    for image_id in image_ids:
        add_fsFile_reference(image_id, product_id)

    # Retrieve and return the created product
    created_product = db.products.find_one({"_id": result.inserted_id})
    created_product['id'] = str(created_product.pop('_id'))

    return productModel(**created_product).model_dump(exclude_none=True)


@productRoutes.get("")
async def get_all_products():
    """Get all products with appropriate models based on product type. No auth required."""
    products = []

    for product in db.products.find():
        product['id'] = str(product.pop('_id'))

        # Return appropriate model based on product_type
        product_type = product.get('product_type', 'generic')
        if product_type == 'book':
            products.append(BookProduct(**product).model_dump(exclude_none=True))
        elif product_type == 'food':
            products.append(FoodProduct(**product).model_dump(exclude_none=True))
        else:
            products.append(Product(**product).model_dump(exclude_none=True))

    return products


@productRoutes.get("/recent")
async def get_recent_products(limit: int = 100):
    """
    Get recently added/modified products sorted by last_modified timestamp.
    No auth required.

    Args:
        limit: Maximum number of products to return (default: 100)
    """
    products = []

    # Find products sorted by last_modified (newest first)
    # Filter to only include products that have last_modified field
    for product in db.products.find({"last_modified": {"$exists": True}}).sort("last_modified", -1).limit(limit):
        product['id'] = str(product.pop('_id'))

        # Return appropriate model based on product_type
        product_type = product.get('product_type', 'generic')
        if product_type == 'book':
            products.append(BookProduct(**product).model_dump(exclude_none=True))
        elif product_type == 'food':
            products.append(FoodProduct(**product).model_dump(exclude_none=True))
        else:
            products.append(Product(**product).model_dump(exclude_none=True))

    return products


@productRoutes.get("/produce")
async def get_produce_items():
    """Get all produce items (Fresh Produce brand or Fruits/Vegetables/Herbs category). No auth required."""
    products = []

    # Query for products with brand "Fresh Produce" OR category in Fruits/Vegetables/Herbs
    query = {
        "$or": [
            {"brand": "Fresh Produce"},
            {"category": {"$in": ["Fruits", "Vegetables", "Herbs"]}}
        ]
    }

    for product in db.products.find(query):
        product['id'] = str(product.pop('_id'))

        # All produce items should be food type
        products.append(FoodProduct(**product).model_dump(exclude_none=True))

    return products


def _detect_product_type(upc: str) -> str:
    """
    Detect if a UPC is likely a book (ISBN) or food product.
    ISBNs are 10 or 13 digits and start with 978 or 979 for ISBN-13.

    Args:
        upc: Universal Product Code or ISBN

    Returns:
        'book' or 'food'
    """
    # Remove any dashes or spaces
    clean_upc = upc.replace('-', '').replace(' ', '')

    # ISBN-13 starts with 978 or 979
    if len(clean_upc) == 13 and (clean_upc.startswith('978') or clean_upc.startswith('979')):
        return 'book'

    # ISBN-10 is 10 digits (less common now)
    if len(clean_upc) == 10:
        return 'book'

    # Default to food
    return 'food'


@productRoutes.get("/upc/{upc}")
async def get_product_by_upc( upc: str, cache: bool = True, product_type: Optional[str] = None):
    """
    Get a single product by UPC or ISBN.
    First checks the database. If not found, automatically detects whether
    it's a book (ISBN) or food product, then uses the appropriate lookup service.

    No authentication required - this endpoint is publicly accessible.

    Args:
        upc: Universal Product Code or ISBN
        cache: If True (default), checks database first and caches results.
               If False, always performs fresh lookup and doesn't save to database.
        product_type: Optional override to force 'book' or 'food' lookup.
                     If not provided, will auto-detect based on UPC format.
    """
    # Check if product exists in database (unless cache is disabled)
    if cache:
        product = db.products.find_one({"upc": upc})

        if product is not None:
            logger.info(f"Product found in database for UPC: {upc}")
            product['id'] = str(product.pop('_id'))

            # Return appropriate model based on product_type
            detected_type = product.get('product_type', 'food')
            if detected_type == 'book':
                return BookProduct(**product).model_dump(exclude_none=True)
            else:
                return FoodProduct(**product).model_dump(exclude_none=True)

    # Detect product type if not specified
    if product_type is None:
        product_type = _detect_product_type(upc)
        logger.info(f"Auto-detected product type: {product_type}")

    # Route to appropriate lookup service
    if product_type == 'book':
        logger.info(f"{'Cache disabled' if not cache else 'Book not in database'}, looking up ISBN {upc}")
        product_data = await _lookup_book(upc, cache)
    else:
        logger.info(f"{'Cache disabled' if not cache else 'Product not in database'}, looking up UPC {upc} using OpenFoodFacts")
        product_data = await _lookup_food(upc, cache)

    return product_data


async def _lookup_food(upc: str, cache: bool) -> Dict[str, Any]:
    """
    Look up a food product using OpenFoodFacts.

    Args:
        upc: Universal Product Code
        cache: Whether to cache the result in database

    Returns:
        Food product data dictionary
    """
    try:
        # Use async version for better performance in FastAPI
        # Include store lookups (Amazon) to get pricing and images
        product_data = await openfoodfacts_lookup.lookup_by_upc_async(upc, include_stores=True)

        if product_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product not found for UPC: {upc}"
            )

        # Ensure product_type is set
        product_data['product_type'] = 'food'

        # Set default price if not available
        if product_data.get('price') is None:
            product_data['price'] = 4.04

        # Download and store images - try Amazon first, then OpenFoodFacts
        image_ids = []
        image_source = None

        # 1. Try Amazon/store images first
        try:
            stores = product_data.get('stores', [])
            if stores and len(stores) > 0 and stores[0].get('image_url'):
                logger.info(f"Trying to download image from {stores[0].get('store_name', 'store')}")
                image_id = await _download_and_store_image(
                    stores[0]['image_url'],
                    f"{product_data.get('name', 'product')}.jpg"
                )
                if image_id:
                    image_ids.append(image_id)
                    image_source = stores[0].get('store_name', 'External Source')
                    logger.info(f"Downloaded image from {image_source}")
        except Exception as e:
            logger.error(f"Error downloading store image: {str(e)}")

        # 2. Fallback to OpenFoodFacts image if Amazon fails
        if not image_ids and product_data.get('image_url'):
            try:
                logger.info("Using OpenFoodFacts image as fallback")
                image_id = await _download_and_store_image(
                    product_data['image_url'],
                    f"{product_data.get('name', 'product')}.jpg"
                )
                if image_id:
                    image_ids.append(image_id)
                    image_source = 'OpenFoodFacts'
                    logger.info(f"Downloaded image from OpenFoodFacts")
            except Exception as e:
                logger.error(f"Error downloading OpenFoodFacts image: {str(e)}")

        # Remove the image_url from product_data as we now have GridFS IDs
        product_data.pop('image_url', None)

        # Add image IDs and source to product data
        if image_ids:
            product_data['images'] = image_ids
        if image_source:
            product_data['image_source'] = image_source

        # Only save to database if caching is enabled
        if cache:
            # Add last_modified timestamp
            product_data['last_modified'] = datetime.utcnow()

            # Insert into database
            result = db.products.insert_one(product_data)
            product_id = str(result.inserted_id)

            # Add product reference to each image file
            for image_id in image_ids:
                add_fsFile_reference(image_id, product_id)

            logger.info(f"Food product saved to database with ID: {product_id}")

            # Retrieve and return the created product
            created_product = db.products.find_one({"_id": result.inserted_id})
            created_product['id'] = str(created_product.pop('_id'))

            return FoodProduct(**created_product).model_dump(exclude_none=True)
        else:
            # Return product without saving to database
            logger.info(f"Cache disabled, returning product without saving to database")
            product_data['id'] = None  # No database ID since it wasn't saved
            return FoodProduct(**product_data).model_dump(exclude_none=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error looking up food product by UPC {upc}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error looking up product: {str(e)}"
        )


async def _lookup_book(isbn: str, cache: bool) -> Dict[str, Any]:
    """
    Look up a book using Open Library and Google Books APIs.

    Args:
        isbn: ISBN-10 or ISBN-13 number
        cache: Whether to cache the result in database

    Returns:
        Book product data dictionary
    """
    try:
        book_data = lookup_book_by_isbn(isbn)

        if book_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book not found for ISBN: {isbn}"
            )

        # Download and store cover image if available
        image_ids = []
        image_source = None

        if book_data.get('image_url'):
            try:
                image_id = await _download_and_store_image(
                    book_data['image_url'],
                    f"{book_data.get('name', 'book')}_cover.jpg"
                )
                if image_id:
                    image_ids.append(image_id)
                    image_source = book_data.get('metadata', {}).get('source', 'Book API')
            except Exception as e:
                logger.error(f"Error downloading book cover image: {str(e)}")

        # Remove the image_url from book_data as we now have GridFS IDs
        book_data.pop('image_url', None)

        # Set default price if not available
        if book_data.get('price') is None:
            book_data['price'] = 4.04

        # Add image IDs and source to book data
        if image_ids:
            book_data['images'] = image_ids
        if image_source:
            book_data['image_source'] = image_source

        # Only save to database if caching is enabled
        if cache:
            # Add last_modified timestamp
            book_data['last_modified'] = datetime.utcnow()

            # Insert into database
            result = db.products.insert_one(book_data)
            product_id = str(result.inserted_id)

            # Add product reference to each image file
            for image_id in image_ids:
                add_fsFile_reference(image_id, product_id)

            logger.info(f"Book saved to database with ID: {product_id}")

            # Retrieve and return the created book
            created_book = db.products.find_one({"_id": result.inserted_id})
            created_book['id'] = str(created_book.pop('_id'))

            return BookProduct(**created_book).model_dump(exclude_none=True)
        else:
            # Return book without saving to database
            logger.info(f"Cache disabled, returning book without saving to database")
            book_data['id'] = None  # No database ID since it wasn't saved
            return BookProduct(**book_data).model_dump(exclude_none=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error looking up book by ISBN {isbn}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error looking up book: {str(e)}"
        )


@productRoutes.get("/{id}")
async def get_product(
    id: str,
    current_user: Annotated[UserModel, Depends(get_current_user('user'))]
):
    """Get a single product by ID. Returns appropriate model based on product type."""
    product = db.products.find_one({"_id": ObjectId(id)})

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    product['id'] = str(product.pop('_id'))

    # Return appropriate model based on product_type
    product_type = product.get('product_type', 'generic')
    if product_type == 'book':
        return BookProduct(**product).model_dump(exclude_none=True)
    elif product_type == 'food':
        return FoodProduct(**product).model_dump(exclude_none=True)
    else:
        return Product(**product).model_dump(exclude_none=True)


@productRoutes.put("/{id}")
async def update_product(
    id: str,
    product: productModel,
    current_user: Annotated[UserModel, Depends(get_current_user('user'))]
):
    """Update a product and manage image references."""
    # Get existing product
    existing_product = db.products.find_one({"_id": ObjectId(id)})

    if existing_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    product_dict = product.model_dump(exclude_none=True)
    product_dict.pop('id', None)

    # Add last_modified timestamp
    product_dict['last_modified'] = datetime.utcnow()

    # Handle image reference updates
    old_images = set(existing_product.get("images", []))
    new_images = set(product_dict.get("images", []))

    # Add references for new images
    added_images = new_images - old_images
    for image_id in added_images:
        add_fsFile_reference(image_id, id)

    # Remove references for deleted images
    removed_images = old_images - new_images
    for image_id in removed_images:
        from api.files.fsFileRoutes import remove_fsFile_reference
        remove_fsFile_reference(image_id, id)

    # Update product
    result = db.products.update_one(
        {"_id": ObjectId(id)},
        {"$set": product_dict}
    )

    return {"message": "Product updated"}


@productRoutes.delete("/{id}")
async def delete_product(
    id: str,
    current_user: Annotated[UserModel, Depends(get_current_user('user'))]
):
    """Delete a product and remove references from image files."""
    product = db.products.find_one({"_id": ObjectId(id)})

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Remove product reference from all associated images
    image_ids = product.get("images", [])
    for image_id in image_ids:
        from api.files.fsFileRoutes import remove_fsFile_reference
        remove_fsFile_reference(image_id, id)

    # Delete the product
    db.products.delete_one({"_id": ObjectId(id)})

    return {"message": "Product deleted"}


@productRoutes.post("/reset")
async def reset_database(
    current_user: Annotated[UserModel, Depends(get_current_user('admin'))]
):
    """
    Reset the database by deleting all products and images.
    This is useful for testing with a clean slate.

    Requires admin privileges.
    """
    try:
        # Count documents before deletion
        products_count = db.products.count_documents({})
        files_count = db.files.count_documents({})

        # Delete all products
        db.products.delete_many({})
        logger.info(f"Deleted {products_count} products")

        # Delete all file metadata
        db.files.delete_many({})
        logger.info(f"Deleted {files_count} file metadata records")

        # Delete all files from GridFS
        # Get all file IDs from GridFS and delete them
        gridfs_files = fs.find({})
        gridfs_count = 0
        for gridfs_file in gridfs_files:
            fs.delete(gridfs_file._id)
            gridfs_count += 1
        logger.info(f"Deleted {gridfs_count} files from GridFS")

        return {
            "message": "Database reset successfully",
            "deleted": {
                "products": products_count,
                "file_metadata": files_count,
                "gridfs_files": gridfs_count
            }
        }

    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting database: {str(e)}"
        )
