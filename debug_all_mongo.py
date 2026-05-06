from pymongo import MongoClient
import json

client = MongoClient('mongodb://localhost:27017/')

print('All databases:')
for db_name in client.list_database_names():
    print(f'\n{db_name}:')
    db = client[db_name]
    collections = db.list_collection_names()
    print(f'  Collections: {collections}')
    for col_name in collections:
        col = db[col_name]
        count = col.count_documents({})
        print(f'    {col_name}: {count} docs')
