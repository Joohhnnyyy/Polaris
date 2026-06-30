# Polaris (CivicMind) — Frontend Architecture & Specification Document

## Executive Overview
This document specifies the architecture, page structure, section components, interactive elements, backend agent integrations, and visual design system for the **Polaris (CivicMind)** Autonomous Urban Intelligence System frontend.

The frontend is designed as a multi-portal ecosystem catering to three primary stakeholders:
1. **Citizens / Residents:** Mobile-first PWA for swift issue reporting and real-time agent tracking.
2. **Municipal Officers & Engineers:** High-density command center for AI co-piloting, risk cluster reviews, and contractor dispatch.
3. **General Public:** Transparency portal highlighting predictive maintenance, SLA tracking, and civic trust.

---

## 🌐 Global Page Hierarchy

| Page Route | Page Name | Primary Target User | Key Purpose |
| :--- | :--- | :--- | :--- |
| **`/`** | **Landing & Executive Portal** | General / Executives | High-level system overview, real-time urban nervous system metrics, active crisis banners, and navigation. |
| **`/citizen`** | **Citizen Intelligence Portal** | Citizens / Residents | Mobile-first issue reporting, AI pre-triage feedback, real-time agent processing timeline, and personal report tracking. |
| **`/officer`** | **Municipal Copilot Dashboard** | Municipal Engineers & Officers | Command center for reviewing correlated risk clusters, AI-generated work briefs, dispatching contractor work orders, and email approvals. |
| **`/map`** | **GIS Urban Intelligence Map** | City Planners & Engineers | Full-screen interactive geospatial workspace with layers for risk heatmaps, issue clusters, causal web overlays, and sensor feeds. |
| **`/autopsy/[id]`** | **Urban Autopsy Studio** *(Signature)* | Senior Engineers & Investigators | Deep-dive investigative studio showing force-directed evidence graphs, Gemini reasoning loops, historical failure timelines, and root cause analysis. |
| **`/transparency`** | **Public Trust & Predictive Portal** | General Public & Media | Community transparency dashboard showcasing predictive hazard forecasts, SLA resolution metrics, and verified civic activity. |

---

## 📄 Comprehensive Page Specifications

### 1. Landing & Executive Portal (`/`)
**Purpose:** Serves as the front door to Polaris, highlighting real-time city health and directing users to their respective portals.

#### 📍 Sections & Details
1. **Hero Header & Real-Time Status Banner:**
   - **Live Urban Status Indicator:** Glowing badge showing system health (e.g., `🟢 Urban Nervous System Active — 3 Critical Risk Clusters Monitoring`).
   - **Headline & Tagline:** Bold typography highlighting autonomous urban intelligence.
   - **Portal Quick-Switch CTA Cards:** Quick action cards for **Citizen Reporting**, **Officer Command Center**, and **Interactive Map**.
2. **Live Agent Activity Ticker:**
   - Real-time horizontal ticker streaming live events from the WebSocket agent pipeline (e.g., `[Synthesis Agent] Correlated 4 leaks in Ward 7 → Water Main Failure Hypothesis (Confidence: 89%)`).
3. **Key Infrastructure Metrics (KPI Grid):**
   - **Active Reports Processed:** Total count of ingested civic reports.
   - **Cascading Risks Prevented:** Number of high-risk multi-issue clusters identified before infrastructure collapse.
   - **Average Response SLA:** AI triage speed vs. traditional resolution time.
   - **Estimated Taxpayer Savings:** Cost saved via early preventive repairs vs. reactive emergency overhauls.
4. **System Architecture & Multi-Agent Flow Visualization:**
   - An interactive visual pipeline diagram demonstrating how citizen inputs flow through **Intake → Evidence → Synthesis → Brief** agents.

---

### 2. Citizen Intelligence Portal (`/citizen`)
**Purpose:** Mobile-optimized Progressive Web App (PWA) interface allowing residents to report infrastructure degradation and monitor their status in real-time.

#### 📍 Sections & Details
1. **Quick Action Bar:**
   - Toggle tabs: `Submit New Report` | `My Active Reports` | `Nearby Community Issues`.
2. **Interactive AI Report Submission Form:**
   - **Multi-Modal Media Upload:** Drag-and-drop or direct camera upload for photos/videos. Includes real-time client-side image preview and compression.
   - **GPS Auto-Geolocator:** Live map preview pinning exact user coordinates (`lat`, `lng`) with manual address search fallback.
   - **Citizen Description Box:** Rich text area with AI prompt suggestions (e.g., *"Describe any sounds, water flow, or structural cracks"*).
   - **Submit & Triage Button:** Initiates immediate agent processing pipeline.
3. **Live Agent Processing Drawer (Real-Time Websocket Modal):**
   - Displays real-time agent reasoning steps upon submission:
     - ⏱️ `12:01:04 [Intake Agent]` Analyzing imagery... Classified as Pothole (Severity 4/5).
     - ⏱️ `12:01:08 [Evidence Agent]` Extracting structural forensic details...
     - ⏱️ `12:01:14 [Synthesis Agent]` Correlating spatial cluster within 300m...
4. **Personal Tracker & Status Feed:**
   - Cards showing past submitted reports with live status pills (`Analyzing`, `Correlated into Cluster #204`, `Dispatched to Contractor`, `Resolved`).

---

### 3. Municipal Copilot Dashboard (`/officer`)
**Purpose:** Command center for city engineers and municipal leaders to review high-priority infrastructure risks and approve AI-generated action briefs.

