from typing import List, Optional
from datetime import datetime
from backend.db.supabase_client import supabase_client
from backend.models.models import HistoricalIncident
from backend.repositories.base import BaseRepository

class HistoryRepository(BaseRepository[HistoricalIncident]):
    def find(self, id: str) -> Optional[HistoricalIncident]:
        try:
            res = supabase_client.table("historical_incidents").select("*").eq("id", int(id)).eq("is_active", True).execute()
            if res.data:
                row = res.data[0]
                return self._map_row(row)
        except Exception as e:
            print(f"Error in HistoryRepository.find: {e}")
        return None

    def find_by_category(self, category: str) -> List[HistoricalIncident]:
        try:
            res = supabase_client.table("historical_incidents").select("*").eq("category", category).eq("is_active", True).execute()
            return [self._map_row(row) for row in res.data]
        except Exception as e:
            print(f"Error in HistoryRepository.find_by_category: {e}")
            return []

    def find_all(self) -> List[HistoricalIncident]:
        try:
            res = supabase_client.table("historical_incidents").select("*").eq("is_active", True).execute()
            return [self._map_row(row) for row in res.data]
        except Exception as e:
            print(f"Error in HistoryRepository.find_all: {e}")
            return []

    def save(self, entity: HistoricalIncident) -> HistoricalIncident:
        payload = {
            "zone_id": entity.zone_id,
            "category": entity.category,
            "root_cause_id": entity.root_cause_id,
            "incident_outcome": entity.incident_outcome,
            "confidence": entity.confidence,
            "risk_level": entity.risk_level,
            "resolution_summary": entity.resolution_summary,
            "resolution_days": entity.resolution_days,
            "resolution_cost": entity.resolution_cost,
            "resolution_method": entity.resolution_method,
            "verification_votes": entity.verification_votes,
            "dispute_votes": entity.dispute_votes,
            "lat": entity.lat,
            "lng": entity.lng,
            "is_active": entity.is_active
        }
        res = supabase_client.table("historical_incidents").insert(payload).execute()
        if res.data:
            entity.id = res.data[0]["id"]
        return entity

    def _map_row(self, row: dict) -> HistoricalIncident:
        # Convert created_at string to datetime
        created_at = datetime.utcnow()
        if "created_at" in row and row["created_at"]:
            try:
                # Handle formats like 2026-06-30T04:41:48+00:00 or similar
                created_str = row["created_at"].replace("Z", "+00:00")
                created_at = datetime.fromisoformat(created_str)
            except Exception:
                pass
        return HistoricalIncident(
            id=row["id"],
            zone_id=row["zone_id"],
            category=row["category"],
            root_cause_id=row["root_cause_id"],
            incident_outcome=row["incident_outcome"],
            confidence=float(row["confidence"]),
            risk_level=row["risk_level"],
            resolution_summary=row.get("resolution_summary"),
            resolution_days=row.get("resolution_days", 3),
            resolution_cost=float(row.get("resolution_cost", 0.0)),
            resolution_method=row.get("resolution_method"),
            verification_votes=row.get("verification_votes", 1),
            dispute_votes=row.get("dispute_votes", 0),
            lat=row["lat"],
            lng=row["lng"],
            embedding_model=row.get("embedding_model", "gemini-embedding-2"),
            created_at=created_at
        )
