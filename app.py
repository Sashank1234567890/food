import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

app = Flask(__name__)
CORS(app)

# MongoDB connection configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "recipesdb")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "config.recipes")

print(f"Using MongoDB URI: {MONGO_URI}")
print(f"Using MongoDB database: {MONGO_DB}")
print(f"Using MongoDB collection: {MONGO_COLLECTION_NAME}")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

recipes_collection = db[MONGO_COLLECTION_NAME]
users_collection = db["users"]
likes_collection = db["likes"]


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user_id = data.get("user_id")
    password = data.get("password")

    user = users_collection.find_one({"user_id": user_id, "password": password})
    if user:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    user_id = data.get("user_id")
    password = data.get("password")

    if not user_id or not password:
        return jsonify({"success": False, "message": "User ID and password required"})

    existing_user = users_collection.find_one({"user_id": user_id})
    if existing_user:
        return jsonify({"success": False, "message": "User ID already exists!"})

    users_collection.insert_one({"user_id": user_id, "password": password})
    return jsonify({"success": True})


@app.route("/get_recipes", methods=["POST"])
def get_recipes():
    data = request.json

    # ✅ Normalize user input
    user_ingredients = [i.lower().strip() for i in data.get("ingredients", [])]
    diet_filters = data.get("diet", [])
    food_type = data.get("type", "")  # "veg" or "non-veg"
    flavor = data.get("flavor", "")  # "sweet", "spicy", etc.

    print(f"GET /get_recipes payload ingredients={user_ingredients} diet={diet_filters} type={food_type} flavor={flavor}")

    all_recipes = list(recipes_collection.find())

    results = []

    for r in all_recipes:

        # ✅ Normalize recipe metadata
        recipe_is_veg = r.get("is_veg", r.get("veg", True))
        recipe_flavor = str(r.get("flavor", "")).lower()

        # ✅ Filter by food type
        if food_type == "veg" and not recipe_is_veg:
            continue
        if food_type == "non-veg" and recipe_is_veg:
            continue

        # ✅ Filter by flavor
        if flavor and recipe_flavor != flavor.lower():
            continue

        # ✅ Normalize recipe ingredients
        recipe_ingredients = [i.lower().strip() for i in r.get("ingredients", [])]

        if len(recipe_ingredients) == 0:
            continue

        # 🔥 SMART MATCHING (partial + flexible)
        match_count = 0

        for user_ing in user_ingredients:
            for rec_ing in recipe_ingredients:
                if user_ing in rec_ing or rec_ing in user_ing:
                    match_count += 1
                    break

        match_percent = (match_count / len(user_ingredients)) * 100 if user_ingredients else 0

        # ❗ Allow even low matches (important)
        if match_percent <= 0:
            continue

        # ✅ Nutrients
        nutrients = r.get("nutrients_per_gram", {})

        calories = nutrients.get("calories", 0)
        protein = nutrients.get("protein_g", 0)
        fat = nutrients.get("fat_g", 0)
        carbs = nutrients.get("carbs_g", 0)

        # 🔥 Diet filters
        ok = True

        if "weight_loss" in diet_filters and calories >= 1.2:
            ok = False
        if "high_protein" in diet_filters and protein <= 0.18:
            ok = False
        if "low_fat" in diet_filters and fat >= 0.05:
            ok = False
        # Relax diabetes filter slightly so high-carb keywords like rice can still return
        if "diabetes" in diet_filters and carbs >= 0.20:
            ok = False

        if ok:
            results.append({
                "name": r.get("name_of_dish", "Unknown"),
                "ingredients": recipe_ingredients,
                "steps": r.get("instructions_to_cook", []),
                "match": round(match_percent, 2),
                "match_percent": round(match_percent, 2),
                "nutrients": {
                    "calories": round(calories, 2),
                    "protein_g": round(protein, 2),
                    "fat_g": round(fat, 2),
                    "carbs_g": round(carbs, 2)
                }
            })

    # 🔥 Sort by best match
    results.sort(key=lambda x: x["match"], reverse=True)

    if len(results) == 0 and diet_filters:
        fallback_results = []

        for r in all_recipes:
            # ✅ Normalize recipe metadata
            recipe_is_veg = r.get("is_veg", r.get("veg", True))
            recipe_flavor = str(r.get("flavor", "")).lower()

            # ✅ Filter by food type
            if food_type == "veg" and not recipe_is_veg:
                continue
            if food_type == "non-veg" and recipe_is_veg:
                continue

            # ✅ Filter by flavor
            if flavor and recipe_flavor != flavor.lower():
                continue

            recipe_ingredients = [i.lower().strip() for i in r.get("ingredients", [])]
            if len(recipe_ingredients) == 0:
                continue

            match_count = 0
            for user_ing in user_ingredients:
                for rec_ing in recipe_ingredients:
                    if user_ing in rec_ing or rec_ing in user_ing:
                        match_count += 1
                        break

            match_percent = (match_count / len(user_ingredients)) * 100 if user_ingredients else 0
            if match_percent <= 0:
                continue

            fallback_results.append({
                "name": r.get("name_of_dish", "Unknown"),
                "ingredients": recipe_ingredients,
                "steps": r.get("instructions_to_cook", []),
                "match": round(match_percent, 2),
                "match_percent": round(match_percent, 2),
                "nutrients": {
                    "calories": round(r.get('nutrients_per_gram', {}).get('calories', 0), 2),
                    "protein_g": round(r.get('nutrients_per_gram', {}).get('protein_g', 0), 2),
                    "fat_g": round(r.get('nutrients_per_gram', {}).get('fat_g', 0), 2),
                    "carbs_g": round(r.get('nutrients_per_gram', {}).get('carbs_g', 0), 2)
                }
            })

        fallback_results.sort(key=lambda x: x["match"], reverse=True)
        return jsonify({
            "recipes": fallback_results[:10],
            "fallback": True,
            "message": "No exact diet-friendly matches found. Showing the closest recipes instead."
        })

    return jsonify({"recipes": results, "fallback": False})


# ❤️ Save liked recipes
@app.route("/like_recipe", methods=["POST"])
def like_recipe():
    data = request.json
    user_id = data.get("user_id")
    recipe = data.get("recipe")
    if user_id and recipe:
        likes_collection.insert_one({"user_id": user_id, "recipe": recipe})
        return jsonify({"message": "saved"})
    return jsonify({"error": "invalid data"}), 400

# 💔 Unlike recipe
@app.route("/unlike_recipe", methods=["POST"])
def unlike_recipe():
    data = request.json
    user_id = data.get("user_id")
    recipe = data.get("recipe")
    if user_id and recipe:
        likes_collection.delete_one({"user_id": user_id, "recipe": recipe})
        return jsonify({"message": "removed"})
    return jsonify({"error": "invalid data"}), 400

# 📋 Get likes
@app.route("/get_likes", methods=["POST"])
def get_likes():
    data = request.json
    user_id = data.get("user_id")
    if user_id:
        likes = list(likes_collection.find({"user_id": user_id}, {"_id": 0, "recipe": 1}))
        recipes = [l["recipe"] for l in likes]
        return jsonify({"likes": recipes})
    return jsonify({"likes": []})


if __name__ == "__main__":
    app.run(debug=True)