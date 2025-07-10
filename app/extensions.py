from pymongo import MongoClient

# Create a MongoDB client. Update the URI if your MongoDB is hosted elsewhere.
client = MongoClient("mongodb://localhost:27017/webhook_data")

# Choose the database and collection
db = client.webhook_data
events_collection = db.events

