from pymongo import MongoClient
import os
from gridfs import GridFS

#get mongourl from environment variable
mongo_host = os.environ.get('MONGO_HOST', 'localhost')
mongo_db = os.environ.get('MONGO_DB_NAME', 'app')

print(f'Connecting to mongodb://{mongo_host}:27017')

client = MongoClient(f'mongodb://{mongo_host}:27017')

db = client[mongo_db]
fs = GridFS(db)

