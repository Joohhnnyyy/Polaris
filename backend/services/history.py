from typing import List
from math import sqrt
from backend.repositories.history import HistoryRepository
from backend.models.models import HistoricalIncident

class HistoryService:
    def __init__(self, history_repo: HistoryRepository):
        self.history_repo = history_repo

    def get_similar_incidents(self, category: str, lat: float, lng: float, query_embedding: List[float], limit: int = 5) -> List[HistoricalIncident]:
        if isinstance(query_embedding, str):
            try:
                cleaned = query_embedding.strip("[] ")
                query_embedding = [float(x) for x in cleaned.split(",") if x.strip()]
            except Exception:
                query_embedding = [0.0] * 768

        # 1. Fetch historical incidents from DB
        # Only query incidents of the same category or overall to match
        incidents = self.history_repo.find_by_category(category)
        if not incidents:
            # Fallback to all if none in category
            incidents = self.history_repo.find_all()

        # 2. Query historical incident embedding vectors
        try:
            db_res = supabase_client_table_embeddings()
        except Exception:
            db_res = {}

        # 3. Calculate scores for each historical case
        scored_incidents = []
        for inc in incidents:
            # Spatial distance
            d_lat = inc.lat - lat
            d_lng = inc.lng - lng
            dist_m = float(111320.0 * sqrt(d_lat*d_lat + d_lng*d_lng))
            inc.distance = dist_m

            # Spatial score: higher score for closer incidents (halves every 100 meters)
            spatial_score = 1.0 / (1.0 + (dist_m / 100.0))

            # Embedding similarity
            embedding = db_res.get(inc.id)
            sim = 0.8 # default baseline
            if embedding and query_embedding:
                # Align dimensions by padding query_embedding to match DB vector length
                aligned_query = query_embedding
                if len(aligned_query) < len(embedding):
                    aligned_query = aligned_query + [0.0] * (len(embedding) - len(aligned_query))
                elif len(aligned_query) > len(embedding):
                    aligned_query = aligned_query[:len(embedding)]
                sim = self._cosine_similarity(aligned_query, embedding)
            inc.similarity = float(sim)

            # Combined retrieval score: 60% semantic similarity + 40% spatial proximity
            inc.retrieval_score = float((sim * 0.60) + (spatial_score * 0.40))
            scored_incidents.append(inc)

        # Sort by unified retrieval score descending
        scored_incidents.sort(key=lambda i: i.retrieval_score, reverse=True)
        return scored_incidents[:limit]

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.8
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = sum(a * a for a in v1) ** 0.5
        norm2 = sum(b * b for b in v2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.8
        return dot / (norm1 * norm2)

def supabase_client_table_embeddings() -> dict:
    # Quick utility to retrieve embeddings directly from historical_incidents table
    from backend.db.supabase_client import supabase_client
    import json
    try:
        res = supabase_client.table("historical_incidents").select("id, embedding").execute()
        embeddings = {}
        for row in res.data:
            val = row.get("embedding")
            if not val:
                continue
            if isinstance(val, str):
                try:
                    # Clean and parse '[0.1,0.2,...]'
                    cleaned = val.strip("[] ")
                    float_list = [float(x) for x in cleaned.split(",") if x.strip()]
                    embeddings[row["id"]] = float_list
                except Exception:
                    pass
            elif isinstance(val, list):
                embeddings[row["id"]] = [float(x) for x in val]
        return embeddings
    except Exception:
        return {}
