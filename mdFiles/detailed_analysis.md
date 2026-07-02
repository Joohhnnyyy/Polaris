# Polaris: The Urban Autopsy Engine
*Multi-Agent Infrastructure Intelligence & Autonomous Municipal Response*

---

## Executive Summary
* **Core Objective**: Transforms reactive municipal maintenance into a proactive forensic intelligence operation.
* **Integration**: Combines multi-modal AI with real-time urban telemetry for identification and diagnosis.
* **Impact**: Reduces triage latency from days to seconds by automating civic infrastructure repair dispatch.

Autonomous multi-agent urban infrastructure intelligence system for parsing civic issues and generating municipal officer briefings.

* **Submitted By**: Ansh Johnson
* **Submission Date**: June 30, 2026
* **Project Track**: Community Hero - Hyperlocal Problem Solver

---

## Project Vision
* **Urban Resilience**: Redefines municipal response by addressing fragmented reporting and silent decay.
* **Multi-Agent Framework**: Converts citizen telemetry into actionable forensic briefs via computer vision and GIS fusion.
* **Root-Cause Diagnosis**: Utilizes utility registries and historical records to prevent minor defects from escalating.

---

## 1. System Architecture & Data Flow
Polaris utilizes a **State-Sharing Sequential Pipeline** coordinated by a central orchestrator. Data flows through a pipeline where each agent enhances the core incident profile, culminating in a synthesized root-cause hypothesis and dispatch brief.

```
[Citizen Report] -> (Intake Agent) -> [Triage & Severity Evaluation]
                          |
                          v
                   (Evidence Agent) -> [Visual Forensics & Embeddings]
                          |
                          v
                  (Synthesis Agent) <-> [Supabase Vector Database (PgVector)]
                          |
                          v
                    [Risk Cluster Creation & Cost Analysis]
                          |
                          v
                    (Brief Agent) -> [Dispatch Brief Draft]
```

### Technical Highlights
* **Urban Autopsy Engine**: Automated forensic investigation of infrastructure anomalies.
* **Multi-Modal Fusion**: Concurrent analysis of visual evidence, GIS telemetry, and environmental data.
* **Autonomous Triage**: Instantaneous department-routed dispatch logic based on unified risk assessment.

### Core Operations
1. **State Representation**: The incident state is represented by a structured `KnowledgeContext` Pydantic model that accumulates metadata.
2. **Coordination**: A FastAPI backend orchestrator schedules task execution across the agentic layers.
3. **Communication Layer**: Agents communicate asynchronously by modifying the shared `KnowledgeContext` stored in memory, which is committed at key checkpoints (Intake, Evidence, and Synthesis) to a Supabase database.
4. **Real-Time Monitoring**: Progress is serialized and pushed via WebSockets to a local frontend for immediate visual feedback.

---

## 2. Technology Stack & Agent Summary

| Component | Primary Technology | Database / Source | Key Output |
| :--- | :--- | :--- | :--- |
| **Intake Agent** | Gemini 2.5 Flash | `issues` (Write) | Spam filtering, Category, Severity |
| **Evidence Agent** | Gemini 2.5 Flash | `issues` (Update) | Physical damage markers, Candidate cause |
| **MKS: Zone & Asset** | PostGIS / Supabase | `zones`, `assets` (Read) | Zone ID, nearest utility ID, asset age |
| **MKS: History** | pgvector (30-day window) | `historical_incidents` | Top 5 similar historical cases |
| **MKS: Weather** | OpenWeather API | External API | Rain accumulation, temp, soil state |
| **Synthesis Agent** | Gemini 2.5 Pro | `decision_audit` (Write) | Causal hypothesis, unified risk level |
| **Policy & Brief** | Local Rule Engine | `briefs` (Write) | Routing department, Dispatch Brief |

---

## 3. Deep-Dive Agent Breakdown

### 3.1 Intake Agent (The Gateway Filter)
* **Design Philosophy**: Boundary validation. Protects downstream analytical resources by filtering noise immediately.
* **Action**: Analyzes raw image bytes and description text to distinguish legitimate civic issues from spam or jokes.
* **Benefit**: Auto-resolves invalid submissions before they consume municipal processing time.

### 3.2 Evidence Agent (The Visual Forensic Expert)
* **Design Philosophy**: Quantitative visual diagnostics. Replaces subjective user descriptions with objective visual markers.
* **Action**: Identifies physical indicators such as "radial asphalt cracking" or "subgrade soil washout" with confidence scoring.
* **Benefit**: Crews arrive on-site with pre-diagnosed indicators, bypassing the initial diagnostic visit and speeding up repairs.

### 3.3 Municipal Knowledge Service (Context Fuser)
* **Design Philosophy**: System integration. Turns an isolated photo into a connected urban puzzle piece by overlaying GIS, weather, and historical telemetry.
* **Benefit**: Context-aware triage. The city can identify if a leak is occurring over a historical fault line, preventing catastrophic sinkholes.

### 3.4 Synthesis Agent (The Brain)
* **Design Philosophy**: Cognitive correlation. Generates the causal bridge linking visual surface indicators to subsurface infrastructure systems.
* **Input**: The accumulated `KnowledgeContext` (Intake + Evidence + GIS + Assets + Weather + History).
* **Benefit**: Provides administrators with a clear audit trail and a "why" behind every automated risk assessment.

---

## 4. Actionable Output Example
```
HIGH-PRIORITY INCIDENT REPORT: CASE 8cf0f647
DEPARTMENT: Water & Sewer Dept (Emergency Division)
URGENCY: IMMEDIATE DISPATCH REQUIRED
```
1. **Causal Hypothesis**: Heavy rain saturated clay soil in Sector 7B, accelerating roadway erosion. Surface bubbling water points to a subgrade pipe burst on Asset W-M14 (1980, Cast Iron).
2. **Physical Site Profile**: Lat: 28.6160, Lng: 77.2060; 12.5m² damage area; active bubbling and radial cracking observed.
3. **Recommendations**: Heavy excavation gear required (backhoe); replacement piping for 150mm cast iron main-line.
4. **Escalation**: Notify District Manager; shut off Valve V-99 immediately.

---

## 5. Operational Resiliency & Integrity
* **API Fallbacks**: If Gemini API quotas are exceeded, the system triggers a keyword-matching regex heuristic and tags the log with `MOCK_FALLBACK` for transparency.
* **Service Timeouts**: If GIS or database lookups fail, the system defaults to a safe state (`Z_UNKNOWN`) and continues analysis based on visual forensics alone.
* **Schema Repair**: A parser catches malformed JSON from LLMs and executes a repair prompt or applies default values (Severity 3, Risk MEDIUM) to prevent pipeline lockup.

---

## 6. Key Impact Metrics

| Metric | Target Performance |
| :--- | :--- |
| **Initial Triage Latency** | < 15 Seconds |
| **Diagnostic Accuracy (Visual)** | 94% Confidence |
| **False Positive Suppression** | 99.8% (Spam/Noise) |
| **Response Efficiency** | Elimination of 1st-Visit Diagnostic |

---

## 7. Future Vision
1. **Live IoT Integration**: Incorporating live pressure sensors and grid voltage feeds directly into the MKS layer.
2. **Drone Inspections**: Automating drone dispatch to verify high-severity anomalies before ground crews depart.
3. **Predictive Maintenance**: Using historical vector matches to predict failure points before they manifest visually.
