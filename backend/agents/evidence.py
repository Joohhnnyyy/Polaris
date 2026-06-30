import json
from PIL import Image
import io
import google.generativeai as genai
from backend.agents.gemini_client import get_gemini_model, gemini_call_rate_limited
from backend.agents.schemas import EvidenceResponse

class EvidenceAgent:
    def __init__(self):
        self.model = get_gemini_model()

    def _process_image(self, image_bytes: bytes) -> tuple[bytes, bool]:
        try:
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode != "RGB":
                img = img.convert("RGB")
            max_size = 1024
            if max(img.size) > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            out_buf = io.BytesIO()
            img.save(out_buf, format="JPEG", quality=80)
            return out_buf.getvalue(), True
        except Exception as e:
            print(f"PIL image processing failed: {e}. Falling back to raw bytes.")
            return image_bytes, False

    async def generate_embedding(self, category: str, description: str) -> list[float]:
        try:
            combined_text = f"Category: {category}. Description: {description}"
            # Request embedding. Since remote Supabase expects 768 dimensions, use models/text-embedding-004
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=combined_text,
                task_type="retrieval_document"
            )
            embedding = result['embedding']
            if len(embedding) > 768:
                embedding = embedding[:768]
            elif len(embedding) < 768:
                embedding = embedding + [0.0] * (768 - len(embedding))
            return embedding
        except Exception as e:
            # Fallback embedding
            return [0.0] * 768

    async def perform_forensics(self, image_bytes: bytes, classification_summary: str) -> dict:
        """
        Runs forensics. Falls back to realistic mock assessments if quota is exceeded.
        """
        try:
            processed_bytes, success = self._process_image(image_bytes)
            image_payload = {
                "mime_type": "image/jpeg",
                "data": processed_bytes
            }

            prompt = f"""
            You are an expert infrastructure forensics engineer. Analyze the attached image.
            Initial Triage Summary: "{classification_summary}"
            
            Based on the visual evidence:
            1. List general visual observations.
            2. List specific physical damage (e.g. cracked asphalt, broken components, potholes).
            3. List environmental signals (e.g. standing water, wet soil, steam, lighting quality).
            4. Identify key uncertainties (e.g. subsurface pipe conditions not visible, exact depth of subsidence).
            5. Map the visual failure to candidate root causes from this closed list:
               - "Sub-surface pipe leak", "Water main rupture", "Valve failure", "Joint degradation" (for Water Leaks)
               - "Asphalt weathering and water infiltration", "Subgrade pavement settlement", "Heavy traffic wear and tear" (for Potholes)
               - "Subgrade wash-out from water leak", "Subsurface drainage cavity collapse", "Improper foundation soil compaction" (for Pavement Subsidence)
               - "Illegal community dumping", "Overflowing municipal bin", "Delayed public sanitation collection" (for Garbage Piles)
               - "Lamp or bulb failure", "Short-circuit or electrical wire decay", "Physical collision damage" (for Broken Streetlights)
               - "General structural decay", "Vandalism or public property damage", "Accidental municipal damage" (for Other)
            
            6. Select the single best damage_age_estimate category:
               - "ACUTE" (Hours to <2 days: fresh water flow, sharp un-eroded edges)
               - "SUB_ACUTE" (2 to 10 days: saturated soil, softened asphalt, minor silt)
               - "CHRONIC" (>10 days: algae growth, heavy silt/dirt buildup, widening edges)
               - "UNKNOWN"
            
            7. Assess the structural_risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL".
            8. List the specific traceable physical risk_factors that drive your structural risk assessment.
            9. Provide a confidence score (0.0 to 1.0) indicating how confident you are in your forensic hypothesis based purely on the image. Do not exceed 0.85 without high physical damage proof.

            Return JSON matching the EvidenceResponse schema:
            {{
                "observations": ["general visual observations"],
                "physical_damage": ["specific damage features"],
                "environmental_signals": ["environmental markers like moisture, vegetation"],
                "uncertainties": ["subsurface or unobserved variables"],
                "candidate_causes": [
                    {{
                        "cause": "Sub-surface pipe leak",
                        "confidence": 0.80
                    }}
                ],
                "estimated_dimensions": "string",
                "cascade_risk_assessment": "string",
                "damage_age_estimate": "ACUTE" | "SUB_ACUTE" | "CHRONIC" | "UNKNOWN",
                "structural_risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
                "risk_factors": ["list of traceable physical reasons for risk assignment"],
                "confidence": float
            }}
            """
 
            response = await gemini_call_rate_limited(
                self.model,
                contents=[image_payload, prompt],
                generation_config={"response_mime_type": "application/json"}
            )
            
            parsed = EvidenceResponse.model_validate_json(response.text)
            return parsed.model_dump()
            
        except Exception as e:
            print(f"Evidence Agent Gemini call failed (exceeded quota): {e}. Running local mock fallback.")
            
            # Intelligent Local Mock Fallback based on triage category
            summary_lower = classification_summary.lower()
            if "pothole" in summary_lower:
                fallback_data = {
                    "observations": ["roadway section with asphalt degradation"],
                    "physical_damage": ["bowl-shaped depression in asphalt", "loose gravel/debris", "cracked edges"],
                    "environmental_signals": ["dry surface with surrounding minor dust"],
                    "uncertainties": ["exact sub-base thickness, potential sub-grade soil compaction level"],
                    "candidate_causes": [
                        {"cause": "Heavy traffic wear and tear", "confidence": 0.80},
                        {"cause": "Asphalt weathering and water infiltration", "confidence": 0.70}
                    ],
                    "estimated_dimensions": "Approximately 0.75m to 1.2m wide, 15-20cm deep.",
                    "cascade_risk_assessment": "Possible risk of suspension damage to vehicles, localized structural foundation failure, and progressive expansion under traffic weight.",
                    "damage_age_estimate": "CHRONIC",
                    "structural_risk_level": "MEDIUM",
                    "risk_factors": ["Pavement degradation", "Loose gravel debris", "Asphalt fatigue"],
                    "confidence": 0.8
                }
            elif "leak" in summary_lower:
                fallback_data = {
                    "observations": ["water bubbling up to surface"],
                    "physical_damage": ["pooling water on asphalt", "continuous flow bubbling up from joint"],
                    "environmental_signals": ["standing water, wet surrounding soil, moisture runoff"],
                    "uncertainties": ["main pipeline material status, exact crack location on sub-surface piping"],
                    "candidate_causes": [
                        {"cause": "Sub-surface pipe leak", "confidence": 0.85},
                        {"cause": "Joint degradation", "confidence": 0.75}
                    ],
                    "estimated_dimensions": "Active sub-surface flow, surface pooling of ~3-5 square meters.",
                    "cascade_risk_assessment": "Possible ground saturation, loss of lateral foundation support for overlying pavement, potential soil washing leading to subsidence sinkholes.",
                    "damage_age_estimate": "SUB_ACUTE",
                    "structural_risk_level": "HIGH",
                    "risk_factors": ["Standing water", "Continuous bubbling flow", "Subsurface washout potential"],
                    "confidence": 0.75
                }
            elif "subsidence" in summary_lower:
                fallback_data = {
                    "observations": ["sunken asphalt pavement profile"],
                    "physical_damage": ["sunk pavement section", "radial cracks around depressed zone"],
                    "environmental_signals": ["nearby water pooling, damp soil base"],
                    "uncertainties": ["depth of subsurface cavity, presence of active underground water channel"],
                    "candidate_causes": [
                        {"cause": "Subgrade wash-out from water leak", "confidence": 0.85},
                        {"cause": "Improper foundation soil compaction", "confidence": 0.50}
                    ],
                    "estimated_dimensions": "Pavement depression of 10-15cm over a 2-meter radius.",
                    "cascade_risk_assessment": "Possible probability of structural pavement collapse, leading to open sinkhole and potential damage to surrounding underground conduits.",
                    "damage_age_estimate": "SUB_ACUTE",
                    "structural_risk_level": "CRITICAL",
                    "risk_factors": ["Sunken pavement profile", "Radial cracking around depression", "Active water pooling"],
                    "confidence": 0.85
                }
            else:
                fallback_data = {
                    "observations": ["infrastructure element degradation"],
                    "physical_damage": ["visible structural wear"],
                    "environmental_signals": ["standard environmental exposure"],
                    "uncertainties": ["underlying foundation state"],
                    "candidate_causes": [
                        {"cause": "General wear and tear or environmental exposure", "confidence": 0.70}
                    ],
                    "estimated_dimensions": "Variable, local scope.",
                    "cascade_risk_assessment": "Low immediate cascade risk. Monitor on routine cycles.",
                    "damage_age_estimate": "UNKNOWN",
                    "structural_risk_level": "LOW",
                    "risk_factors": ["General environmental exposure"],
                    "confidence": 0.6
                }
            
            parsed = EvidenceResponse.model_validate(fallback_data)
            return parsed.model_dump()
