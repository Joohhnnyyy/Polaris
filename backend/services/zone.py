from typing import Optional, List
import time
from backend.repositories.zone import ZoneRepository
from backend.repositories.asset import AssetRepository
from backend.models.models import Zone

class ZoneService:
    def __init__(self, zone_repo: ZoneRepository, asset_repo: AssetRepository):
        self.zone_repo = zone_repo
        self.asset_repo = asset_repo
        # Local Cache
        self._cache_zones: List[Zone] = []
        self._cache_time: float = 0.0
        self._ttl_seconds: float = 24 * 3600 # 24 Hours TTL

    def _refresh_cache(self):
        now = time.time()
        if not self._cache_zones or (now - self._cache_time) > self._ttl_seconds:
            self._cache_zones = self.zone_repo.find_all()
            self._cache_time = now

    def resolve_zone(self, lat: float, lng: float) -> Optional[Zone]:
        self._refresh_cache()
        # 1. Bounding Box Filter first for fast spatial retrieval scaling
        candidate_zones = []
        for zone in self._cache_zones:
            poly = zone.boundary_polygon
            if not poly:
                continue
            lats = [pt[0] for pt in poly]
            lngs = [pt[1] for pt in poly]
            min_lat, max_lat = min(lats), max(lats)
            min_lng, max_lng = min(lngs), max(lngs)
            
            if min_lat <= lat <= max_lat and min_lng <= lng <= max_lng:
                candidate_zones.append(zone)
        
        # 2. Detailed Ray-Casting Point-in-Polygon check on candidates
        for zone in candidate_zones:
            if self._point_in_polygon(lat, lng, zone.boundary_polygon):
                return zone
                
        # If outside all polygons, assign default nearest zone
        if self._cache_zones:
            return self._cache_zones[0]
        return None

    def get_dominant_material(self, zone_id: str) -> str:
        # Compute dynamically from assets
        assets = self.asset_repo.find_by_zone(zone_id, asset_type="WATER_MAIN")
        if not assets:
            return "Cast Iron" # Fallback default
        counts = {}
        for asset in assets:
            if asset.material:
                counts[asset.material] = counts.get(asset.material, 0) + 1
        if not counts:
            return "Cast Iron"
        return max(counts, key=counts.get)

    def get_average_pipe_age(self, zone_id: str) -> int:
        # Compute dynamically from assets
        assets = self.asset_repo.find_by_zone(zone_id, asset_type="WATER_MAIN")
        if not assets:
            return 35 # Fallback default
        current_year = 2026
        years = [current_year - asset.install_year for asset in assets]
        return int(sum(years) / len(years)) if years else 35

    def _point_in_polygon(self, x: float, y: float, poly: List[List[float]]) -> bool:
        n = len(poly)
        inside = False
        p1x, p1y = poly[0]
        for i in range(n + 1):
            p2x, p2y = poly[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xints:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside
