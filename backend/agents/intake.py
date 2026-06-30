import json
from PIL import Image
import io
from backend.agents.gemini_client import get_gemini_model, gemini_call_rate_limited
from backend.agents.schemas import IntakeResponse

class IntakeAgent:
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

    async def classify_report(self, image_bytes: bytes, user_description: str = "") -> dict:
        """
        Uses Gemini to classify the civic issue. Falls back to keyword-based heuristics if quota is exceeded.
        """
        try:
            processed_bytes, success = self._process_image(image_bytes)
            
            image_payload = {
                "mime_type": "image/jpeg",
                "data": processed_bytes
            }
            
            prompt = f"""
            You are the CivicMind Intake Agent. Analyze the attached image and description of a civic infrastructure issue.
            User Description: "{user_description}"
            
            Determine if the image/report is a valid civic infrastructure or municipal issue (e.g., potholes, leaks, garbage, streetlights, sidewalk subsidence, damaged public property).
            Set "is_civic_issue" to true if it is a civic/public issue, and false if it is unrelated (e.g. food pictures, pets, private indoor rooms, text-only spam, irrelevant memes).

            Define the severity using this strict rubric:
            1 = Cosmetic issue (minor visual defect, no functional impact)
            2 = Minor inconvenience (nuisance, but no structural or safety threat)
            3 = Requires attention (noticeable degradation, needs monitoring/repairs soon)
            4 = Dangerous (poses immediate structural hazard or vehicle damage risk)
            5 = Critical public safety risk (active hazard causing immediate danger to lives or critical systems)

            Classify and return a strict JSON object matching the IntakeResponse schema:
            {{
                "category": "Pothole" | "Water Leak" | "Pavement Subsidence" | "Garbage Pile" | "Broken Streetlight" | "Other",
                "severity": integer (1-5),
                "area_affected_m2": float,
                "infrastructure_type": "string",
                "confidence": float,
                "summary": "Brief 1-sentence summary",
                "is_civic_issue": boolean
            }}
            """
            
            response = await gemini_call_rate_limited(
                self.model,
                contents=[image_payload, prompt],
                generation_config={"response_mime_type": "application/json"}
            )
            
            parsed = IntakeResponse.model_validate_json(response.text)
            res_dict = parsed.model_dump()
            if res_dict.get("confidence", 1.0) < 0.5:
                res_dict["is_civic_issue"] = False
            return res_dict
            
        except Exception as e:
            print(f"Intake Agent Gemini call failed (exceeded quota/rate limit): {e}. Running local mock fallback.")
            
            # Intelligent Local Mock Fallback based on description keywords
            desc_lower = user_description.lower()
            category = "Other"
            severity = 3
            infra = "Unknown"
            summary = "Issue reported in municipal sector."
            is_civic = True

            NON_CIVIC_OBJECTS = ["laptop", "computer", "keyboard", "phone", "monitor", "food", "dog", "cat", "person", "selfie", "pizza", "coffee"]

            # If user explicitly submits something clearly non-civic (food, cat, etc.)
            desc_words = set(desc_lower.replace(".", " ").replace(",", " ").split())
            if any(x in desc_words for x in NON_CIVIC_OBJECTS):
                is_civic = False
                summary = "Non-civic submission detected (contains private/unrelated content)."

            if is_civic:
                clean_desc = user_description.strip()
                desc_summary = clean_desc if len(clean_desc) < 70 else f"{clean_desc[:67]}..."
                
                if "leak" in desc_lower or "water" in desc_lower or "pipe" in desc_lower:
                    category = "Water Leak"
                    severity = 4 if "burst" in desc_lower or "flooding" in desc_lower else 3
                    infra = "water pipe"
                    summary = f"Water leak detected: {desc_summary}" if clean_desc else "Water leakage observed rising from sub-surface pipes."
                elif "light" in desc_lower or "lamp" in desc_lower or "dark" in desc_lower:
                    category = "Broken Streetlight"
                    severity = 3 if "flicker" in desc_lower else 4
                    infra = "streetlight fixture"
                    summary = f"Streetlight issue: {desc_summary}" if clean_desc else "Streetlight fixture is reported flickering or non-functional."
                elif "garbage" in desc_lower or "trash" in desc_lower or "dumpster" in desc_lower or "waste" in desc_lower:
                    category = "Garbage Pile"
                    severity = 3
                    infra = "waste container"
                    summary = f"Garbage overflow: {desc_summary}" if clean_desc else "Overflowing garbage container creating sanitary issues."
                elif "pothole" in desc_lower or "road" in desc_lower or "street" in desc_lower:
                    category = "Pothole"
                    severity = 4 if "deep" in desc_lower or "danger" in desc_lower else 3
                    infra = "road"
                    summary = f"Pothole report: {desc_summary}" if clean_desc else "Medium to large size pothole detected on asphalt road surface."
                elif "subsidence" in desc_lower or "sink" in desc_lower or "sunk" in desc_lower:
                    category = "Pavement Subsidence"
                    severity = 5 if "deep" in desc_lower else 4
                    infra = "road/sidewalk foundation"
                    summary = f"Subsidence report: {desc_summary}" if clean_desc else "Structural pavement depression and sub-base failure detected."
            
            fallback_data = {
                "category": category,
                "severity": severity,
                "area_affected_m2": 2.5 if is_civic else 0.0,
                "infrastructure_type": infra,
                "confidence": 0.9,
                "summary": f"[Local Triage Output] {summary}",
                "is_civic_issue": is_civic
            }
            # Validate fallback data as well to ensure type correctness
            parsed = IntakeResponse.model_validate(fallback_data)
            return parsed.model_dump()
