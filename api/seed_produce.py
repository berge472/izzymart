#!/usr/bin/env python3
"""
Seed Database with Common Produce Items
========================================
This script adds 100 common produce items to the database with images.
"""

import os
import sys
from pymongo import MongoClient
from bson import ObjectId
import gridfs

# Add parent directory to path to import utilities
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util.GoogleImageUtil import search_google_images
import requests
import hashlib

# MongoDB connection
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.getenv('MONGO_PORT', '27017'))
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'app')

# 100 most common produce items with realistic prices
PRODUCE_ITEMS = [
    # Fruits
    {"name": "Apples - Gala", "price": 1.99, "category": "Fruits"},
    {"name": "Apples - Honeycrisp", "price": 2.49, "category": "Fruits"},
    {"name": "Apples - Granny Smith", "price": 1.89, "category": "Fruits"},
    {"name": "Apples - Fuji", "price": 2.19, "category": "Fruits"},
    {"name": "Bananas", "price": 0.59, "category": "Fruits"},
    {"name": "Strawberries", "price": 3.99, "category": "Fruits"},
    {"name": "Blueberries", "price": 4.99, "category": "Fruits"},
    {"name": "Raspberries", "price": 4.99, "category": "Fruits"},
    {"name": "Blackberries", "price": 4.49, "category": "Fruits"},
    {"name": "Grapes - Green Seedless", "price": 2.99, "category": "Fruits"},
    {"name": "Grapes - Red Seedless", "price": 2.99, "category": "Fruits"},
    {"name": "Oranges - Navel", "price": 1.49, "category": "Fruits"},
    {"name": "Oranges - Valencia", "price": 1.39, "category": "Fruits"},
    {"name": "Lemons", "price": 0.79, "category": "Fruits"},
    {"name": "Limes", "price": 0.69, "category": "Fruits"},
    {"name": "Grapefruit - Ruby Red", "price": 1.29, "category": "Fruits"},
    {"name": "Watermelon", "price": 5.99, "category": "Fruits"},
    {"name": "Cantaloupe", "price": 3.99, "category": "Fruits"},
    {"name": "Honeydew Melon", "price": 3.49, "category": "Fruits"},
    {"name": "Pineapple", "price": 3.99, "category": "Fruits"},
    {"name": "Mango", "price": 1.99, "category": "Fruits"},
    {"name": "Papaya", "price": 2.99, "category": "Fruits"},
    {"name": "Kiwi", "price": 0.99, "category": "Fruits"},
    {"name": "Pears - Bartlett", "price": 1.79, "category": "Fruits"},
    {"name": "Pears - Anjou", "price": 1.89, "category": "Fruits"},
    {"name": "Peaches", "price": 2.49, "category": "Fruits"},
    {"name": "Nectarines", "price": 2.39, "category": "Fruits"},
    {"name": "Plums", "price": 2.29, "category": "Fruits"},
    {"name": "Cherries", "price": 5.99, "category": "Fruits"},
    {"name": "Pomegranate", "price": 2.99, "category": "Fruits"},

    # Vegetables
    {"name": "Avocados", "price": 1.99, "category": "Vegetables"},
    {"name": "Tomatoes - Roma", "price": 1.99, "category": "Vegetables"},
    {"name": "Tomatoes - Vine Ripened", "price": 2.49, "category": "Vegetables"},
    {"name": "Tomatoes - Cherry", "price": 3.49, "category": "Vegetables"},
    {"name": "Tomatoes - Grape", "price": 3.29, "category": "Vegetables"},
    {"name": "Lettuce - Romaine", "price": 2.49, "category": "Vegetables"},
    {"name": "Lettuce - Iceberg", "price": 1.99, "category": "Vegetables"},
    {"name": "Lettuce - Butter", "price": 2.99, "category": "Vegetables"},
    {"name": "Spinach - Fresh", "price": 2.99, "category": "Vegetables"},
    {"name": "Kale", "price": 2.49, "category": "Vegetables"},
    {"name": "Arugula", "price": 3.49, "category": "Vegetables"},
    {"name": "Mixed Salad Greens", "price": 3.99, "category": "Vegetables"},
    {"name": "Cucumbers", "price": 1.29, "category": "Vegetables"},
    {"name": "Bell Peppers - Red", "price": 1.99, "category": "Vegetables"},
    {"name": "Bell Peppers - Green", "price": 1.49, "category": "Vegetables"},
    {"name": "Bell Peppers - Yellow", "price": 1.89, "category": "Vegetables"},
    {"name": "Bell Peppers - Orange", "price": 1.89, "category": "Vegetables"},
    {"name": "Jalapeño Peppers", "price": 0.99, "category": "Vegetables"},
    {"name": "Serrano Peppers", "price": 1.29, "category": "Vegetables"},
    {"name": "Onions - Yellow", "price": 1.49, "category": "Vegetables"},
    {"name": "Onions - Red", "price": 1.69, "category": "Vegetables"},
    {"name": "Onions - White", "price": 1.59, "category": "Vegetables"},
    {"name": "Green Onions", "price": 1.29, "category": "Vegetables"},
    {"name": "Garlic", "price": 0.99, "category": "Vegetables"},
    {"name": "Ginger Root", "price": 2.99, "category": "Vegetables"},
    {"name": "Carrots", "price": 1.49, "category": "Vegetables"},
    {"name": "Celery", "price": 2.49, "category": "Vegetables"},
    {"name": "Broccoli", "price": 2.99, "category": "Vegetables"},
    {"name": "Cauliflower", "price": 3.49, "category": "Vegetables"},
    {"name": "Cabbage - Green", "price": 1.99, "category": "Vegetables"},
    {"name": "Cabbage - Red", "price": 2.29, "category": "Vegetables"},
    {"name": "Brussels Sprouts", "price": 3.99, "category": "Vegetables"},
    {"name": "Asparagus", "price": 4.99, "category": "Vegetables"},
    {"name": "Green Beans", "price": 2.99, "category": "Vegetables"},
    {"name": "Zucchini", "price": 1.99, "category": "Vegetables"},
    {"name": "Yellow Squash", "price": 1.99, "category": "Vegetables"},
    {"name": "Eggplant", "price": 2.49, "category": "Vegetables"},
    {"name": "Mushrooms - White Button", "price": 3.49, "category": "Vegetables"},
    {"name": "Mushrooms - Portobello", "price": 4.99, "category": "Vegetables"},
    {"name": "Mushrooms - Shiitake", "price": 5.99, "category": "Vegetables"},
    {"name": "Corn on the Cob", "price": 0.99, "category": "Vegetables"},
    {"name": "Sweet Potatoes", "price": 1.79, "category": "Vegetables"},
    {"name": "Potatoes - Russet", "price": 1.29, "category": "Vegetables"},
    {"name": "Potatoes - Red", "price": 1.49, "category": "Vegetables"},
    {"name": "Potatoes - Yukon Gold", "price": 1.69, "category": "Vegetables"},
    {"name": "Beets", "price": 2.49, "category": "Vegetables"},
    {"name": "Radishes", "price": 1.99, "category": "Vegetables"},
    {"name": "Turnips", "price": 1.79, "category": "Vegetables"},
    {"name": "Parsnips", "price": 2.29, "category": "Vegetables"},

    # Herbs
    {"name": "Basil - Fresh", "price": 2.99, "category": "Herbs"},
    {"name": "Cilantro - Fresh", "price": 1.49, "category": "Herbs"},
    {"name": "Parsley - Fresh", "price": 1.49, "category": "Herbs"},
    {"name": "Mint - Fresh", "price": 2.49, "category": "Herbs"},
    {"name": "Rosemary - Fresh", "price": 2.99, "category": "Herbs"},
    {"name": "Thyme - Fresh", "price": 2.99, "category": "Herbs"},
    {"name": "Oregano - Fresh", "price": 2.99, "category": "Herbs"},
    {"name": "Dill - Fresh", "price": 2.49, "category": "Herbs"},

    # Specialty Items
    {"name": "Artichokes", "price": 3.99, "category": "Vegetables"},
    {"name": "Leeks", "price": 2.99, "category": "Vegetables"},
    {"name": "Bok Choy", "price": 2.49, "category": "Vegetables"},
    {"name": "Napa Cabbage", "price": 3.49, "category": "Vegetables"},
    {"name": "Radicchio", "price": 3.99, "category": "Vegetables"},
    {"name": "Endive", "price": 3.49, "category": "Vegetables"},
    {"name": "Fennel", "price": 2.99, "category": "Vegetables"},
    {"name": "Jicama", "price": 2.49, "category": "Vegetables"},
    {"name": "Kohlrabi", "price": 2.29, "category": "Vegetables"},
    {"name": "Rutabaga", "price": 1.99, "category": "Vegetables"},
    {"name": "Shallots", "price": 3.49, "category": "Vegetables"},
    {"name": "Snow Peas", "price": 4.49, "category": "Vegetables"},
    {"name": "Sugar Snap Peas", "price": 4.49, "category": "Vegetables"},
    {"name": "Okra", "price": 3.49, "category": "Vegetables"},
    {"name": "Tomatillos", "price": 2.99, "category": "Vegetables"},
    {"name": "Horseradish Root", "price": 4.99, "category": "Vegetables"},
    {"name": "Water Chestnuts - Fresh", "price": 3.99, "category": "Vegetables"},
    {"name": "Bean Sprouts", "price": 2.49, "category": "Vegetables"},
    {"name": "Alfalfa Sprouts", "price": 2.99, "category": "Vegetables"},
    {"name": "Butternut Squash", "price": 2.99, "category": "Vegetables"},
    {"name": "Acorn Squash", "price": 2.49, "category": "Vegetables"},
    {"name": "Spaghetti Squash", "price": 3.49, "category": "Vegetables"},
    {"name": "Pumpkin", "price": 4.99, "category": "Vegetables"},
]

