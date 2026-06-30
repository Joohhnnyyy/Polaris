# Polaris: Urban Operating System

Polaris is a multi-agent platform designed to unify fragmented municipal infrastructure reports, sensor telemetry, and urban planning historical data into a single operational interface. By leveraging structured multi-modal reasoning and real-time data streaming, the system categorizes citizen reports, hypothesizes root causes for infrastructure degradation, evaluates systemic risks of cascading failures, and drafts ready-to-dispatch briefs for field engineers.

---

## Tech Stack

### Frontend Architecture
* **Framework**: React 19 with Vite 8
* **Routing and SSR**: TanStack Start (Server-Side Rendering) and TanStack Router
* **State Management**: TanStack Query (React Query)
* **Styling**: TailwindCSS with CSS custom properties for dark mode and structural glassmorphism
* **Animations**: Framer Motion for timeline streaming transitions and fluid interactive views
* **Maps**: Google Maps JS API with customized dark canvas styles

### Backend Architecture
* **Framework**: FastAPI (Python 3.11)
* **Server**: Uvicorn
* **Database & Storage**: Supabase (PostgreSQL with PgVector for semantic similarity matching)
* **In-Memory Caching & Session Store**: Redis (Upstash)
* **External Integration**: OpenWeather API (current conditions mapping), SendGrid (officer alert email dispatches)

### Infrastructure and Deployment
* **Cloud Platform**: Google Cloud Platform (GCP)
* **Compute Services**: Google Cloud Run (Frontend and Backend services deployed as independent, auto-scaling containers)
* **Authentication & Keyless Access**: Workload Identity Federation (OIDC) enabling secure, keyless deployments from GitHub Actions
* **Continuous Integration / Continuous Deployment (CI/CD)**: GitHub Actions (workflows for targeted backend and frontend container build-and-deploy stages)

---

## Multi-Agent System Architecture and Flow

The application processes report ingestion through a multi-stage sequential agent pipeline. Each agent is isolated with specific instructions and returns structured, validated JSON data matching predefined Pydantic schemas.

```
[Citizen Report] -> (Intake Agent) -> [Triage & Severity]
                         |
                         v
                  (Evidence Agent) -> [Visual Forensics & Embeddings]
                         |
                         v
                 (Synthesis Agent) <-> [Supabase Vector DB (PgVector)]
                         |
                         v
                   [Risk Cluster]
                         |
                         v
                   (Brief Agent) -> [Dispatch Brief Email Draft]
```

### 1. Intake Agent (intake.py)
* **Model**: gemini-2.5-flash
* **Responsibility**: Ingests citizen-submitted reports containing images and descriptions. It classifies the issue category, evaluates severity levels, and estimates the physical dimensions of the affected zone.
* **Severity Rubric**:
  * Level 1: Cosmetic issue (visual defect, no functional or safety impact)
  * Level 2: Minor inconvenience (nuisance, no immediate structural threat)
  * Level 3: Requires attention (noticeable structural degradation requiring repair queue)
  * Level 4: Dangerous (poses immediate structural hazard or vehicle damage risk)
  * Level 5: Critical public safety risk (active hazard causing immediate danger to lives or critical systems)

### 2. Evidence Agent (evidence.py)
* **Model**: gemini-2.5-flash & models/text-embedding-004
* **Responsibility**: Performs deep visual forensics on the uploaded images. It identifies signs of structural degradation (e.g. rust, cracking, moisture ingress), generates hypotheses for root causes with associated confidence values, evaluates the probability of cascading failures, and computes high-dimensional text embeddings of the forensic description for similarity matching.

### 3. Synthesis Agent (synthesis.py)
* **Model**: gemini-2.5-pro
* **Responsibility**: Coordinates urban planning intelligence. It runs an autonomous reasoning loop using function calling to search database tables (reports, infrastructure histories) and query nearby incidents using PgVector similarity matching via Supabase RPC. It synthesizes individual events into correlated "Risk Clusters", identifies spatial bounds, estimates repair costs, and determines the total resident count affected.

### 4. Brief Agent (brief.py)
* **Model**: gemini-2.5-flash
* **Responsibility**: Formats and generates communications. It consumes the output of the Synthesis Agent and draft briefs containing professional email subject lines and descriptive body text tailored for dispatching engineering crews.

---

## Testing, Verification, and Certification

The codebase is hardened and verified through automated test suites located in the scripts directory. These validation metrics ensure compliance with production stability guidelines:

### 1. Production Hardening Verification (test_production_hardening.py)
* **Health Check Validation**: Verifies root API path readiness and Uvicorn responsiveness.
* **CORS Compliance**: Evaluates cross-origin restriction settings.
* **Upload Limits Verification**: Checks that payloads exceeding configuration limits (e.g. file size > 10MB) are rejected with HTTP 413.

### 2. Adversarial Robustness Testing (adversarial_testing.py)
* **Prompt Injection Defense**: Validates that system instructions and severity rubrics are preserved under adversarial citizen descriptions.
* **Corrupted Image Integrity**: Assures that the Intake and Evidence agents fail gracefully when parsing corrupted or unreadable image binaries.

### 3. Urban Autopsy Benchmarking (urban_autopsy_benchmark.py)
* **Reasoning Accuracy**: Evaluates the Synthesis Agent's causal hypotheses against historical ground-truth incident records to calculate precision and recall statistics.
* **Cost Approximation Margin**: Compares estimated repair costs generated by the Synthesis Agent against actual municipal budget allocations.
