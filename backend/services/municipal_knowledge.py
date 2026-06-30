import time
from typing import List, Optional
from backend.repositories.zone import ZoneRepository
from backend.repositories.asset import AssetRepository
from backend.repositories.history import HistoryRepository
from backend.repositories.policy import PolicyRepository
from backend.repositories.root_cause import RootCauseRepository

from backend.services.zone import ZoneService
from backend.services.asset import AssetService
from backend.services.history import HistoryService
from backend.services.policy import PolicyService
from backend.services.weather_provider import WeatherProvider, OpenWeatherProvider, MockWeatherProvider

from backend.models.models import (
    KnowledgeContext, IssueContext, TraceItem,
    Zone, Asset, HistoricalIncident, Policy, RootCause, WeatherSnapshot
)
from backend.config import settings

class MunicipalKnowledgeService:
    def __init__(self):
        # Repositories
        self.zone_repo = ZoneRepository()
        self.asset_repo = AssetRepository()
        self.history_repo = HistoryRepository()
        self.policy_repo = PolicyRepository()
        self.root_cause_repo = RootCauseRepository()

        # Services
        self.zone_service = ZoneService(self.zone_repo, self.asset_repo)
        self.asset_service = AssetService(self.asset_repo)
        self.history_service = HistoryService(self.history_repo)
        self.policy_service = PolicyService(self.policy_repo, self.root_cause_repo)

        # Weather Provider
        weather_key = os.getenv("OPEN_WEATHER") or getattr(settings, "OPEN_WEATHER", None)
        if weather_key:
            self.weather_provider = OpenWeatherProvider(weather_key)
        else:
            self.weather_provider = MockWeatherProvider()

    async def retrieve_context(self, issue_id: str, category: str, severity: int, lat: float, lng: float, embedding: List[float]) -> KnowledgeContext:
        trace: List[TraceItem] = []
        issue_ctx = IssueContext(
            id=issue_id,
            category=category,
            severity=severity,
            lat=lat,
            lng=lng,
            embedding=embedding
        )

        # Step 1: Zone Resolution
        t0 = time.time()
        zone = self.zone_service.resolve_zone(lat, lng)
        latency = int((time.time() - t0) * 1000)
        zone_name = zone.name if zone else "Unknown Zone"
        trace.append(TraceItem(
            step=1,
            service="ZoneService",
            status="SUCCESS",
            latency_ms=latency,
            summary=f"Resolved GIS boundary: {zone_name}."
        ))

        zone_id = zone.id if zone else "Z_UNKNOWN"

        # Step 2: Selective Asset Retrieval
        t0 = time.time()
        assets = self.asset_service.get_nearest_assets(zone_id, lat, lng, category, limit=5)
        latency = int((time.time() - t0) * 1000)
        trace.append(TraceItem(
            step=2,
            service="AssetService",
            status="SUCCESS",
            latency_ms=latency,
            summary=f"Retrieved {len(assets)} proximal infrastructure assets."
        ))

        # Step 3: Historical Incidents retrieval with Python spatial/semantic ranking
        t0 = time.time()
        history = self.history_service.get_similar_incidents(category, lat, lng, embedding, limit=5)
        latency = int((time.time() - t0) * 1000)
        trace.append(TraceItem(
            step=3,
            service="HistoryService",
            status="SUCCESS",
            latency_ms=latency,
            summary=f"Indexed {len(history)} similar historical incidents."
        ))

        # Step 4: Weather provider
        t0 = time.time()
        weather = await self.weather_provider.get_weather(lat, lng)
        latency = int((time.time() - t0) * 1000)
        trace.append(TraceItem(
            step=4,
            service="WeatherService",
            status="SUCCESS",
            latency_ms=latency,
            summary=f"Fetched local weather logs: {weather.weather_condition} ({weather.source})."
        ))

        # Step 5: Active Policy retrieval
        t0 = time.time()
        policies = self.policy_service.get_policies_for_category(category)
        root_causes = self.policy_service.get_root_causes_for_category(category)
        latency = int((time.time() - t0) * 1000)
        trace.append(TraceItem(
            step=5,
            service="PolicyService",
            status="SUCCESS",
            latency_ms=latency,
            summary=f"Ingested {len(policies)} policies & {len(root_causes)} root cause models."
        ))

        return KnowledgeContext(
            issue=issue_ctx,
            zone=zone,
            nearest_assets=assets,
            historical_cases=history,
            weather=weather,
            policies=policies,
            root_causes=root_causes,
            decision_trace=trace
        )

import os
