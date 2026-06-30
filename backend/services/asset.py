from typing import List, Optional
import time
from math import sqrt
from backend.repositories.asset import AssetRepository
from backend.models.models import Asset

class AssetService:
    def __init__(self, asset_repo: AssetRepository):
        self.asset_repo = asset_repo
        # Cache zone_id -> (assets, timestamp)
        self._cache = {}
        self._ttl_seconds = 300 # 5 Minutes TTL

    def get_nearest_assets(self, zone_id: str, lat: float, lng: float, category: str, limit: int = 5) -> List[Asset]:
        # 1. Map issue category to relevant asset types (Selective Retrieval)
        relevant_types = []
        if category == "Water Leak":
            relevant_types = ["WATER_MAIN", "DRAIN"]
        elif category == "Pavement Subsidence" or category == "Pothole":
            relevant_types = ["ROAD", "DRAIN", "WATER_MAIN"]
        elif category == "Broken Streetlight":
            relevant_types = ["STREETLIGHT", "TRANSFORMER"]
        else:
            relevant_types = ["ROAD", "FOOTPATH"]

        # 2. Get assets (check cache first)
        now = time.time()
        cached = self._cache.get(zone_id)
        if cached and (now - cached[1]) < self._ttl_seconds:
            all_assets = cached[0]
        else:
            all_assets = self.asset_repo.find_by_zone(zone_id)
            self._cache[zone_id] = (all_assets, now)

        # Filter by relevant types
        filtered = [a for a in all_assets if a.asset_type in relevant_types]
        if not filtered:
            # Fallback to all if no matched types
            filtered = all_assets

        # 3. Compute distance to each asset and sort
        for asset in filtered:
            d_lat = asset.lat - lat
            d_lng = asset.lng - lng
            # Approximated spatial distance in meters
            asset.distance_m = float(111320.0 * sqrt(d_lat*d_lat + d_lng*d_lng))

        filtered.sort(key=lambda a: a.distance_m if a.distance_m is not None else 99999)
        return filtered[:limit]
