import asyncio
import csv
import os
import sys
import time
import json
import statistics
import math

# Ensure project root is on Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.agents.synthesis import SynthesisAgent

CSV_OUTPUT_PATH = "/Users/anshjohnson/Polaris/urban_autopsy_benchmark_results.csv"

# Helper to grade explainability detail (0.0 to 1.0)
def grade_explainability_quality(factors):
    if not factors:
        return 0.0
    detailed_count = 0
    # Detailed factors should have specific metrics (numbers, distances, days, etc.)
    for f in factors:
        f_lower = f.lower()
        has_number = any(char.isdigit() for char in f)
        has_specific_words = any(w in f_lower for w in ["meter", "day", "year", "leak", "saturation", "corrosion", "age", "m2"])
        if has_number or has_specific_words:
            detailed_count += 1
    return round(detailed_count / len(factors), 2)

# Helper to grade decision summary clarity (0.0 to 1.0)
# Answers: 1) What happened? 2) Why was risk elevated? 3) What evidence was used?
def grade_decision_summary(summary):
    if not summary:
        return 0.0
    summary_lower = summary.lower()
    score = 0
    # 1. Did it describe what happened (leak, damage, defect, failure)?
    if any(w in summary_lower for w in ["leak", "pothole", "subsidence", "street", "garbage", "failure", "decay"]):
        score += 1
    # 2. Did it explain risk elevation (risk, elevate, critical, severity, danger)?
    if any(w in summary_lower for w in ["risk", "elevat", "critical", "severity", "danger", "threat", "hazard"]):
        score += 1
    # 3. Did it list evidence (evidence, historical, report, leak, proximity, logic)?
    if any(w in summary_lower for w in ["evidence", "history", "report", "pipeline", "traffic", "underground"]):
        score += 1
    return round(score / 3.0, 2)

# Generate 50 synthetic scenarios
def generate_scenarios():
    scenarios = []
    
    # 20 Water Line Failures (Water Leak + Pavement Subsidence + Pothole)
    for i in range(20):
        scenarios.append({
            "id": f"Water_Failure_{i+1}",
            "type": "Water Line Failure",
            "issues": [
                {"id": f"leak_{i}", "category": "Water Leak", "severity": 4, "lat": 28.6692, "lng": 77.2211, "description": "Water main leak bubbling up through pavement near market", "credibility_score": 0.9, "verification_votes": 6, "dispute_votes": 1},
                {"id": f"sub_{i}", "category": "Pavement Subsidence", "severity": 3, "lat": 28.6693, "lng": 77.2212, "description": "Depression on road pavement", "credibility_score": 0.8, "verification_votes": 3, "dispute_votes": 0},
                {"id": f"pot_{i}", "category": "Pothole", "severity": 3, "lat": 28.6691, "lng": 77.2210, "description": "Severe pothole right next to the puddle", "credibility_score": 0.85, "verification_votes": 2, "dispute_votes": 0}
            ],
            "expected_causal": True,
            "expected_root_cause": "Pipe/Water Line Failure"
        })
        
    # 15 Streetlight/Electrical Faults (Streetlight + Other/Electrical Box)
    for i in range(15):
        scenarios.append({
            "id": f"Electrical_Fault_{i+1}",
            "type": "Electrical Fault",
            "issues": [
                {"id": f"light_{i}", "category": "Broken Streetlight", "severity": 3, "lat": 28.5412, "lng": 77.3345, "description": "Broken streetlight flicking off near Sector 12 sub-station", "credibility_score": 0.85, "verification_votes": 4, "dispute_votes": 0},
                {"id": f"box_{i}", "category": "Other", "severity": 4, "lat": 28.5413, "lng": 77.3346, "description": "Exposed electrical box wiring sparking", "credibility_score": 0.9, "verification_votes": 5, "dispute_votes": 0}
            ],
            "expected_causal": True,
            "expected_root_cause": "Electrical Fault"
        })

    # 15 No Causal Link (Garbage Pile + Broken Streetlight)
    for i in range(15):
        scenarios.append({
            "id": f"No_Link_{i+1}",
            "type": "No Causal Link",
            "issues": [
                {"id": f"trash_{i}", "category": "Garbage Pile", "severity": 3, "lat": 28.6692, "lng": 77.2211, "description": "Illegal municipal garbage heap on corner in Sector 7B", "credibility_score": 0.9, "verification_votes": 1, "dispute_votes": 0},
                {"id": f"light_{i}", "category": "Broken Streetlight", "severity": 2, "lat": 28.6737, "lng": 77.2211, "description": "Flickering streetlight bulb far away", "credibility_score": 0.8, "verification_votes": 2, "dispute_votes": 0}
            ],
            "expected_causal": False,
            "expected_root_cause": "No Link"
        })

    return scenarios

