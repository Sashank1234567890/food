import os
from pymongo import MongoClient

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "recipesdb")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "config.recipes")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
recipes_collection = db[MONGO_COLLECTION_NAME]
users_collection = db["users"]
likes_collection = db["likes"]

# Sample recipes
sample_recipes = [
    {
        "name_of_dish": "Chicken Salad",
        "ingredients": ["chicken", "lettuce", "tomato"],
        "instructions_to_cook": ["Mix all ingredients.", "Serve chilled."],
        "nutrients_per_gram": {
            "calories": 0.8,
            "protein_g": 0.25,
            "fat_g": 0.03,
            "carbs_g": 0.1
        },
        "is_veg": False,
        "flavor": "sour"
    },
    {
        "name_of_dish": "Veggie Stir Fry",
        "ingredients": ["broccoli", "carrot", "soy sauce"],
        "instructions_to_cook": ["Stir fry vegetables.", "Add sauce."],
        "nutrients_per_gram": {
            "calories": 0.5,
            "protein_g": 0.15,
            "fat_g": 0.02,
            "carbs_g": 0.12
        },
        "is_veg": True,
        "flavor": "spicy"
    },
    {
        "name_of_dish": "Protein Shake",
        "ingredients": ["banana", "protein powder", "milk"],
        "instructions_to_cook": ["Blend all ingredients.", "Drink immediately."],
        "nutrients_per_gram": {
            "calories": 1.0,
            "protein_g": 0.3,
            "fat_g": 0.04,
            "carbs_g": 0.2
        },
        "is_veg": True,
        "flavor": "sweet"
    }
]

# Insert if not exists
for recipe in sample_recipes:
    existing = recipes_collection.find_one({"name_of_dish": recipe["name_of_dish"]})
    if existing:
        recipes_collection.update_one({"name_of_dish": recipe["name_of_dish"]}, {"$set": {"is_veg": recipe["is_veg"], "flavor": recipe["flavor"]}})
    else:
        recipes_collection.insert_one(recipe)

print("Sample recipes inserted.")

# Sample users
sample_users = [
    {"user_id": "user1", "password": "pass1"},
    {"user_id": "user2", "password": "pass2"}
]

for user in sample_users:
    if not users_collection.find_one({"user_id": user["user_id"]}):
        users_collection.insert_one(user)

print("Sample users inserted.")