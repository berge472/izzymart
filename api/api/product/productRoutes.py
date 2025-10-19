from bson import ObjectId
from fastapi import status, Depends, File, UploadFile, HTTPException, Form
from typing import Annotated, List, Optional
from util.authUtil import get_current_user
from fastapi import APIRouter
from config.db import db, fs
from api.users.userModels import UserModel
from api.product.productModel import productModel
import hashlib
from typing import Dict
import json

productRoutes = APIRouter()


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
        "images": image_ids
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
async def get_all_products(
    current_user: Annotated[UserModel, Depends(get_current_user('user'))]
):
    """Get all products."""
    products = []

    for product in db.products.find():
        product['id'] = str(product.pop('_id'))
        products.append(productModel(**product).model_dump(exclude_none=True))

    return products


@productRoutes.get("/upc/{upc}")
async def get_product_by_upc(
    upc: str,
    current_user: Annotated[UserModel, Depends(get_current_user('user'))]
):
    """Get a single product by UPC."""
    product = db.products.find_one({"upc": upc})

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    product['id'] = str(product.pop('_id'))

    return productModel(**product).model_dump(exclude_none=True)


@productRoutes.get("/{id}")
async def get_product(
    id: str,
    current_user: Annotated[UserModel, Depends(get_current_user('user'))]
):
    """Get a single product by ID."""
    product = db.products.find_one({"_id": ObjectId(id)})

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    product['id'] = str(product.pop('_id'))

    return productModel(**product).model_dump(exclude_none=True)


@productRoutes.put("/{id}")
async def update_product(
    id: str,
    product: productModel,
    current_user: Annotated[UserModel, Depends(get_current_user('user'))]
):
    """Update a product."""
    product_dict = product.model_dump(exclude_none=True)
    product_dict.pop('id', None)

    result = db.products.update_one(
        {"_id": ObjectId(id)},
        {"$set": product_dict}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
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
