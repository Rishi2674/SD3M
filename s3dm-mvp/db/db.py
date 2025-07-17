# app/db.py
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv # Used to load environment variables from .env
import os
from typing import Optional

# Load environment variables from the central .env file at the project root.
# This ensures that MONGO_URI is available.
load_dotenv() 

# Retrieve MONGO_URI from environment variables.
# This variable should be set in your .env file in the s3dm-mvp/ directory.
MONGO_URI = os.getenv("MONGO_URI")

# Basic check to ensure the MONGO_URI is actually loaded.
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable not set. Please ensure it's in your .env file at the project root (s3dm-mvp/).")

# Global MongoClient instance.
# This allows the connection to be reused across different parts of your application
# without creating a new connection for every database operation.
_mongo_client: Optional[MongoClient] = None

def get_mongo_db_connection():
    """
    Returns the MongoDB database instance.
    Initializes the client if it hasn't been already.
    Performs a ping to check connection health.
    """
    global _mongo_client
    if _mongo_client is None:
        try:
            # Attempt to create a new MongoClient instance
            _mongo_client = MongoClient(MONGO_URI)
            
            # The 'ismaster' or 'ping' command is a lightweight way to check if
            # the MongoDB server is reachable and authenticable.
            _mongo_client.admin.command('ping')
            print("DB: MongoDB connection successful!")
        except ConnectionFailure as e:
            # If connection fails, print an error and re-raise the exception
            # so the calling part of the application can handle it.
            print(f"DB: MongoDB connection failed: {e}")
            raise ConnectionFailure(f"Database connection error: {e}")
    
    # Extract the database name from the MONGO_URI.
    # This handles both standard URIs (mongodb://host:port/dbname)
    # and SRV URIs (mongodb+srv://user:pass@cluster.mongodb.net/dbname?...)
    # If no database name is explicitly provided in the URI path, it defaults to "s3dm_db".
    db_name_from_uri = MONGO_URI.split('/')[-1].split('?')[0] if '/' in MONGO_URI else ""
    db_name = db_name_from_uri if db_name_from_uri and not db_name_from_uri.startswith('?') else "s3dm_db"
    
    # Return the specific database instance from the client.
    return _mongo_client[db_name]

def close_mongo_db_connection():
    """
    Closes the global MongoDB connection.
    This should be called on application shutdown to release resources.
    """
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None # Reset client to None after closing
        print("DB: MongoDB connection closed.")