async def run_benchmark():
    print("Initializing Urban Autopsy AI Reasoning & Calibration Benchmark (50 Scenarios)...")
    agent = SynthesisAgent()
    scenarios = generate_scenarios()
    
    results = []
    
    # Validation metrics
    causal_accuracies = []
    root_cause_accuracies = []
    hallucination_indicators = []
    brier_elements = []
    
    explainability_scores = []
    summary_clarity_scores = []

    for sc in scenarios:
        start_time = time.time()
        primary_issue = sc["issues"][0]
        primary_issue["embedding"] = [0.0] * 768  # mock embedding
        
        # Run Synthesis Agent directly on primary issue
        try:
            res = await agent.run_synthesis(primary_issue)
            latency = (time.time() - start_time) * 1000
            
            # 1. Evaluate Causal Accuracy
            # We predict causal if the decision is CONFIDENT or UNCERTAIN and evidence chain contains > 1 issue
            predicted_causal = res.get("decision") in ["CONFIDENT", "UNCERTAIN"] and len(res.get("evidence_chain_issue_ids", [])) > 1
            causal_correct = predicted_causal == sc["expected_causal"]
            causal_accuracies.append(1 if causal_correct else 0)
            
            # 2. Evaluate Root Cause Accuracy
            hypothesis = res.get("causal_hypothesis", "").lower()
            if sc["type"] == "Water Line Failure":
                root_correct = any(w in hypothesis for w in ["water", "leak", "pipe", "line", "drainage", "saturation"])
            elif sc["type"] == "Electrical Fault":
                root_correct = any(w in hypothesis for w in ["electrical", "power", "wire", "light", "conduit", "spark"])
            else:
                # No Causal Link expected
                root_correct = "no validated causal pathway" in hypothesis or "insufficient" in hypothesis or "no link" in hypothesis or len(res.get("evidence_chain_issue_ids", [])) <= 1 or res.get("decision") == "INSUFFICIENT_EVIDENCE"
            root_cause_accuracies.append(1 if root_correct else 0)
            
            # 3. Evaluate Hallucination Indicators
            hallucinated = False
            if sc["type"] == "No Causal Link" and predicted_causal:
                hallucinated = True
            hallucination_indicators.append(1 if hallucinated else 0)
            
            # 4. Calibration & Brier Score Element
            forecast = res.get("confidence", 0.5)
            actual = 1.0 if sc["expected_causal"] else 0.0
            brier_elements.append((forecast - actual) ** 2)
            
            # 5. Explainability & Decision Summary Quality Audits
            exp_quality = grade_explainability_quality(res.get("explainability_factors", []))
            explainability_scores.append(exp_quality)
            
            summary_clarity = grade_decision_summary(res.get("decision_summary", ""))
            summary_clarity_scores.append(summary_clarity)
            
            results.append({
                "scenario_id": sc["id"],
                "type": sc["type"],
                "expected_causal": sc["expected_causal"],
                "predicted_causal": predicted_causal,
                "causal_correct": causal_correct,
                "expected_root_cause": sc["expected_root_cause"],
                "actual_causal_hypothesis": res.get("causal_hypothesis"),
                "root_cause_correct": root_correct,
                "hallucinated": hallucinated,
                "confidence": forecast,
                "decision": res.get("decision", "CONFIDENT"),
                "risk_level": res.get("risk_level", "LOW"),
                "vision_confidence": res.get("confidence_sources", {}).get("vision", 0.0),
                "similarity_confidence": res.get("confidence_sources", {}).get("similarity", 0.0),
                "historical_confidence": res.get("confidence_sources", {}).get("historical", 0.0),
                "causal_prior_confidence": res.get("confidence_sources", {}).get("causal_prior", 0.0),
                "explainability_quality": exp_quality,
                "summary_clarity": summary_clarity,
                "latency_ms": round(latency, 1)
            })
            
            print(f"Scenario {sc['id']}: Causal Correct: {causal_correct} | Root Cause Correct: {root_correct} | Hallucinated: {hallucinated} | Decision: {res.get('decision')} | Latency: {latency:.1f}ms")
            
        except Exception as e:
            print(f"Failed executing scenario {sc['id']}: {e}")

    # Compute Final Statistics
    total_runs = len(results)
    if total_runs > 0:
        overall_causal_accuracy = (sum(causal_accuracies) / total_runs) * 100
        overall_root_cause_accuracy = (sum(root_cause_accuracies) / total_runs) * 100
        hallucination_rate = (sum(hallucination_indicators) / total_runs) * 100
        brier_score = sum(brier_elements) / total_runs
        
        # Calibration error (simplified absolute difference)
        calibration_error = statistics.mean([abs(r["confidence"] - (1 if r["expected_causal"] else 0)) for r in results])
        
        # Precision, Recall, F1 for Causal Classification
        tp = sum(1 for r in results if r["expected_causal"] and r["predicted_causal"])
        fp = sum(1 for r in results if not r["expected_causal"] and r["predicted_causal"])
        fn = sum(1 for r in results if r["expected_causal"] and not r["predicted_causal"])
        tn = sum(1 for r in results if not r["expected_causal"] and not r["predicted_causal"])
        
        precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0
        recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        avg_explainability_quality = statistics.mean(explainability_scores) * 100
        avg_summary_clarity = statistics.mean(summary_clarity_scores) * 100
        
        # Abstention Rate (how often does it correctly abstain when expected causal is False)
        expected_abstain = sum(1 for r in results if not r["expected_causal"])
        actual_abstain = sum(1 for r in results if not r["expected_causal"] and r["decision"] in ["INSUFFICIENT_EVIDENCE", "UNCERTAIN"])
        abstention_rate = (actual_abstain / expected_abstain * 100) if expected_abstain > 0 else 0.0

        # False Escalation Rate (HIGH/CRITICAL risks assigned when expected causal is False)
        false_escalations = sum(1 for r in results if not r["expected_causal"] and r["risk_level"] in ["HIGH", "CRITICAL"])
        false_escalation_rate = (false_escalations / expected_abstain * 100) if expected_abstain > 0 else 0.0

        # Bucketed Confidence Calibration analysis
        buckets = {
            "90-100": {"count": 0, "correct": 0},
            "80-90": {"count": 0, "correct": 0},
            "70-80": {"count": 0, "correct": 0},
            "below-70": {"count": 0, "correct": 0}
        }
        for r in results:
            conf = r["confidence"]
            is_correct = r["causal_correct"]
            if conf >= 0.90:
                buckets["90-100"]["count"] += 1
                if is_correct: buckets["90-100"]["correct"] += 1
            elif conf >= 0.80:
                buckets["80-90"]["count"] += 1
                if is_correct: buckets["80-90"]["correct"] += 1
            elif conf >= 0.70:
                buckets["70-80"]["count"] += 1
                if is_correct: buckets["70-80"]["correct"] += 1
            else:
                buckets["below-70"]["count"] += 1
                if is_correct: buckets["below-70"]["correct"] += 1

        print("\n================ BENCHMARK SUMMARY ================")
        print(f"Total Scenarios Evaluated   : {total_runs}")
        print(f"Causal Accuracy             : {overall_causal_accuracy:.1f}%")
        print(f"Root Cause Accuracy         : {overall_root_cause_accuracy:.1f}%")
        print(f"Hallucination Rate          : {hallucination_rate:.1f}%")
        print(f"Decision Abstention Rate    : {abstention_rate:.1f}%")
        print(f"False Escalation Rate       : {false_escalation_rate:.1f}%")
        print(f"Brier Score                 : {brier_score:.3f}")
        print(f"Calibration Error           : {calibration_error:.3f}")
        print(f"Precision                   : {precision:.1f}%")
        print(f"Recall                      : {recall:.1f}%")
        print(f"F1 Score                    : {f1:.1f}%")
        print(f"Avg Explainability Quality  : {avg_explainability_quality:.1f}%")
        print(f"Avg Decision Summary Clarity: {avg_summary_clarity:.1f}%")
        print("\n--- Bucket Calibration Analysis ---")
        for bucket, data in buckets.items():
            count = data["count"]
            acc = (data["correct"] / count * 100) if count > 0 else 0.0
            print(f"Bucket {bucket}% Confidence: {count} runs | Accuracy: {acc:.1f}%")
        print("====================================================")
        
        # Save results to CSV
        fields = results[0].keys()
        with open(CSV_OUTPUT_PATH, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(results)
        print(f"Benchmark results written successfully to {CSV_OUTPUT_PATH}")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
