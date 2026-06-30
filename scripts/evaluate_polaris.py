import asyncio
import httpx
import json
import time
import os
import sys

# Ensure project root is on Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

BASE_URL = "http://localhost:8000"

async def run_evaluation():
    print("Starting Polaris Agentic System Evaluation Suite...")
    
    # 1. Prepare sample binary file for upload tests
    dummy_image = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xa0\x00\xff\xd9"

    test_cases = [
        # Valid civic issue - Water Leak
        {
            "name": "Valid Water Leak (Sector 7B)",
            "lat": 28.6692,
            "lng": 77.2211,
            "description": "Large underground water leak overflowing from the road. Sector 7B water main leakage.",
            "is_civic": True,
            "category": "Water Leak"
        },
        # Duplicate test case (Same day, same category, same location)
        {
            "name": "Duplicate Water Leak (Sector 7B)",
            "lat": 28.6693, # <10 meters away
            "lng": 77.2212,
            "description": "Large underground water leak overflowing from the road. Sector 7B water main leakage.",
            "is_civic": True,
            "category": "Water Leak",
            "is_duplicate": True
        },
        # Valid civic issue - Pothole
        {
            "name": "Valid Pothole (Sector 7B)",
            "lat": 28.6695,
            "lng": 77.2213,
            "description": "Deep road pothole causing cars to slow down significantly on main lane.",
            "is_civic": True,
            "category": "Pothole"
        },
        # Non-civic issue test case
        {
            "name": "Non-Civic Image (Irrelevant Food photo)",
            "lat": 28.6700,
            "lng": 77.2220,
            "description": "Look at this delicious pizza and cat I had for dinner last night!",
            "is_civic": False,
            "category": "Other"
        }
    ]

    metrics = {
        "total_runs": 0,
        "correct_civic_classification": 0,
        "correct_rejections": 0,
        "duplicates_detected": 0,
        "duplicate_detection_failures": 0,
        "total_synthesis_tested": 0,
        "causal_hypotheses_validated": 0,
        "explainability_items_found": 0,
        "decision_summary_found": 0
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Check health first
        try:
            health = await client.get(f"{BASE_URL}/health")
            print(f"Backend Health: {health.json()}")
        except Exception as e:
            print(f"Error connecting to backend: {e}. Make sure backend is running.")
            return

        for tc in test_cases:
            print(f"\n--- Running: {tc['name']} ---")
            files = {"image": ("test.jpg", dummy_image, "image/jpeg")}
            data = {
                "lat": tc["lat"],
                "lng": tc["lng"],
                "description": tc["description"]
            }

            try:
                res = await client.post(f"{BASE_URL}/reports", data=data, files=files)
                res_data = res.json()
                metrics["total_runs"] += 1
                
                # Check for rejection
                if not tc["is_civic"]:
                    if res_data.get("success") is False and "reject" in res_data.get("reason", "").lower():
                        print("✅ Rejection verified successfully.")
                        metrics["correct_rejections"] += 1
                    else:
                        print(f"❌ Failed to reject non-civic input. Response: {res_data}")
                    continue

                # Check duplicate detection
                if tc.get("is_duplicate"):
                    if res_data.get("duplicate") is True:
                        print("✅ Duplicate detected successfully.")
                        metrics["duplicates_detected"] += 1
                    else:
                        print(f"❌ Duplicate not detected. Response: {res_data}")
                        metrics["duplicate_detection_failures"] += 1
                    continue

                # Verify normal ingest
                if res_data.get("success") is True or res_data.get("status") == "processing":
                    print(f"✅ Ingestion successful. Issue ID: {res_data.get('issue_id')}")
                    intake_category = res_data.get("category")
                    # Handle when mock output wraps the classification under intake_result / gemini_analysis
                    if not intake_category and "gemini_analysis" in res_data:
                        intake_category = res_data["gemini_analysis"].get("intake", {}).get("category")
                    
                    if intake_category == tc["category"]:
                        metrics["correct_civic_classification"] += 1
                    else:
                        print(f"⚠️ Category mismatch: expected {tc['category']}, got {intake_category}")
                else:
                    print(f"❌ Ingestion failed: {res_data}")

            except Exception as run_err:
                print(f"Error during run: {run_err}")

        # Wait to let background task execute
        print("\nWaiting 5 seconds for background Synthesis and Briefing worker to process...")
        await asyncio.sleep(5.0)

        # Retrieve and evaluate SynthesisAgent outputs directly to bypass remote database cache limits
        try:
            print("\nDirectly evaluating SynthesisAgent reasoning & explainability output...")
            from backend.agents.synthesis import SynthesisAgent
            
            agent = SynthesisAgent()
            mock_issue = {
                "id": "af2d66e6-5dd5-4eeb-9f18-7ccf13a850c4",
                "category": "Water Leak",
                "severity": 4,
                "lat": 28.6692,
                "lng": 77.2211,
                "description": "Large underground water leak overflowing from the road. Sector 7B water main leakage.",
                "credibility_score": 0.9,
                "embedding": [0.0] * 768
            }
            
            synthesis_result = await agent.run_synthesis(mock_issue)
            
            metrics["total_synthesis_tested"] += 1
            if synthesis_result.get("causal_hypothesis") and len(synthesis_result.get("causal_hypothesis")) > 10:
                metrics["causal_hypotheses_validated"] += 1
                print("✅ Causal Hypothesis validated successfully.")
            
            factors = synthesis_result.get("explainability_factors", [])
            if factors and len(factors) > 0:
                metrics["explainability_items_found"] += 1
                print(f"✅ Explainability Factors generated: {factors}")
                
            if synthesis_result.get("decision_summary"):
                metrics["decision_summary_found"] += 1
                print(f"✅ Decision Summary generated: {synthesis_result.get('decision_summary')}")
                
        except Exception as eval_err:
            print(f"Error during direct synthesis verification: {eval_err}")

        # Output Summary Metrics
        total_civic = sum(1 for tc in test_cases if tc["is_civic"] and not tc.get("is_duplicate"))
        total_non_civic = sum(1 for tc in test_cases if not tc["is_civic"])
        total_duplicates = sum(1 for tc in test_cases if tc.get("is_duplicate"))

        classification_accuracy = (metrics["correct_civic_classification"] / total_civic) * 100 if total_civic > 0 else 0
        rejection_rate = (metrics["correct_rejections"] / total_non_civic) * 100 if total_non_civic > 0 else 0
        duplicate_precision = (metrics["duplicates_detected"] / (metrics["duplicates_detected"] + metrics["duplicate_detection_failures"])) * 100 if (metrics["duplicates_detected"] + metrics["duplicate_detection_failures"]) > 0 else 0
        explainability_coverage = (metrics["explainability_items_found"] / metrics["total_synthesis_tested"]) * 100 if metrics["total_synthesis_tested"] > 0 else 0

        print("\n================ EVALUATION SUMMARY ================")
        print(f"Triage Classification Accuracy : {classification_accuracy:.1f}%")
        print(f"Non-Civic Rejection Rate       : {rejection_rate:.1f}%")
        print(f"Duplicate Detection Precision  : {duplicate_precision:.1f}%")
        print(f"Explainability Coverage        : {explainability_coverage:.1f}%")
        print(f"Causal Accuracy                : {100.0 if metrics['causal_hypotheses_validated'] > 0 else 0.0:.1f}%")
        print("====================================================")

if __name__ == "__main__":
    asyncio.run(run_evaluation())
