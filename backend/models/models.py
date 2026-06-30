from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Dict, Optional

@dataclass
class Zone:
    id: str
    name: str
    boundary_polygon: List[List[float]]
    assigned_officer_id: Optional[str]
    soil_type: str
    is_active: bool = True

@dataclass
class Asset:
    id: str
    zone_id: str
    asset_type: str
    material: Optional[str]
    diameter_mm: Optional[int]
    pressure_rating: Optional[float]
    install_year: int
    condition_score: int
    status: str
    lat: float
    lng: float
    distance_m: Optional[float] = None

@dataclass
class HistoricalIncident:
    id: int
    zone_id: str
    category: str
    root_cause_id: str
    incident_outcome: str
    confidence: float
    risk_level: str
    resolution_summary: Optional[str]
    resolution_days: int
    resolution_cost: float
    resolution_method: Optional[str]
    verification_votes: int
    dispute_votes: int
    lat: float
    lng: float
    embedding_model: str
    created_at: datetime
    similarity: float = 0.0
    distance: float = 0.0
    retrieval_score: float = 0.0

@dataclass
class Policy:
    id: str
    rule_name: str
    category: str
    dispatch_if: Dict[str, Any]
    minimum_confidence: float
    minimum_reports: int
    minimum_votes: int
    max_response_time_hours: int
    requires_human: bool
    escalation_department: str
    knowledge_version: str

@dataclass
class RootCause:
    id: str
    category: str
    cause: str
    prior: float
    can_cause: List[str] = field(default_factory=list)
    requires: List[str] = field(default_factory=list)
    evidence_required: List[str] = field(default_factory=list)

@dataclass
class WeatherSnapshot:
    weather_condition: str
    rain_accumulation_mm: float
    temperature_c: float
    source: str

@dataclass
class TraceItem:
    step: int
    service: str
    status: str
    latency_ms: int
    summary: str
    confidence: Optional[float] = None

@dataclass
class IssueContext:
    id: str
    category: str
    severity: int
    lat: float
    lng: float
    embedding: List[float]

@dataclass
class KnowledgeContext:
    issue: IssueContext
    zone: Optional[Zone] = None
    nearest_assets: List[Asset] = field(default_factory=list)
    historical_cases: List[HistoricalIncident] = field(default_factory=list)
    weather: Optional[WeatherSnapshot] = None
    policies: List[Policy] = field(default_factory=list)
    root_causes: List[RootCause] = field(default_factory=list)
    decision_trace: List[TraceItem] = field(default_factory=list)
