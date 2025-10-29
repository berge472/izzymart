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
from datetime import datetime

# Add parent directory to path to import utilities
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import requests
import hashlib

# MongoDB connection
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.getenv('MONGO_PORT', '27017'))
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'app')

# 100 most common produce items with realistic prices and image URLs
PRODUCE_ITEMS = [
    # Fruits
    {"name": "Apples - Gala", "price": 1.99, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=400"},
    {"name": "Apples - Honeycrisp", "price": 2.49, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1619546813926-a78fa6372cd2?w=400"},
    {"name": "Apples - Granny Smith", "price": 1.89, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1590005354167-6da97870c757?w=400"},
    {"name": "Apples - Fuji", "price": 2.19, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1570913149827-d2ac84ab3f9a?w=400"},
    {"name": "Bananas", "price": 0.59, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1603833665858-e61d17a86224?w=400"},
    {"name": "Strawberries", "price": 3.99, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=400"},
    {"name": "Blueberries", "price": 4.99, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1498557850523-fd3d118b962e?w=400"},
    {"name": "Raspberries", "price": 4.99, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1577069861033-55d04cec4ef5?w=400"},
    {"name": "Blackberries", "price": 4.49, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1588438784171-f8d1f573c443?w=400"},
    {"name": "Grapes - Green Seedless", "price": 2.99, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1599819177668-e48f1c2e3b8d?w=400"},
    {"name": "Grapes - Red Seedless", "price": 2.99, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1596363505729-4190a9506133?w=400"},
    {"name": "Oranges - Navel", "price": 1.49, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1582979512210-99b6a53386f9?w=400"},
    {"name": "Oranges - Valencia", "price": 1.39, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1611080626919-7cf5a9dbab5b?w=400"},
    {"name": "Lemons", "price": 0.79, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1590502593747-42a996133562?w=400"},
    {"name": "Limes", "price": 0.69, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11?w=400"},
    {"name": "Grapefruit - Ruby Red", "price": 1.29, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400"},
    {"name": "Watermelon", "price": 5.99, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1587049352846-4a222e784169?w=400"},
    {"name": "Cantaloupe", "price": 3.99, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1621583832937-d0c7b9f1d9d2?w=400"},
    {"name": "Honeydew Melon", "price": 3.49, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1621583832937-d0c7b9f1d9d2?w=400"},
    {"name": "Pineapple", "price": 3.99, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1550258987-190a2d41a8ba?w=400"},
    {"name": "Mango", "price": 1.99, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=400"},
    {"name": "Papaya", "price": 2.99, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1617112848923-cc2234396a8d?w=400"},
    {"name": "Kiwi", "price": 0.99, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1585059895524-72359e06133a?w=400"},
    {"name": "Pears - Bartlett", "price": 1.79, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1568649929187-cbd0c0277e59?w=400"},
    {"name": "Pears - Anjou", "price": 1.89, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1574856344991-aaa31b6f4ce3?w=400"},
    {"name": "Peaches", "price": 2.49, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1629828874514-d11e85c8a999?w=400"},
    {"name": "Nectarines", "price": 2.39, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1629828874514-d11e85c8a999?w=400"},
    {"name": "Plums", "price": 2.29, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1600475373749-751daa72eff5?w=400"},
    {"name": "Cherries", "price": 5.99, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1528821128474-27f963b062bf?w=400"},
    {"name": "Pomegranate", "price": 2.99, "category": "Fruits", "image_url": "https://images.unsplash.com/photo-1590845947670-c009801ffa74?w=400"},

    # Vegetables
    {"name": "Avocados", "price": 1.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=400"},
    {"name": "Tomatoes - Roma", "price": 1.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1592924728850-586c4ff74f5e?w=400"},
    {"name": "Tomatoes - Vine Ripened", "price": 2.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1546094096-0df4bcaaa337?w=400"},
    {"name": "Tomatoes - Cherry", "price": 3.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1561136594-7f68413baa99?w=400"},
    {"name": "Tomatoes - Grape", "price": 3.29, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=400"},
    {"name": "Lettuce - Romaine", "price": 2.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1622205313162-be1d19fdd7bb?w=400"},
    {"name": "Lettuce - Iceberg", "price": 1.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1550440537-d0b7e32d5e95?w=400"},
    {"name": "Lettuce - Butter", "price": 2.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1591024968525-bdb079033c14?w=400"},
    {"name": "Spinach - Fresh", "price": 2.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400"},
    {"name": "Kale", "price": 2.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1560803268-3fa93f4e26b7?w=400"},
    {"name": "Arugula", "price": 3.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1629194291293-8c6c125a0245?w=400"},
    {"name": "Mixed Salad Greens", "price": 3.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1505576399279-565b52d4ac71?w=400"},
    {"name": "Cucumbers", "price": 1.29, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1604977042946-a3aef0562ec5?w=400"},
    {"name": "Bell Peppers - Red", "price": 1.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=400"},
    {"name": "Bell Peppers - Green", "price": 1.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1574621925530-05d5e06dd5e9?w=400"},
    {"name": "Bell Peppers - Yellow", "price": 1.89, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=400"},
    {"name": "Bell Peppers - Orange", "price": 1.89, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1588438784171-f8d1f573c443?w=400"},
    {"name": "Jalapeño Peppers", "price": 0.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1599940824399-b87987ceb72a?w=400"},
    {"name": "Serrano Peppers", "price": 1.29, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1609142506270-8f366c6c8dd9?w=400"},
    {"name": "Onions - Yellow", "price": 1.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1618512496248-a07fe83c3913?w=400"},
    {"name": "Onions - Red", "price": 1.69, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1580201092675-a0a6a6cafbb1?w=400"},
    {"name": "Onions - White", "price": 1.59, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=400"},
    {"name": "Green Onions", "price": 1.29, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1609702159600-604e30519d9c?w=400"},
    {"name": "Garlic", "price": 0.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1587365225332-f6f28e8a77f3?w=400"},
    {"name": "Ginger Root", "price": 2.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1582693479452-dc72e8d5ab61?w=400"},
    {"name": "Carrots", "price": 1.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=400"},
    {"name": "Celery", "price": 2.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1604687330005-c32ad4c3e8d0?w=400"},
    {"name": "Broccoli", "price": 2.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1459411621453-7b03977a4f08?w=400"},
    {"name": "Cauliflower", "price": 3.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1568584711271-79a3d1bfb33b?w=400"},
    {"name": "Cabbage - Green", "price": 1.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1596870230751-ebdfce98ec42?w=400"},
    {"name": "Cabbage - Red", "price": 2.29, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1615485500834-bc10199bc160?w=400"},
    {"name": "Brussels Sprouts", "price": 3.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1616665806342-f4714f13aa8a?w=400"},
    {"name": "Asparagus", "price": 4.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1597599974571-3491c4f97ac0?w=400"},
    {"name": "Green Beans", "price": 2.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1553395572-5b683d1c8f1d?w=400"},
    {"name": "Zucchini", "price": 1.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1589927986089-35812388d1f4?w=400"},
    {"name": "Yellow Squash", "price": 1.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1600617572118-67ce29667d56?w=400"},
    {"name": "Eggplant", "price": 2.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1597305877032-0668b3c22deb?w=400"},
    {"name": "Mushrooms - White Button", "price": 3.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1621544402532-5fc59f68e709?w=400"},
    {"name": "Mushrooms - Portobello", "price": 4.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1611961756165-e6cd7164012b?w=400"},
    {"name": "Mushrooms - Shiitake", "price": 5.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1601309269625-e8e1a8c71ced?w=400"},
    {"name": "Corn on the Cob", "price": 0.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1603893733881-b60eb8c1dd02?w=400"},
    {"name": "Sweet Potatoes", "price": 1.79, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1604152135912-04a022e23696?w=400"},
    {"name": "Potatoes - Russet", "price": 1.29, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400"},
    {"name": "Potatoes - Red", "price": 1.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1552661397-0ff55d1b4954?w=400"},
    {"name": "Potatoes - Yukon Gold", "price": 1.69, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1587574293340-e0011c4e8ecf?w=400"},
    {"name": "Beets", "price": 2.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1563769623928-b3f8b5ab1c1a?w=400"},
    {"name": "Radishes", "price": 1.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1585766497410-e60e879e06e0?w=400"},
    {"name": "Turnips", "price": 1.79, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1613743983303-b3e89f8a9b2d?w=400"},
    {"name": "Parsnips", "price": 2.29, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1599217036895-dc3e5b4a3faa?w=400"},

    # Herbs
    {"name": "Basil - Fresh", "price": 2.99, "category": "Herbs", "image_url": "https://images.unsplash.com/photo-1618164435735-413e3b9c3a16?w=400"},
    {"name": "Cilantro - Fresh", "price": 1.49, "category": "Herbs", "image_url": "https://images.unsplash.com/photo-1595803610928-aab2533ddc5e?w=400"},
    {"name": "Parsley - Fresh", "price": 1.49, "category": "Herbs", "image_url": "https://images.unsplash.com/photo-1551803091-e20673f15770?w=400"},
    {"name": "Mint - Fresh", "price": 2.49, "category": "Herbs", "image_url": "https://images.unsplash.com/photo-1628556270448-4d4e4148e1b1?w=400"},
    {"name": "Rosemary - Fresh", "price": 2.99, "category": "Herbs", "image_url": "https://images.unsplash.com/photo-1595903054551-2c0afc497b1e?w=400"},
    {"name": "Thyme - Fresh", "price": 2.99, "category": "Herbs", "image_url": "https://images.unsplash.com/photo-1586184898564-96e34e964f7f?w=400"},
    {"name": "Oregano - Fresh", "price": 2.99, "category": "Herbs", "image_url": "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=400"},
    {"name": "Dill - Fresh", "price": 2.49, "category": "Herbs", "image_url": "https://images.unsplash.com/photo-1628556270448-4d4e4148e1b1?w=400"},

    # Specialty Items
    {"name": "Artichokes", "price": 3.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1572018195667-62a6c5c23e48?w=400"},
    {"name": "Leeks", "price": 2.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1610105173959-73a93b4e5e19?w=400"},
    {"name": "Bok Choy", "price": 2.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1590777516308-e7b3c2c70d2f?w=400"},
    {"name": "Napa Cabbage", "price": 3.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1597733375162-4a0fa2b85e69?w=400"},
    {"name": "Radicchio", "price": 3.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1595932477371-f2c0ca6bb4e1?w=400"},
    {"name": "Endive", "price": 3.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1603048719539-9ecb4aa395e3?w=400"},
    {"name": "Fennel", "price": 2.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1597332570950-3d5a3e34c93d?w=400"},
    {"name": "Jicama", "price": 2.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=400"},
    {"name": "Kohlrabi", "price": 2.29, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1590777516308-e7b3c2c70d2f?w=400"},
    {"name": "Rutabaga", "price": 1.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1595903054551-2c0afc497b1e?w=400"},
    {"name": "Shallots", "price": 3.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1612693414923-de0e2e5c2954?w=400"},
    {"name": "Snow Peas", "price": 4.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=400"},
    {"name": "Sugar Snap Peas", "price": 4.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1601413965169-a92c0b7c7e93?w=400"},
    {"name": "Okra", "price": 3.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1597995333227-45921db0e2c7?w=400"},
    {"name": "Tomatillos", "price": 2.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1629194291293-8c6c125a0245?w=400"},
    {"name": "Horseradish Root", "price": 4.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1582693479452-dc72e8d5ab61?w=400"},
    {"name": "Water Chestnuts - Fresh", "price": 3.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1590777516308-e7b3c2c70d2f?w=400"},
    {"name": "Bean Sprouts", "price": 2.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1560803268-3fa93f4e26b7?w=400"},
    {"name": "Alfalfa Sprouts", "price": 2.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1629194291293-8c6c125a0245?w=400"},
    {"name": "Butternut Squash", "price": 2.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1570268999554-cfad8b260df3?w=400"},
    {"name": "Acorn Squash", "price": 2.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1605329079945-7e5b4b14fe04?w=400"},
    {"name": "Spaghetti Squash", "price": 3.49, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1600617572118-67ce29667d56?w=400"},
    {"name": "Pumpkin", "price": 4.99, "category": "Vegetables", "image_url": "https://images.unsplash.com/photo-1569976710208-b52636b52c09?w=400"},
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

        # Download image from URL if available
        image_ids = []
        if "image_url" in item and item["image_url"]:
            try:
                image_id = download_and_store_image(
                    item['image_url'],
                    f"{item['name']}.jpg",
                    db,
                    fs
                )
                if image_id:
                    image_ids.append(image_id)
                    images_added += 1
            except Exception as e:
                print(f"  ⚠️  Error downloading image: {str(e)}")

        product = {
            "product_type": "food",
            "upc": plu,  # Use PLU as UPC for produce
            "name": item["name"],
            "brand": "Fresh Produce",
            "price": item["price"],
            "category": item["category"],
            "images": image_ids,
            "image_source": "Unsplash" if image_ids else None,
            "last_modified": datetime.utcnow(),
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