def download_and_store_image(image_url, filename, db, fs):
    """
    Download an image from a URL and store it in GridFS.

    Args:
        image_url: URL of the image to download
        filename: Name to give the file
        db: MongoDB database instance
        fs: GridFS instance

    Returns:
        File ID string if successful, None otherwise
    """
    try:
        print(f"    📥 Downloading image from: {image_url[:60]}...")
        response = requests.get(image_url, timeout=10)

        if response.status_code != 200:
            print(f"    ❌ Failed to download image: HTTP {response.status_code}")
            return None

        image_data = response.content

        # Calculate MD5 hash for deduplication
        md5_hash = hashlib.md5(image_data).hexdigest()

        # Check if file already exists
        existing = db.files.find_one({"md5": md5_hash})

        if existing is not None:
            print(f"    ♻️  Image already exists (using cached)")
            return str(existing['_id'])

        # Store in GridFS
        gridfs_file_id = fs.put(
            image_data,
            filename=filename,
            owner='system',
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

        print(f"    ✅ Image stored successfully")
        return file_id

    except Exception as e:
        print(f"    ❌ Error downloading image: {str(e)}")
        return None

def seed_produce():
    """Seed the database with produce items."""
    print("=" * 60)
    print("IzzyMart - Seed Produce Items")
    print("=" * 60)
    print()

    # Connect to database
    print(f"📡 Connecting to MongoDB at {MONGO_HOST}:{MONGO_PORT}...")
    client = MongoClient(f'mongodb://{MONGO_HOST}:{MONGO_PORT}/')
    db = client[MONGO_DB_NAME]
    fs = gridfs.GridFS(db)
    print("✅ Connected to database")
    print()

    # Check for existing produce items
    existing_count = db.products.count_documents({"product_type": "food", "category": {"$in": ["Fruits", "Vegetables", "Herbs"]}})
    print(f"📊 Found {existing_count} existing produce items")

    if existing_count > 0:
        response = input("Do you want to delete existing produce items first? (y/n): ")
        if response.lower() == 'y':
            result = db.products.delete_many({"product_type": "food", "category": {"$in": ["Fruits", "Vegetables", "Herbs"]}})
            print(f"🗑️  Deleted {result.deleted_count} existing produce items")

    print()
    print(f"🌱 Adding {len(PRODUCE_ITEMS)} produce items with images...")
    print("⚠️  Note: Image fetching may take a few minutes...")
    print()

    # Insert produce items
    inserted_count = 0
    images_added = 0

    for item in PRODUCE_ITEMS:
        # Generate a PLU code (4-digit code for produce)
        plu = f"4{1000 + inserted_count}"

        print(f"[{inserted_count + 1}/{len(PRODUCE_ITEMS)}] Processing: {item['name']}")

        # Try to fetch image from Google Images
        image_ids = []
        # try:
        #     print(f"  🔍 Searching for image...")
        #     image_urls = search_google_images(item["name"], max_results=1)

        #     if image_urls and len(image_urls) > 0:
        #         image_id = download_and_store_image(
        #             image_urls[0],
        #             f"{item['name']}.jpg",
        #             db,
        #             fs
        #         )
        #         if image_id:
        #             image_ids.append(image_id)
        #             images_added += 1
        #     else:
        #         print(f"  ⚠️  No images found for {item['name']}")
        # except Exception as e:
        #     print(f"  ⚠️  Error fetching image: {str(e)}")

        product = {
            "product_type": "food",
            "upc": plu,  # Use PLU as UPC for produce
            "name": item["name"],
            "brand": "Fresh Produce",
            "price": item["price"],
            "category": item["category"],
            "images": image_ids,
            "image_source": "Google Images" if image_ids else None,
            "nutrition": {
                "serving_size": "1 item",
                "calories": 0,
                "total_fat": 0,
                "saturated_fat": 0,
                "trans_fat": 0,
                "cholesterol": 0,
                "sodium": 0,
                "total_carbohydrate": 0,
                "dietary_fiber": 0,
                "total_sugars": 0,
                "protein": 0
            },
            "ingredients": "",
            "allergens": []
        }

        db.products.insert_one(product)
        inserted_count += 1
        print()

    print()
    print("=" * 60)
    print(f"✅ Successfully added {inserted_count} produce items!")
    print(f"📷 Images added: {images_added}/{inserted_count}")
    print("=" * 60)
    print()
    print("Items are now searchable by:")
    print("  - PLU codes (4-digit codes: 41000-41099)")
    print("  - Product names (e.g., 'Apples', 'Bananas')")
    print("  - Categories (Fruits, Vegetables, Herbs)")
    print()
    print("💡 Tip: View these items on the product lookup page!")
    print()

if __name__ == "__main__":
    try:
        seed_produce()
    except KeyboardInterrupt:
        print()
        print("⚠️  Operation cancelled by user")
    except Exception as e:
        print()
        print(f"❌ Error: {e}")
