import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["matchmind"]

for col in ["faq_embeddings", "venues", "local_businesses"]:
    idxs = list(db[col].list_search_indexes())
    names = [i.get("name") for i in idxs]
    print(f"{col}: {names}")
