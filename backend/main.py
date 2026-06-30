from fastapi import FastAPI, UploadFile, File, Form, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.db.supabase_client import supabase_client
from backend.agents.intake import IntakeAgent
from backend.agents.evidence import EvidenceAgent
from backend.agents.synthesis import SynthesisAgent
from backend.agents.brief import BriefAgent
import uuid
from datetime import datetime
from pillow_heif import register_heif_opener

# Register HEIC/HEIF opener for Pillow to handle iOS uploaded photos
register_heif_opener()

from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="CivicMind API", version="1.0.0")

# Mount local static files directory to serve uploaded images locally
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure CORS based on environment settings
allowed_origins_raw = settings.ALLOWED_ORIGINS
if not allowed_origins_raw or allowed_origins_raw == "*":
    origins = ["*"]
    allow_credentials = False
else:
    origins = [origin.strip() for origin in allowed_origins_raw.split(",") if origin.strip()]
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize agents
intake_agent = IntakeAgent()
evidence_agent = EvidenceAgent()
synthesis_agent = SynthesisAgent()
brief_agent = BriefAgent()

# Helper for timeline logs
async def timeline_log(stage: str, message: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    await manager.broadcast(f"{timestamp} [{stage}] {message}")


@app.on_event("startup")
async def startup_event():
    try:
        # Create public bucket 'civicmind-images'
        supabase_client.storage.create_bucket("civicmind-images", options={"public": True})
        print("Successfully created Supabase storage bucket 'civicmind-images'")
    except Exception as e:
        # Bucket likely already exists, ignore error
        print(f"Supabase storage bucket check: {e}")

# WebSocket Connection Manager for agent thought logs
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "project": "CivicMind",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

import asyncio
from fastapi import BackgroundTasks

# Async background process to run synthesis & briefing
async def process_async_synthesis(inserted_issue: dict):
    try:
        await timeline_log("Synthesis", "Invoking reasoning loop on Gemini 2.5 Pro (Urban Autopsy) in background.")
        synthesis_result = await synthesis_agent.run_synthesis(inserted_issue)
        await timeline_log("Synthesis", f"Completed. Risk level: {synthesis_result.get('risk_level')}. Hypothesis: {synthesis_result.get('causal_hypothesis')}.")
        
        # Dispatch brief if risk is high/critical
        if synthesis_result.get("risk_level") in ["HIGH", "CRITICAL"]:
            cluster_id = synthesis_result.get("cluster_id")
            if cluster_id:
                await timeline_log("Briefing", f"Generating communication brief and auto-dispatching work order.")
                # We can trigger the email brief automatically
                # Query cluster info first
                try:
                    cluster_res = supabase_client.table("clusters").select("*").eq("id", cluster_id).execute()
                    if cluster_res.data:
                        cluster_data = cluster_res.data[0]
                        # Fetch officer details
                        officer_email = "anshuman.ash@outlook.com"
                        officer_name = "Officer Johnson"
                        if cluster_data.get("assigned_officer_id"):
                            off_res = supabase_client.table("officers").select("*").eq("id", cluster_data.get("assigned_officer_id")).execute()
                            if off_res.data:
                                officer_email = off_res.data[0].get("email", officer_email)
                                officer_name = off_res.data[0].get("name", officer_name)
                        
                        generated_brief = await brief_agent.generate_brief(
                            zone_id=cluster_data.get("zone_id", "Sector 7B"),
                            risk_level=cluster_data.get("risk_level", "HIGH"),
                            causal_hypothesis=cluster_data.get("causal_hypothesis", ""),
                            affected_residents=cluster_data.get("affected_residents", 2400)
                        )
                        
                        custom_subject = generated_brief.get("subject")
                        custom_body = generated_brief.get("email_body")
                        
                        brief_details = {
                            "zone_id": cluster_data.get("zone_id", "Sector 7B"),
                            "risk_level": cluster_data.get("risk_level", "HIGH"),
                            "confidence": cluster_data.get("confidence", 0.8),
                            "affected_residents": cluster_data.get("affected_residents", 2400),
                            "causal_hypothesis": cluster_data.get("causal_hypothesis", "")
                        }
                        
                        success = sendgrid_client.send_officer_email(
                            to_email=officer_email,
                            officer_name=officer_name,
                            brief_details=brief_details,
                            custom_subject=custom_subject,
                            custom_body=custom_body
                        )
                        
                        # Save brief to DB
                        supabase_client.table("briefs").insert({
                            "cluster_id": cluster_id,
                            "officer_id": cluster_data.get("assigned_officer_id"),
                            "draft_email": f"To: {officer_email}\nSubject: {custom_subject}\n\n{custom_body}",
                            "status": "SENT" if success else "FAILED"
                        }).execute()
                        await timeline_log("Briefing", f"Brief dispatched successfully to {officer_name} ({officer_email}).")
                except Exception as brief_err:
                    print(f"Background brief failed: {brief_err}")
    except Exception as e:
        import traceback
        print(f"Async synthesis background process failed: {e}")
        traceback.print_exc()

@app.post("/reports")
async def create_report(
    request: Request,
    background_tasks: BackgroundTasks,
    lat: float = Form(...),
    lng: float = Form(...),
    description: str = Form(""),
    image: UploadFile = File(...)
):
    try:
        # Check upload size limit
        max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
        content_length = image.headers.get("content-length")
        if content_length and int(content_length) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum limit of {settings.MAX_UPLOAD_MB}MB"
            )

        # Read image bytes and check actual length
        image_bytes = await image.read()
        if len(image_bytes) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum limit of {settings.MAX_UPLOAD_MB}MB"
            )
        
        print(f"DEBUG: Received image bytes length = {len(image_bytes)}")
        
        # 1. Run Intake Agent
        await timeline_log("Intake", "Received new citizen report. Starting classification.")
        intake_result = await intake_agent.classify_report(image_bytes, description)
        
        # Early rejection for non-civic issues
        is_civic = intake_result.get("is_civic_issue", True)
        if not is_civic:
            await timeline_log("Intake", "Report rejected: Submission classified as non-civic/irrelevant.")
            return {
                "success": False,
                "reason": "Non-civic/irrelevant image detected. Submission rejected.",
                "intake_result": intake_result
            }

        await timeline_log("Intake", f"Classified issue as {intake_result.get('category')} (Severity: {intake_result.get('severity')}/5).")
        
        # 2. Concurrently run Evidence Agent perform_forensics and generate_embedding
        await timeline_log("Evidence", "Running forensics and generating embeddings concurrently.")
        forensics_task = evidence_agent.perform_forensics(image_bytes, intake_result.get("summary", ""))
        embedding_task = evidence_agent.generate_embedding(
            category=intake_result.get("category", "Other"),
            description=description
        )
        
        forensics_result, embedding = await asyncio.gather(forensics_task, embedding_task)
        
        # Extract likely root cause safely from new candidate_causes list or hypotheses fallback
        likely_cause = "Unknown degradation"
        if "candidate_causes" in forensics_result and forensics_result["candidate_causes"]:
            likely_cause = forensics_result["candidate_causes"][0].get("cause", likely_cause)
        elif "hypotheses" in forensics_result and forensics_result["hypotheses"]:
            likely_cause = forensics_result["hypotheses"][0].get("cause", likely_cause)
            
        await timeline_log("Evidence", f"Forensics complete. Hypothesis: {likely_cause} (Confidence: {int(forensics_result.get('confidence', 0.7)*100)}%).")
        
        # Save image locally to static directory to ensure reliable loading in frontend
        file_ext = image.filename.split(".")[-1] if "." in image.filename else "jpg"
        filename = f"{uuid.uuid4()}.{file_ext}"
        os.makedirs("static", exist_ok=True)
        local_path = os.path.join("static", filename)
        with open(local_path, "wb") as local_f:
            local_f.write(image_bytes)
        
        base_url = str(request.base_url)
        image_url = f"{base_url.rstrip('/')}/static/{filename}"
        
        # Also try uploading to Supabase Storage in the background (best-effort)
        try:
            filepath = f"public/{filename}"
            supabase_client.storage.from_("civicmind-images").upload(
                filepath, 
                image_bytes, 
                {"content-type": f"image/{file_ext}"}
            )
        except Exception as storage_err:
            print(f"Storage upload failed (falling back to local serving only): {storage_err}")
 
        # 3. Duplicate Detection Logic: same category + within 50m distance + cosine similarity > 0.90
        await timeline_log("Analysis", "Performing duplicate check against recent reports.")
        try:
            # Query nearby issues of the SAME category within 100m to evaluate locally
            # We can use find_similar_issues rpc but with larger radius then filter in python to ensure exact matches
            similar_res = supabase_client.rpc(
                "find_similar_issues",
                {
                    "query_embedding": embedding,
                    "center_lat": lat,
                    "center_lng": lng,
                    "radius_meters": 50.0,
                    "days_back": 30 # check up to 30 days
                }
            ).execute()
            
            duplicate_issue = None
            if similar_res.data:
                for nearby_issue in similar_res.data:
                    # check exact category match, distance < 50m
                    same_category = nearby_issue.get("category") == intake_result.get("category")
                    dist = float(nearby_issue.get("distance_meters") or 999.0)
                    
                    if same_category and dist < 50.0:
                        duplicate_issue = nearby_issue
                        break
            
            if duplicate_issue:
                await timeline_log("Analysis", f"Duplicate detected: Issue {duplicate_issue['id']} matches category and coordinates.")
                return {
                    "success": True,
                    "duplicate": True,
                    "issue_id": duplicate_issue["id"],
                    "category": duplicate_issue["category"],
                    "message": "Duplicate report detected. Logged verification vote on existing report."
                }
        except Exception as dup_err:
            print(f"Duplicate detection search failed: {dup_err}")

        # Combine agent outputs
        gemini_analysis = {
            "intake": intake_result,
            "forensics": forensics_result
        }
        
        # Save to database
        db_data = {
            "category": intake_result.get("category", "Other"),
            "severity": intake_result.get("severity", 3),
            "lat": lat,
            "lng": lng,
            "description": description,
            "images": [image_url],
            "status": "REPORTED",
            "credibility_score": intake_result.get("confidence", 1.0),
            "embedding": embedding,
            "gemini_analysis": gemini_analysis
        }
        
        res = supabase_client.table("issues").insert(db_data).execute()
        
        if not res.data:
            raise HTTPException(status_code=500, detail="Failed to save report to database")
            
        inserted_issue = res.data[0]
        
        # 4. Trigger Synthesis Agent loop (Urban Autopsy) in background task
        background_tasks.add_task(process_async_synthesis, inserted_issue)
        await timeline_log("System", "Initial report ingestion complete. Offloaded deep Synthesis analysis to background worker.")
        
        return {
            "success": True,
            "issue_id": inserted_issue["id"],
            "category": inserted_issue["category"],
            "severity": inserted_issue["severity"],
            "gemini_analysis": gemini_analysis,
            "status": "processing"
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        await timeline_log("System Error", f"processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing report: {str(e)}")


from backend.notifications.sendgrid_client import SendGridClient
sendgrid_client = SendGridClient()

@app.get("/clusters")
def get_clusters():
    try:
        res = supabase_client.table("clusters").select("*").order("created_at", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch clusters: {str(e)}")

@app.get("/issues")
def get_issues(cluster_id: str = None):
    try:
        query = supabase_client.table("issues").select("*")
        if cluster_id:
            query = query.eq("cluster_id", cluster_id)
        res = query.order("created_at", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch issues: {str(e)}")

@app.get("/decision_audit/{issue_id}")
def get_decision_audit(issue_id: str):
    try:
        res = supabase_client.table("decision_audit").select("*").eq("issue_id", issue_id).limit(1).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch decision audit: {str(e)}")

@app.get("/briefs")
def get_briefs():
    try:
        res = supabase_client.table("briefs").select("*, clusters(*)").order("created_at", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch briefs: {str(e)}")

@app.post("/briefs/{brief_id}/approve")
def approve_brief(brief_id: str):
    try:
        res = supabase_client.table("briefs").update({"status": "APPROVED"}).eq("id", brief_id).execute()
        return {"success": True, "data": res.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve brief: {str(e)}")

@app.get("/config")
def get_config():
    return {
        "google_maps_key": settings.GOOGLE_MAPS_KEY
    }

@app.post("/dispatch")
async def dispatch_brief(payload: dict):
    cluster_id = payload.get("cluster_id")
    email = payload.get("email", "anshuman.ash@outlook.com")
    officer_name = payload.get("officer_name", "Officer Johnson")
    
    try:
        res = supabase_client.table("clusters").select("*").eq("id", cluster_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Cluster not found")
        
        cluster_data = res.data[0]
        
        brief_details = {
            "zone_id": cluster_data.get("zone_id", "Sector 7B"),
            "risk_level": cluster_data.get("risk_level", "HIGH"),
            "confidence": cluster_data.get("confidence", 0.8),
            "affected_residents": cluster_data.get("affected_residents", 2400),
            "causal_hypothesis": cluster_data.get("causal_hypothesis", "")
        }
        
        # Generate communication brief using BriefAgent
        generated_brief = await brief_agent.generate_brief(
            zone_id=brief_details["zone_id"],
            risk_level=brief_details["risk_level"],
            causal_hypothesis=brief_details["causal_hypothesis"],
            affected_residents=brief_details["affected_residents"]
        )
        
        custom_subject = generated_brief.get("subject")
        custom_body = generated_brief.get("email_body")
        
        success = sendgrid_client.send_officer_email(
            to_email=email,
            officer_name=officer_name,
            brief_details=brief_details,
            custom_subject=custom_subject,
            custom_body=custom_body
        )
        
        # Save to briefs table
        supabase_client.table("briefs").insert({
            "cluster_id": cluster_id,
            "draft_email": f"To: {email}\nSubject: {custom_subject}\n\n{custom_body}",
            "status": "SENT" if success else "FAILED"
        }).execute()
        
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dispatch failed: {str(e)}")

