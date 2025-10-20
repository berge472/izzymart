#!/usr/bin/env python3
"""
Seed Database with Common Produce Items
========================================
This script adds 100 common produce items to the database.
"""

import os
from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.getenv('MONGO_PORT', '27017'))
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'izzymart')

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
    print(f"🌱 Adding {len(PRODUCE_ITEMS)} produce items...")

    # Insert produce items
    inserted_count = 0
    for item in PRODUCE_ITEMS:
        # Generate a PLU code (4-digit code for produce)
        plu = f"4{1000 + inserted_count}"

        product = {
            "product_type": "food",
            "upc": plu,  # Use PLU as UPC for produce
            "name": item["name"],
            "brand": "Fresh Produce",
            "price": item["price"],
            "category": item["category"],
            "images": [],
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

        if inserted_count % 10 == 0:
            print(f"  Added {inserted_count} items...")

    print()
    print("=" * 60)
    print(f"✅ Successfully added {inserted_count} produce items!")
    print("=" * 60)
    print()
    print("Items are now searchable by:")
    print("  - PLU codes (4-digit codes: 41000-41099)")
    print("  - Product names (e.g., 'Apples', 'Bananas')")
    print("  - Categories (Fruits, Vegetables, Herbs)")
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
