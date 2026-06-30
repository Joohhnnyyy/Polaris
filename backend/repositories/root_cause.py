from typing import List, Optional
from backend.db.supabase_client import supabase_client
from backend.models.models import RootCause
from backend.repositories.base import BaseRepository

class RootCauseRepository(BaseRepository[RootCause]):
    def find(self, id: str) -> Optional[RootCause]:
        try:
            res = supabase_client.table("root_cause_library").select("*").eq("id", id).execute()
            if res.data:
                row = res.data[0]
                return self._map_row(row)
        except Exception as e:
            print(f"Error in RootCauseRepository.find: {e}")
        return None

    def find_all(self) -> List[RootCause]:
        try:
            res = supabase_client.table("root_cause_library").select("*").execute()
            return [self._map_row(row) for row in res.data]
        except Exception as e:
            print(f"Error in RootCauseRepository.find_all: {e}")
            return []

    def _map_row(self, row: dict) -> RootCause:
        return RootCause(
            id=row["id"],
            category=row["category"],
            cause=row["cause"],
            prior=float(row["prior"]),
            can_cause=row.get("can_cause", []),
            requires=row.get("requires", []),
            evidence_required=row.get("evidence_required", [])
        )
