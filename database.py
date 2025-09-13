from pymongo import MongoClient

# Simple MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["assessment_db"]
employees_collection = db["employees"]

employees_collection.create_index("employee_id", unique=True)

def get_database():
    return employees_collection