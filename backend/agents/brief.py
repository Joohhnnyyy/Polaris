import json
from backend.agents.gemini_client import get_gemini_model, gemini_call_rate_limited
from backend.agents.schemas import BriefResponse

class BriefAgent:
    def __init__(self):
        # Brief agent uses Gemini 2.5 Flash to write structured communication drafts
        self.model = get_gemini_model("gemini-2.5-flash")

    async def generate_brief(self, zone_id: str, risk_level: str, causal_hypothesis: str, affected_residents: int) -> dict:
        """
        Generates a professional email briefing to dispatch to city engineers.
        """
        try:
            prompt = f"""
            You are the CivicMind Brief Agent. Your task is to draft a professional, action-oriented email notification to dispatch to municipal engineers.
            
            Details:
            - Zone: {zone_id}
            - Risk Level: {risk_level}
            - Causal Hypothesis: {causal_hypothesis}
            - Affected Residents: {affected_residents}
            
            Return JSON matching the BriefResponse schema:
            {{
                "subject": "string email subject line starting with [CivicMind Urgent] or similar",
                "email_body": "string full formatted professional body of the email brief to dispatch. Include greeting, warning details, causal assessment, and recommendation to deploy preventative resources."
            }}
            """
            
            response = await gemini_call_rate_limited(
                self.model,
                contents=prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            parsed = BriefResponse.model_validate_json(response.text)
            return parsed.model_dump()
            
        except Exception as e:
            print(f"Brief Agent Gemini call failed (exceeded quota): {e}. Running local mock fallback.")
            
            fallback_subject = f"[CivicMind Urgent] {risk_level} Infrastructure Threat in {zone_id}"
            fallback_body = f"""Dear Ward Engineer,

CivicMind has identified a {risk_level} infrastructure failure risk in {zone_id}.

Causal Hypothesis:
{causal_hypothesis}

Impact Assessment:
Approximately {affected_residents} residents are estimated to be affected by this potential system failure.

Preventive action is recommended immediately.

Best regards,
CivicMind Urban Triage System"""
            
            fallback_data = {
                "subject": fallback_subject,
                "email_body": fallback_body
            }
            parsed = BriefResponse.model_validate(fallback_data)
            return parsed.model_dump()
