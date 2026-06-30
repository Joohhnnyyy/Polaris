from backend.models.models import KnowledgeContext

class ContextBuilder:
    def build_llm_context(self, context: KnowledgeContext) -> str:
        # Formats the typed KnowledgeContext into structured prompt instructions
        lines = []
        lines.append("=== MUNICIPAL KNOWLEDGE CONTEXT ===")
        
        # 1. Target Issue
        issue = context.issue
        lines.append(f"Target Report Category: {issue.category}")
        lines.append(f"Target Severity: {issue.severity}/5")
        lines.append(f"Target Coordinates: ({issue.lat:.5f}, {issue.lng:.5f})")

        # 2. Zone Information
        if context.zone:
            lines.append(f"Resolved Administrative Zone: {context.zone.name}")
            lines.append(f"Zone Soil Type: {context.zone.soil_type}")
        else:
            lines.append("Resolved Administrative Zone: Unknown")

        # 3. Weather
        if context.weather:
            lines.append(f"Current Local Weather: {context.weather.weather_condition}")
            lines.append(f"Rain Accumulation (1h): {context.weather.rain_accumulation_mm} mm")
            lines.append(f"Temperature: {context.weather.temperature_c}°C (Source: {context.weather.source})")

        # 4. Nearest Infrastructure Assets
        lines.append("\n--- Nearby Infrastructure Assets (selective retrieval) ---")
        if context.nearest_assets:
            for idx, asset in enumerate(context.nearest_assets, 1):
                lines.append(f"{idx}. Asset ID: {asset.id} | Type: {asset.asset_type} | Material: {asset.material} | Condition: {asset.condition_score}/10 | Distance: {asset.distance_m:.1f} meters | Status: {asset.status}")
        else:
            lines.append("No proximate utility assets resolved in database.")

        # 5. Historical Incidents
        lines.append("\n--- Semantically Similar Historical Cases (retrieval ranking) ---")
        if context.historical_cases:
            for idx, inc in enumerate(context.historical_cases, 1):
                lines.append(f"{idx}. ID: {inc.id} | Outcome: {inc.incident_outcome} | Risk: {inc.risk_level} | Causal Confidence: {inc.confidence} | Distance: {inc.distance:.1f}m | Similarity: {inc.similarity:.3f} | Score: {inc.retrieval_score:.3f} | Summary: {inc.resolution_summary}")
        else:
            lines.append("No similar historical records returned in project memory.")

        # 6. Active Municipal Policies
        lines.append("\n--- Applicable Municipal Policies ---")
        if context.policies:
            for idx, p in enumerate(context.policies, 1):
                lines.append(f"{idx}. Policy: {p.rule_name} | Escalation: {p.escalation_department} | Max response: {p.max_response_time_hours} hours | Requires Human: {p.requires_human}")
        else:
            lines.append("Using standard default dispatch policy.")

        # 7. Root Cause Library
        lines.append("\n--- Allowed Causal Mappings (Root Cause Library) ---")
        if context.root_causes:
            for idx, rc in enumerate(context.root_causes, 1):
                lines.append(f"{idx}. Root Cause ID: {rc.id} | Cause: {rc.cause} | Base Prior: {rc.prior} | Requires observations: {', '.join(rc.evidence_required)}")
        else:
            lines.append("Standard physical failure propagation library active.")

        return "\n".join(lines)
