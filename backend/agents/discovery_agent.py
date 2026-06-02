def vector_search_faqs(db, query_embedding, limit=5):
    pipeline = [
        {
            "$vectorSearch": {
                "index": "faq_embeddings",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": limit * 10,
                "limit": limit,
            }
        },
        {
            "$project": {
                "_id": 0,
                "question": 1,
                "answer": 1,
                "tags": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]
    return list(db.faq_embeddings.aggregate(pipeline))


def hybrid_search_businesses(db, query_embedding, venue_id, dietary_flags=None, limit=10):
    vs_filter = {"venue_id": venue_id}
    if dietary_flags:
        if "halal" in dietary_flags:
            vs_filter["halal_flag"] = True
        if "vegan" in dietary_flags or "vegetarian" in dietary_flags:
            vs_filter["vegan_flag"] = True

    pipeline = [
        {
            "$vectorSearch": {
                "index": "businesses_vector",
                "path": "description_embedding",
                "queryVector": query_embedding,
                "numCandidates": limit * 10,
                "limit": limit,
                "filter": vs_filter,
            }
        },
        {
            "$project": {
                "_id": 0,
                "name": 1,
                "category": 1,
                "cuisine": 1,
                "halal_flag": 1,
                "vegan_flag": 1,
                "rating": 1,
                "price_range": 1,
                "distance_to_venue_m": 1,
                "address": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]
    return list(db.local_businesses.aggregate(pipeline))


def build_faq_answer(results):
    if not results:
        return None
    top = results[0]
    return {
        "question": top["question"],
        "answer": top["answer"],
        "score": top.get("score"),
        "tags": top.get("tags", []),
    }
