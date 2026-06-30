from typing import List, Optional
import json
from backend.db.supabase_client import supabase_client
from backend.models.models import Zone
from backend.repositories.base import BaseRepository

class ZoneRepository(BaseRepository[Zone]):
    def find(self, id: str) -> Optional[Zone]:
        try:
            res = supabase_client.table("zones").select("*").eq("id", id).eq("is_active", True).execute()
            if res.data:
                row = res.data[0]
                # Safely parse boundary_polygon JSON
                poly = row["boundary_polygon"]
                if isinstance(poly, str):
                    poly = json.loads(poly)
                return Zone(
                    id=row["id"],
                    name=row["name"],
                    boundary_polygon=poly,
                    assigned_officer_id=row.get("assigned_officer_id"),
                    soil_type=row.get("soil_type", "Clayey")
                )
        except Exception as e:
            print(f"Error in ZoneRepository.find: {e}")
        return None

    def find_all(self) -> List[Zone]:
        try:
            res = supabase_client.table("zones").select("*").eq("is_active", True).execute()
            zones = []
            for row in res.data:
                poly = row["boundary_polygon"]
                if isinstance(poly, str):
                    poly = json.loads(poly)
                zones.append(Zone(
                    id=row["id"],
                    name=row["name"],
                    boundary_polygon=poly,
                    assigned_officer_id=row.get("assigned_officer_id"),
                    soil_type=row.get("soil_type", "Clayey")
                ))
            return zones
        except Exception as e:
            print(f"Error in ZoneRepository.find_all: {e}")
            return []

    def save(self, entity: Zone) -> Zone:
        payload = {
            "id": entity.id,
            "name": entity.name,
            "boundary_polygon": entity.boundary_polygon,
            "assigned_officer_id": entity.assigned_officer_id,
            "soil_type": entity.soil_type,
            "is_active": entity.is_active
        }
        supabase_client.table("zones").insert(payload).execute()
        return entity
