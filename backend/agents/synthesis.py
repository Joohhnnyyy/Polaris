import json
import time
from datetime import datetime
from backend.db.supabase_client import supabase_client
from backend.agents.gemini_client import get_gemini_model, gemini_call_rate_limited
from backend.agents.schemas import SynthesisResponse

from backend.services.municipal_knowledge import MunicipalKnowledgeService
from backend.services.context_builder import ContextBuilder
from backend.models.models import KnowledgeContext, IssueContext, TraceItem

CAUSAL_RELATIONS = {
    ("Water Leak", "Pavement Subsidence"): 0.85,
    ("Pavement Subsidence", "Pothole"): 0.75,
    ("Water Leak", "Pothole"): 0.70,
    ("Drain Blockage", "Water Leak"): 0.65
}

class SynthesisAgent:
    def __init__(self):
        # Synthesis uses Gemini 2.5 Pro for deep urban autopsy reasoning
        self.model = get_gemini_model("gemini-2.5-pro")
        self.mks = MunicipalKnowledgeService()
        self.context_builder = ContextBuilder()

    async def run_synthesis(self, new_issue: dict, on_step_callback=None) -> dict:
        """
        Runs the main Gemini prompt logic consulting the Municipal Knowledge Service.
        """
        start_time = time.time()
        llm_calls_count = 0
        token_usage = 0
        fallback_used = False

        issue_id = new_issue["id"]
        category = new_issue["category"]
        severity = new_issue["severity"]
        lat = new_issue["lat"]
        lng = new_issue["lng"]
        embedding = new_issue.get("embedding") or ([0.0] * 768)

        # 1. Query Municipal Knowledge Service (MKS) context
        context = await self.mks.retrieve_context(
            issue_id=issue_id,
            category=category,
            severity=severity,
            lat=lat,
            lng=lng,
            embedding=embedding
        )

        # Ingest resolved details
        zone_id = context.zone.id if context.zone else "Z_UNKNOWN"
        zone_name = context.zone.name if context.zone else "Unknown"

        # Update intermediate context in DB
        try:
            intermediate_trace = [
                {"step": 1, "service": "IntakeAgentService", "status": "SUCCESS", "latency_ms": 100, "summary": f"Report categorized as {category} (Severity: {severity}/5)"},
                {"step": 2, "service": "EvidenceAgentService", "status": "SUCCESS", "latency_ms": 100, "summary": "Forensics and embeddings completed."},
                {"step": 3, "service": "MunicipalKnowledgeService", "status": "SUCCESS", "latency_ms": 50, "summary": f"Retrieved context for zone {zone_name}."}
            ]
            supabase_client.table("decision_audit").update({
                "decision_trace": json.dumps({
                    "trace": intermediate_trace,
                    "context": {
                        "zone": context.zone.__dict__ if context.zone else None,
                        "weather": context.weather.__dict__ if context.weather else None,
                        "nearest_assets": [a.__dict__ for a in context.nearest_assets],
                        "historical_cases": [{
                            "id": h.id,
                            "category": h.category,
                            "incident_outcome": h.incident_outcome,
                            "similarity": h.similarity,
                            "distance": h.distance,
                            "retrieval_score": h.retrieval_score,
                            "resolution_summary": h.resolution_summary
                        } for h in context.historical_cases]
                    }
                })
            }).eq("issue_id", issue_id).execute()

            if on_step_callback:
                await on_step_callback("Synthesis", f"Retrieved municipal context: weather ({context.weather.weather_condition if context.weather else 'Clear'}), {len(context.nearest_assets)} assets, {len(context.historical_cases)} past cases.")
        except Exception as inter_err:
            print(f"Failed to save intermediate decision audit: {inter_err}")

        # 2. Format LLM Context Prompt using ContextBuilder
        formatted_context = self.context_builder.build_llm_context(context)

        system_instruction = """
        You are CivicMind's Urban Intelligence Agent. 
        You analyze current reports and compare them against municipal registers and policies.
        
        Follow a Multi-Stage Reasoning Flow:
        1. **Evidence Collection**: Analyze nearby infrastructure assets and historical incidents.
        2. **Relationship Validation**: Compute pairwise relationships and causal prior connections.
        3. **Historical Match**: Compare with similar past resolved cases in the zone.
        4. **Contradiction Detection**: Check for conflicting observations (e.g. water leaks with dry weather, or unrelated categories).
        5. **Root Cause Ranking**: Ingest allowed root causes from the Root Cause Library and rank them.
        6. **Policy Evaluation**: Apply active policies (minimum confidence, reports, response times).
        """

        input_prompt = f"""
        {formatted_context}
        
        Using the above municipal data and policy guidelines, determine if this issue is part of an active infrastructure failure.
        Run your analysis and output a structured Risk Brief JSON matching this schema:
        {{
            "risk_level": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
            "causal_hypothesis": "Brief description of the top causal chain",
            "top_hypotheses": [
                {{
                    "cause": "Potential root cause from allowed list",
                    "confidence": float (0.0 to 1.0),
                    "supporting_evidence": ["list of supporting reasons/observations"],
                    "contradictory_evidence": ["list of contradictions or missing indicators"]
                }}
            ],
            "decision": "CONFIDENT" | "UNCERTAIN" | "INSUFFICIENT_EVIDENCE",
            "confidence": float (0.0 to 1.0),
            "affected_residents": integer,
            "preventive_cost_estimate_rupees": float,
            "reactive_cost_estimate_rupees": float,
            "evidence_chain_issue_ids": ["array of issue IDs included in this cluster"],
            "explainability_factors": ["List 2-4 key reasons why this risk level was assigned"],
            "evidence_items": [
                {{
                    "source": "Vector Search" | "Historical Cluster" | "Forensics",
                    "evidence": "Description of matching data",
                    "confidence": float (0.0 to 1.0)
                }}
            ],
            "decision_summary": "Summary explaining the final recommendation or risk elevation"
        }}
        """

        try:
            llm_calls_count += 1
            t0 = time.time()
            response = await gemini_call_rate_limited(
                self.model,
                f"{system_instruction}\n\n{input_prompt}",
                method="generate_content",
                generation_config={"response_mime_type": "application/json"}
            )
            llm_latency = int((time.time() - t0) * 1000)
            token_usage = len(response.text) // 4 # Rough approximation of tokens

            # Update trace with LLM execution
            context.decision_trace.append(TraceItem(
                step=len(context.decision_trace) + 1,
                service="LLMSynthesisService",
                status="SUCCESS",
                latency_ms=llm_latency,
                summary="Generated causal analysis brief using Gemini 2.5 Pro."
            ))

            parsed = SynthesisResponse.model_validate_json(response.text)
            result = parsed.model_dump()
            result["decision_trace"] = [t.__dict__ for t in context.decision_trace]

        except Exception as e:
            print(f"Synthesis Agent Gemini call failed: {e}. Executing production-grade local rule engine.")
            fallback_used = True
            
            # Local Fallback Rule Engine Path
            # Computes decisions and risk levels deterministically using MKS context data
            valid_evidence_ids = [issue_id]
            similarities = []
            
            # Map nearby issues from history
            for inc in context.historical_cases:
                if inc.similarity > 0.70:
                    valid_evidence_ids.append(str(inc.id))
                    similarities.append(inc.similarity)

            avg_similarity = sum(similarities) / len(similarities) if similarities else 0.8
            
            # Verificationvotes
            votes_for = new_issue.get("verification_votes", 1)
            votes_against = new_issue.get("dispute_votes", 0)
            verification_score = (votes_for + 2) / (votes_for + votes_against + 4)

            # Map category logic
            if category == "Water Leak":
                cause = "Water main rupture" if severity >= 4 else "Sub-surface pipe leak"
                top_hyp = [
                    {"cause": cause, "confidence": 0.80, "supporting_evidence": ["Wet pavement saturation"], "contradictory_evidence": []}
                ]
            elif category == "Pavement Subsidence":
                cause = "Subgrade wash-out from water leak"
                top_hyp = [
                    {"cause": cause, "confidence": 0.75, "supporting_evidence": ["Sunken road surface"], "contradictory_evidence": []}
                ]
            else:
                cause = "General structural decay"
                top_hyp = [
                    {"cause": cause, "confidence": 0.60, "supporting_evidence": [], "contradictory_evidence": []}
                ]

            calibrated_conf = round((avg_similarity * 0.50) + (verification_score * 0.50), 2)
            
            # Policies evaluation
            evaluated_policy = self.mks.policy_service.evaluate_policy(
                category=category,
                risk_level="HIGH" if severity >= 4 else "MEDIUM",
                confidence=calibrated_conf,
                reports_count=len(valid_evidence_ids),
                votes_count=votes_for
            )
            
            risk_level = "CRITICAL" if severity >= 5 else ("HIGH" if severity >= 4 else "MEDIUM")
            decision = "LOCAL_RULE_ENGINE"
            hypothesis = f"[Local Rule Engine] Causal failure path: {cause}."

            affected_residents = max(100, len(valid_evidence_ids) * 200)
            preventive_cost = float(max(20000.0, severity * 35000.0))
            reactive_cost = preventive_cost * 6.0

            result = {
                "risk_level": risk_level,
                "causal_hypothesis": hypothesis,
                "top_hypotheses": top_hyp,
                "decision": decision,
                "confidence": calibrated_conf,
                "affected_residents": affected_residents,
                "preventive_cost_estimate_rupees": preventive_cost,
                "reactive_cost_estimate_rupees": reactive_cost,
                "evidence_chain_issue_ids": valid_evidence_ids,
                "explainability_factors": [
                    f"Resolved active {category} in sector zone {zone_name}.",
                    f"Calibrated rule-engine causal confidence: {int(calibrated_conf*100)}%."
                ],
                "evidence_items": [
                    {"source": "Vector Search", "evidence": f"Found {len(valid_evidence_ids) - 1} historically similar incidents in zone {zone_name}", "confidence": round(avg_similarity, 2)}
                ],
                "decision_summary": f"Risk level assessed as {risk_level} by Local Rule Engine (Policy: {evaluated_policy.rule_name if evaluated_policy else 'Default'})."
            }

            # Update trace with Fallback execution
            context.decision_trace.append(TraceItem(
                step=len(context.decision_trace) + 1,
                service="LocalRuleEngineService",
                status="SUCCESS",
                latency_ms=10,
                summary="Executed local rule engine fallback path."
            ))
            result["decision_trace"] = [t.__dict__ for t in context.decision_trace]

        # 3. Post-Process: Save Cluster and updates in DB
        result["confidence_sources"] = {
            "vision": round(new_issue.get("credibility_score", 1.0), 2),
            "similarity": round(result.get("confidence", 0.8), 2),
            "historical": 0.8 if context.historical_cases else 0.2,
            "causal_prior": 0.7 if len(result.get("evidence_chain_issue_ids", [])) > 1 else 0.5
        }

        # Save to database tables (clusters and issues updates)
        try:
            officer_id = None
            if context.zone and context.zone.assigned_officer_id:
                officer_id = context.zone.assigned_officer_id
            
            cluster_data = {
                "zone_id": zone_name,
                "center_lat": lat,
                "center_lng": lng,
                "radius_m": 300,
                "risk_level": result["risk_level"],
                "causal_hypothesis": result["causal_hypothesis"],
                "confidence": result["confidence"],
                "affected_residents": result["affected_residents"],
                "evidence_chain": json.dumps(result["evidence_chain_issue_ids"])
            }
            cluster_res = supabase_client.table("clusters").insert(cluster_data).execute()
            if cluster_res.data:
                cluster_id = cluster_res.data[0]["id"]
                import uuid
                for issue_id_val in result["evidence_chain_issue_ids"]:
                    try:
                        uuid.UUID(str(issue_id_val))
                        supabase_client.table("issues").update({"cluster_id": cluster_id}).eq("id", issue_id_val).execute()
                    except ValueError:
                        pass
                result["cluster_id"] = cluster_id
        except Exception as db_err:
            print(f"Failed to save cluster in DB: {db_err}")

        # 4. Write audit log & system metrics
        try:
            audit_payload = {
                "issue_id": issue_id,
                "risk_level": result["risk_level"],
                "decision": result["decision"],
                "confidence": result["confidence"],
                "causal_hypothesis": result["causal_hypothesis"],
                "knowledge_version": "v1.4",
                "policy_version": "v1.4",
                "llm_model": "gemini-2.5-pro",
                "embedding_model": "text-embedding-004",
                "decision_trace": json.dumps({
                    "trace": result["decision_trace"],
                    "context": {
                        "zone": context.zone.__dict__ if context.zone else None,
                        "weather": context.weather.__dict__ if context.weather else None,
                        "nearest_assets": [a.__dict__ for a in context.nearest_assets],
                        "historical_cases": [{
                            "id": h.id,
                            "category": h.category,
                            "incident_outcome": h.incident_outcome,
                            "similarity": h.similarity,
                            "distance": h.distance,
                            "retrieval_score": h.retrieval_score,
                            "resolution_summary": h.resolution_summary
                        } for h in context.historical_cases]
                    }
                })
            }
            supabase_client.table("decision_audit").update(audit_payload).eq("issue_id", issue_id).execute()
            if on_step_callback:
                await on_step_callback("Synthesis", f"Updated final decision audit for issue {issue_id}.")
        except Exception as aud_err:
            print(f"Failed to update decision audit record: {aud_err}")

        try:
            total_latency = int((time.time() - start_time) * 1000)
            metrics_payload = {
                "issue_id": issue_id,
                "latency_ms": total_latency,
                "llm_calls": llm_calls_count,
                "token_usage": token_usage,
                "cache_hit": False,
                "fallback_used": fallback_used,
                "reasoning_depth": len(result["decision_trace"]),
                "reasoning_steps": [t["summary"] for t in result["decision_trace"]]
            }
            supabase_client.table("system_metrics").insert(metrics_payload).execute()
        except Exception as met_err:
            print(f"Failed to log system metrics: {met_err}")

        return result
