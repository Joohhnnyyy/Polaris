from typing import List, Optional
import json
from backend.db.supabase_client import supabase_client
from backend.models.models import Policy
from backend.repositories.base import BaseRepository

class PolicyRepository(BaseRepository[Policy]):
    def find(self, id: str) -> Optional[Policy]:
        try:
            res = supabase_client.table("municipal_policies").select("*").eq("id", id).execute()
            if res.data:
                row = res.data[0]
                return self._map_row(row)
        except Exception as e:
            print(f"Error in PolicyRepository.find: {e}")
        return None

    def find_all(self) -> List[Policy]:
        try:
            res = supabase_client.table("municipal_policies").select("*").execute()
            return [self._map_row(row) for row in res.data]
        except Exception as e:
            print(f"Error in PolicyRepository.find_all: {e}")
            return []

    def _map_row(self, row: dict) -> Policy:
        dispatch = row.get("dispatch_if", {})
        if isinstance(dispatch, str):
            try:
                dispatch = json.loads(dispatch)
            except Exception:
                dispatch = {}
        return Policy(
            id=row["id"],
            rule_name=row["rule_name"],
            category=row["category"],
            dispatch_if=dispatch,
            minimum_confidence=float(row.get("minimum_confidence", 0.0)),
            minimum_reports=row.get("minimum_reports", 0),
            minimum_votes=row.get("minimum_votes", 0),
            max_response_time_hours=row.get("max_response_time_hours", 24),
            requires_human=row.get("requires_human", True),
            escalation_department=row["escalation_department"],
            knowledge_version=row.get("knowledge_version", "v1.0")
        )