#### 📍 Sections & Details
1. **Command Metrics & Alert Header:**
   - **Urgent Action Needed Badge:** Red pulsating counter showing unreviewed critical briefs.
   - **Active Cluster Counter by Urgency:** Categorized breakdown into `CRITICAL`, `HIGH`, `MEDIUM`, and `LOW`.
2. **Priority Risk Cluster Feed (Split View Master-Detail):**
   - **Left Panel (Cluster List):** Filterable list sorted by Risk Score and Affected Residents. Displays risk badge, location zone, and top hypothesis summary.
   - **Right Panel (Selected Cluster Intelligence Brief):**
     - **Synthesized Hypothesis Header:** AI-generated executive summary of the root cause (e.g., *Subsurface Pipe Degradation causing localized subsidence*).
     - **Risk Score & Impact Metrics:** Visual gauge meters for Severity, Confidence Score (0.0 - 1.0), and Estimated Affected Residents.
     - **Financial Impact Comparison:** Side-by-side card comparing *Preventive Repair Cost* vs. *Emergency Collapse Cost*.
3. **Autonomous Action Center (AI Officer Copilot):**
   - **AI-Drafted Communication Brief:** Pre-formatted professional email draft prepared by the `BriefAgent` addressed to the specific ward engineer.
   - **Work Order Dispatcher Preview:** Structured JSON/Table detailing contractor type, priority level, equipment required, and estimated turnaround.
   - **One-Click Action Buttons:** `Approve & Dispatch Work Order`, `Edit Brief`, `Escalate to Department Head`, or `Mark Disputed`.

---

### 4. GIS Urban Intelligence Map (`/map`)
**Purpose:** Full-screen interactive spatial exploration platform providing macro and micro urban monitoring.

#### 📍 Sections & Details
1. **Map Viewport Controls & Layer Selector:**
   - **Base Maps:** Toggle between Dark Vector Map, Satellite Hybrid, and Terrain.
   - **Layer Toggles:**
     - 🔴 **Risk Heatmap Layer:** Density map showing high-risk infrastructure failure zones.
     - 🔵 **Individual Reports Layer:** Clusters of individual citizen reports grouped spatially.
     - ⚡ **Causal Web Overlay:** Connected line graph linking isolated incidents (e.g., connecting 3 potholes to 1 central water main leak).
     - 🛰️ **IoT Infrastructure Assets:** Water mains, power grids, and transit line overlays.
2. **Interactive Map Side Panel:**
   - Clicking any cluster or marker slides open a quick context card with photo thumbnails, risk breakdown, and a link to open full **Urban Autopsy Mode**.
3. **Time-Travel Slider (Temporal Filtering):**
   - Range slider allowing officers to scrub back and forth through time (e.g., `Past 24 Hours`, `Past 7 Days`, `Past 30 Days`) to visualize how an infrastructure failure cluster evolved.

---

### 5. Urban Autopsy Studio (`/autopsy/[cluster_id]`) ⭐ *Signature Feature*
**Purpose:** An investigative studio for deep-dive root cause analysis. Demonstrates multi-agent reasoning depth for complex municipal cases.

#### 📍 Sections & Details
1. **Case Overview & Header Banner:**
   - Cluster ID, Geographic Zone ID, Timestamp of first detection, and overall System Stability Score.
2. **Force-Directed Evidence Web (Interactive Graph Visualization):**
   - Interactive D3.js or React Flow graph rendering nodes for **Citizen Reports (Images/Text)**, **Historical Maintenance Logs**, **Geospatial Sensors**, and the central **Synthesis Root Cause Hypothesis**.
3. **Gemini Agent Multi-Turn Reasoning Log:**
   - Terminal-style collapsible view displaying the precise function calls and multi-turn chat turns executed by `Gemini 2.5 Pro` during synthesis (e.g., `query_nearby_issues()`, `fetch_infrastructure_history()`, `assess_causal_chain()`).
4. **Multi-Modal Evidence Gallery:**
   - Side-by-side inspection grid showing uploaded citizen photos with Gemini Vision forensic annotations, overlaying surface cracks, water accumulation, and structural fault highlights.
5. **Causal Timeline Audit:**
   - Vertical chronological timeline showing how early minor symptoms developed into a correlated multi-point failure.

---

### 6. Public Trust & Predictive Portal (`/transparency`)
**Purpose:** Builds civic trust and provides open data access on city repairs and predictive maintenance.

#### 📍 Sections & Details
1. **Predictive Hotspot Forecast Map:**
   - Heatmap highlighting areas with high probability of failure over the next 30 to 90 days based on historical degradation models and seasonal weather.
2. **Community Resolution Feed:**
   - Publicly viewable stream of verified fixed issues with before-and-after photos, citizen upvotes, and resolution timelines.
3. **Municipal Accountability & SLA Leaderboard:**
   - Transparency graphs displaying department resolution speeds, active budget utilization, and community satisfaction ratings across city wards.

---

## 🎨 Design System & Aesthetics Guidelines

- **Color Palette & Theme:** Deep, sleek slate dark mode (`#0B0F17` background) combined with crisp neon accents:
  - **Emerald (`#10B981`):** Normal status, high confidence, resolved issues.
  - **Amber (`#F59E0B`):** Warnings, moderate risk, pending approvals.
  - **Crimson (`#EF4444`):** Critical risks, immediate structural hazards.
  - **Cyan (`#06B6D4`):** AI agent reasoning loops, WebSockets active.
- **Typography:** Modern clean sans-serif (**Inter** or **Outfit**) for UI elements, accompanied by monospace (**JetBrains Mono**) for agent logs and payload previews.
- **Micro-Animations & Motion:** Glassmorphism backdrop filters, pulsating live indicators, smooth layout morphing for card expansions, and interactive force-directed graph physics.
