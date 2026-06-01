import json
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SEED_DIR = Path(__file__).resolve().parent.parent / "data" / "seed"


def get_embedding(text):
    result = genai.embed_content(model="models/text-embedding-004", content=text)
    return result["embedding"]


def embed_venues(db):
    venues = db.venues.find()
    for venue in venues:
        text = venue["description"]
        embedding = get_embedding(text)
        db.venues.update_one(
            {"venue_id": venue["venue_id"]},
            {"$set": {"description_embedding": embedding}}
        )


def build_faq_doc(faq, embedding):
    return {
        "question": faq["question"],
        "answer": faq["answer"],
        "tags": faq["tags"],
        "embedding": embedding,
    }


def embed_faqs(db):
    faq_file = SEED_DIR / "faqs.json"
    faqs = json.loads(faq_file.read_text(encoding="utf-8"))

    db.faq_embeddings.drop()

    docs = []
    for faq in faqs:
        text = faq["question"] + " " + faq["answer"]
        embedding = get_embedding(text)
        docs.append(build_faq_doc(faq, embedding))

    db.faq_embeddings.insert_many(docs)


if __name__ == "__main__":
    from pymongo import MongoClient

    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client[os.getenv("MONGODB_DB_NAME", "matchmind")]

    print("embedding venues...")
    embed_venues(db)
    print("done")

    print("embedding faqs...")
    embed_faqs(db)
    print("done")
