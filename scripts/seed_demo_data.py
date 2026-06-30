import json
from datetime import datetime, timedelta
from backend.db.supabase_client import supabase_client
from backend.agents.evidence import EvidenceAgent
import asyncio

async def seed_data():
    print("Starting data seeding...")
    
    # 1. Clear existing records to ensure clean slate
    try:
        supabase_client.table("briefs").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        supabase_client.table("issues").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        supabase_client.table("clusters").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        supabase_client.table("officers").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print("Cleared existing records.")
    except Exception as e:
        print(f"Cleanup failed (might be empty or missing table): {e}")

    # 2. Seed Officers
    officer_data = [
        {
            "name": "Dr. Devender Sharma",
            "email": "teesstting23213@gmail.com", # Matches SendGrid verified email for testing!
            "department": "Water Works and Sanitation Division",
            "zone_id": "Sector 7B"
        },
        {
            "name": "Arun K. Singh",
            "email": "arun.singh@ghaziabadmunicipal.org",
            "department": "Road Maintenance & Public Works",
            "zone_id": "Sector 12"
        }
    ]
    
    officers = supabase_client.table("officers").insert(officer_data).execute()
    print(f"Seeded {len(officers.data)} officers.")

    # 3. Initialize Evidence Agent for generating real embeddings for historical cases
    evidence = EvidenceAgent()
    
    # Baseline Issue 1: Water Leakage (reported 3 days ago in Sector 7B)
    leak_description = "Continuous clean water bubbling up from expansion joints on the road near Sector 7B market."
    leak_embedding = await evidence.generate_embedding("Water Leak", leak_description)
    
    # Baseline Issue 2: Road Subsidence (reported 1 day ago)
    sub_description = "The road surface has sunk by about 3-4 inches near the Sector 7B market entrance. Soil feels damp."
    sub_embedding = await evidence.generate_embedding("Pavement Subsidence", sub_description)

    # Seed issues
    issues_data = [
        {
            "category": "Water Leak",
            "severity": 4,
            "lat": 28.6695,
            "lng": 77.4540,
            "description": leak_description,
            "status": "REPORTED",
            "credibility_score": 0.85,
            "embedding": leak_embedding,
            "created_at": (datetime.utcnow() - timedelta(days=3)).isoformat()
        },
        {
            "category": "Pavement Subsidence",
            "severity": 4,
            "lat": 28.6690,
            "lng": 77.4535,
            "description": sub_description,
            "status": "REPORTED",
            "credibility_score": 0.90,
            "embedding": sub_embedding,
            "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat()
        }
    ]

    issues = supabase_client.table("issues").insert(issues_data).execute()
    print(f"Seeded {len(issues.data)} baseline historical issues in Sector 7B cluster zone.")
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    asyncio.run(seed_data())
