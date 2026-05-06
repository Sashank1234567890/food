from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['config']
col = db['recipes']

user_ingredients = ['rice', 'tomato', 'onion']
diet_filters = ['diabetes']

all_recipes = list(col.find())
results = []

print(f'Testing {len(all_recipes)} recipes...')
print(f'User ingredients: {user_ingredients}')
print(f'Diet filters: {diet_filters}')
print()

for r in all_recipes:
    recipe_ingredients = [i.lower().strip() for i in r.get('ingredients', [])]
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

    nutrients = r.get('nutrients_per_gram', {})
    calories = nutrients.get('calories', 0)
    protein = nutrients.get('protein_g', 0)
    fat = nutrients.get('fat_g', 0)
    carbs = nutrients.get('carbs_g', 0)

    ok = True
    if 'diabetes' in diet_filters and carbs >= 0.20:
        ok = False

    if ok:
        results.append({
            'name': r.get('name_of_dish'),
            'match': round(match_percent, 2),
            'carbs': carbs
        })

results.sort(key=lambda x: x['match'], reverse=True)

print(f'Found {len(results)} matching recipes')
print('\nTop 10 results:')
for i, r in enumerate(results[:10]):
    print(f"  {i+1}. {r['name']} - {r['match']}% match (carbs: {r['carbs']})")
