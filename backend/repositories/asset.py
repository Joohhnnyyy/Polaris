from typing import List, Optional
from backend.db.supabase_client import supabase_client
from backend.models.models import Asset
from backend.repositories.base import BaseRepository

class AssetRepository(BaseRepository[Asset]):
    def find(self, id: str) -> Optional[Asset]:
        try:
            res = supabase_client.table("utility_assets").select("*").eq("id", id).eq("is_active", True).execute()
            if res.data:
                row = res.data[0]
                return Asset(
                    id=row["id"],
                    zone_id=row["zone_id"],
                    asset_type=row["asset_type"],
                    material=row.get("material"),
                    diameter_mm=row.get("diameter_mm"),
                    pressure_rating=row.get("pressure_rating"),
                    install_year=row["install_year"],
                    condition_score=row["condition_score"],
                    status=row["status"],
                    lat=row["lat"],
                    lng=row["lng"]
                )
        except Exception as e:
            print(f"Error in AssetRepository.find: {e}")
        return None

    def find_by_zone(self, zone_id: str, asset_type: Optional[str] = None) -> List[Asset]:
        try:
            query = supabase_client.table("utility_assets").select("*").eq("zone_id", zone_id).eq("is_active", True)
            if asset_type:
                query = query.eq("asset_type", asset_type)
            res = query.execute()
            assets = []
            for row in res.data:
                assets.append(Asset(
                    id=row["id"],
                    zone_id=row["zone_id"],
                    asset_type=row["asset_type"],
                    material=row.get("material"),
                    diameter_mm=row.get("diameter_mm"),
                    pressure_rating=row.get("pressure_rating"),
                    install_year=row["install_year"],
                    condition_score=row["condition_score"],
                    status=row["status"],
                    lat=row["lat"],
                    lng=row["lng"]
                ))
            return assets
        except Exception as e:
            print(f"Error in AssetRepository.find_by_zone: {e}")
            return []

    def get_maintenance_history(self, asset_id: str) -> List[dict]:
        try:
            res = supabase_client.table("maintenance_history")\
                .select("*")\
                .eq("asset_id", asset_id)\
                .eq("is_active", True)\
                .order("inspection_date", desc=True)\
                .execute()
            return res.data if res.data else []
        except Exception as e:
            print(f"Error fetching maintenance history for asset {asset_id}: {e}")
            return []

    def save(self, entity: Asset) -> Asset:
        payload = {
            "id": entity.id,
            "zone_id": entity.zone_id,
            "asset_type": entity.asset_type,
            "material": entity.material,
            "diameter_mm": entity.diameter_mm,
            "pressure_rating": entity.pressure_rating,
            "install_year": entity.install_year,
            "condition_score": entity.condition_score,
            "status": entity.status,
            "lat": entity.lat,
            "lng": entity.lng,
            "is_active": entity.is_active
        }
        supabase_client.table("utility_assets").insert(payload).execute()
        return entity
