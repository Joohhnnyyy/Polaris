from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class DamageAgeCategory(str, Enum):
    ACUTE = "ACUTE"
    SUB_ACUTE = "SUB_ACUTE"
    CHRONIC = "CHRONIC"
    UNKNOWN = "UNKNOWN"

class IntakeResponse(BaseModel):
    category: Literal["Pothole", "Water Leak", "Pavement Subsidence", "Garbage Pile", "Broken Streetlight", "Other"] = Field(
        ..., description="The category classification of the civic issue"
    )
    severity: int = Field(..., ge=1, le=5, description="Severity rubric from 1 (Cosmetic) to 5 (Critical public safety risk)")
    area_affected_m2: float = Field(..., description="Estimated size of the affected area in square meters")
    infrastructure_type: str = Field(..., description="Type of infrastructure involved (e.g. road, water pipe, sidewalk)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence of the intake classification")
    summary: str = Field(..., description="Brief one-sentence summary of the reported issue")
    is_civic_issue: bool = Field(..., description="True if the image represents actual civic or public infrastructure issues, False if not")

class ForensicCauseItem(BaseModel):
    cause: str = Field(..., description="Candidate root cause from visual evidence")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this cause based purely on visual inspection")

class EvidenceResponse(BaseModel):
    observations: List[str] = Field(..., description="List of general visual observations from the image")
    physical_damage: List[str] = Field(..., description="Specific physical damage observed (cracks, holes, breaks)")
    environmental_signals: List[str] = Field(..., description="Environmental signals (standing water, wet soil, foliage overgrowth)")
    uncertainties: List[str] = Field(..., description="Key uncertainties or non-visible elements (e.g. underground depth)")
    candidate_causes: List[ForensicCauseItem] = Field(..., description="Constrained candidate root causes from the allowed domain list")
    estimated_dimensions: str = Field(..., description="Forensic estimate of the damage dimensions")
    cascade_risk_assessment: str = Field(..., description="Assessment of risks of cascading/secondary failure")
    damage_age_estimate: DamageAgeCategory = Field(..., description="Calibrated age estimation category")
    structural_risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(..., description="Categorized structural risk based on observed damage severity")
    risk_factors: List[str] = Field(..., description="Traceable risk factors driving the structural risk assessment")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the forensics analysis")

class EvidenceItem(BaseModel):
    source: str = Field(..., description="Source of the evidence (e.g. Vector Search, Historical Cluster, Forensics)")
    evidence: str = Field(..., description="Description of the evidence")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this evidence item")

class ConfidenceSources(BaseModel):
    vision: float = Field(..., ge=0.0, le=1.0, description="Confidence from image analysis")
    similarity: float = Field(..., ge=0.0, le=1.0, description="Confidence from spatial vector similarity")
    historical: float = Field(..., ge=0.0, le=1.0, description="Confidence from historical context/memory")
    causal_prior: float = Field(..., ge=0.0, le=1.0, description="Confidence from the causal rules engine prior")

class RootCauseDecision(str, Enum):
    CONFIDENT = "CONFIDENT"
    UNCERTAIN = "UNCERTAIN"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

class CausalHypothesisItem(BaseModel):
    cause: str = Field(..., description="Potential root cause hypothesis")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this hypothesis")
    supporting_evidence: List[str] = Field(default_factory=list, description="Specific evidence items supporting this cause")
    contradictory_evidence: List[str] = Field(default_factory=list, description="Specific evidence items contradicting this cause")

class SynthesisResponse(BaseModel):
    risk_level: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"] = Field(..., description="Assessed overall risk level of the cluster")
    causal_hypothesis: str = Field(..., description="Synthesized causal hypothesis explaining the failure chain")
    top_hypotheses: List[CausalHypothesisItem] = Field(default_factory=list, description="Ranked list of potential causes with supporting/contradictory evidence")
    decision: RootCauseDecision = Field(..., description="Causal reasoning decision state")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Causal link confidence score")
    confidence_sources: Optional[ConfidenceSources] = Field(None, description="Detailed sources breakdown of the confidence calculation")
    affected_residents: int = Field(..., description="Estimated number of affected residents")
    preventive_cost_estimate_rupees: float = Field(..., description="Estimated cost of preventive repairs in Rupees")
    reactive_cost_estimate_rupees: float = Field(..., description="Estimated cost if the failure is left to reactive damage in Rupees")
    evidence_chain_issue_ids: List[str] = Field(..., description="List of issue UUIDs included in this cluster")
    explainability_factors: List[str] = Field(..., description="Key factors explaining why this risk level was assigned")
    evidence_items: List[EvidenceItem] = Field(default_factory=list, description="Structured items proving/supporting this synthesis")
    decision_summary: str = Field(..., description="Judge-readable summary explaining the final recommendation/risk elevation")

class BriefResponse(BaseModel):
    subject: str = Field(..., description="Urgent email subject line for dispatching details to the authority")
    email_body: str = Field(..., description="Full formatted professional body of the email brief to dispatch")


