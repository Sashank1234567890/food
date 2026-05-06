from pymongo import MongoClient
import json

client = MongoClient('mongodb://localhost:27017/')
db = client['config']
col = db['recipes']

print('Total recipes:', col.count_documents({}))
print()

print('Searching for recipes with rice, tomato, onion...')
print('With rice:', col.count_documents({'ingredients': {'$elemMatch': {'$regex': 'rice', '$options': 'i'}}}))
print('With tomato:', col.count_documents({'ingredients': {'$elemMatch': {'$regex': 'tomato', '$options': 'i'}}}))
print('With onion:', col.count_documents({'ingredients': {'$elemMatch': {'$regex': 'onion', '$options': 'i'}}}))
print()

print('Sample recipes with low carbs (diabetes-friendly):')
for rec in col.find({'nutrients_per_gram.carbs_g': {'$lt': 0.20}}).limit(5):
    print(f"  {rec.get('name_of_dish')}: carbs={rec.get('nutrients_per_gram', {}).get('carbs_g')}, ingredients={rec.get('ingredients', [])[:2]}")
