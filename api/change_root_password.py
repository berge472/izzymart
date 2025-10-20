#!/usr/bin/env python3
"""
Change Root Password Script
============================
This script allows you to change the root admin password from within the API container.

Usage:
    python change_root_password.py

Or make it executable:
    chmod +x change_root_password.py
    ./change_root_password.py
"""

import sys
import os
from getpass import getpass
from pymongo import MongoClient
from passlib.context import CryptContext
from bson import ObjectId

# Setup password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB connection settings from environment
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = int(os.getenv('MONGO_PORT', '27017'))
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'izzymart')


def connect_to_db():
    """Connect to MongoDB database."""
    try:
        client = MongoClient(f'mongodb://{MONGO_HOST}:{MONGO_PORT}/')
        db = client[MONGO_DB_NAME]
        return db
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        sys.exit(1)


def get_root_user(db):
    """Get the root user from the database."""
    root_user = db.users.find_one({"username": "root"})
    if not root_user:
        print("❌ Root user not found in database!")
        sys.exit(1)
    return root_user


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # Bcrypt has a 72-byte limit, truncate the password bytes if necessary
    passwd_bytes = password.encode('utf-8')
    if len(passwd_bytes) > 72:
        passwd_bytes = passwd_bytes[:72]
        print("⚠️  Warning: Password truncated to 72 bytes for bcrypt")

    passwd_to_hash = passwd_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(passwd_to_hash)


def update_password(db, new_password: str):
    """Update the root user's password."""
    try:
        hashed_password = hash_password(new_password)

        print(f"🔍 Debug: Password length: {len(new_password)} characters")
        print(f"🔍 Debug: Hash starts with: {hashed_password[:20]}...")

        result = db.users.update_one(
            {"username": "root"},
            {"$set": {"password": hashed_password}}
        )

        if result.modified_count > 0:
            # Verify the password was stored correctly
            stored_user = db.users.find_one({"username": "root"})
            can_verify = pwd_context.verify(new_password, stored_user['password'])

            print("✅ Root password updated successfully!")
            print(f"🔍 Debug: Immediate verification test: {can_verify}")

            if not can_verify:
                print("⚠️  WARNING: Password was stored but verification failed!")
                print("This might indicate a problem with password encoding.")

            return True
        else:
            print("❌ Failed to update password")
            return False
    except Exception as e:
        print(f"❌ Error updating password: {e}")
        return False


def main():
    print("=" * 60)
    print("IzzyMart - Change Root Password")
    print("=" * 60)
    print()

    # Connect to database
    print(f"📡 Connecting to MongoDB at {MONGO_HOST}:{MONGO_PORT}...")
    db = connect_to_db()
    print("✅ Connected to database")
    print()

    # Verify root user exists
    root_user = get_root_user(db)
    print(f"👤 Found root user (ID: {root_user['_id']})")
    print()

    # Get new password
    print("Please enter the new password for the root user.")
    print("Note: Password will not be visible as you type.")
    print()

    while True:
        new_password = getpass("New password: ")

        if len(new_password) < 8:
            print("⚠️  Password must be at least 8 characters long. Please try again.")
            print()
            continue

        confirm_password = getpass("Confirm password: ")

        if new_password != confirm_password:
            print("❌ Passwords do not match. Please try again.")
            print()
            continue

        break

    print()
    print("🔄 Updating password...")

    # Update the password
    if update_password(db, new_password):
        print()
        print("=" * 60)
        print("🎉 Password changed successfully!")
        print("=" * 60)
        print()
        print("You can now log in to the admin panel with your new password.")
        print("Username: root")
        print("Password: (the password you just set)")
        print()
    else:
        print()
        print("=" * 60)
        print("❌ Failed to change password")
        print("=" * 60)
        print()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print()
        print("⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
