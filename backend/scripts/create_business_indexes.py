"""
Creates Atlas Search indexes for local_businesses.
Drops the unused venues_description_embedding index first to stay under M0 3-index limit.
"""
import os
import time
from pymongo import MongoClient
from pymongo.operations import SearchIndexModel
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["matchmind"]

# drop unused venues vector index to free a slot
print("dropping venues_description_embedding...")
try:
    db.venues.drop_search_index("venues_description_embedding")
    # give Atlas a moment to process the drop
    time.sleep(3)
    print("  dropped")
except Exception as e:
    print(f"  skip (already gone or error): {e}")

# vector search index — used by hybrid_search_businesses()
print("creating businesses_vector...")
vector_model = SearchIndexModel(
    definition={
        "fields": [
            {
                "type": "vector",
                "path": "description_embedding",
                "numDimensions": 768,
                "similarity": "cosine",
            },
            {"type": "filter", "path": "venue_id"},
            {"type": "filter", "path": "halal_flag"},
            {"type": "filter", "path": "vegan_flag"},
        ]
    },
    name="businesses_vector",
    type="vectorSearch",
)
db.local_businesses.create_search_index(vector_model)
print("  submitted")

# atlas search (BM25) index — used for text keyword matching in hybrid search
print("creating businesses_text...")
text_model = SearchIndexModel(
    definition={
        "mappings": {
            "dynamic": False,
            "fields": {
                "name": {"type": "string"},
                "category": {"type": "string"},
                "cuisine": {"type": "string"},
                "address": {"type": "string"},
            },
        }
    },
    name="businesses_text",
    type="search",
)
db.local_businesses.create_search_index(text_model)
print("  submitted")

print("\nIndexes submitted. Atlas builds them in the background (usually 1-3 min).")
print("Run check_indexes.py to confirm status.")
