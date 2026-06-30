import os
import json
import random
from datetime import datetime, timedelta
import asyncio
from backend.db.supabase_client import supabase_client
from backend.agents.evidence import EvidenceAgent

# Set default timezone for Postgres execution
os.environ["TZ"] = "UTC"

async def seed_db():
    print("Starting production municipal seeding script...")
    evidence = EvidenceAgent()

    # 1. Seed root causes
    root_causes = [
        # Water Leak
        {"id": "RC001", "category": "Water Leak", "cause": "Water main rupture", "prior": 0.35, "can_cause": ["Pavement Subsidence", "Road Collapse"], "requires": [], "evidence_required": ["Standing Water", "Bubbling"]},
        {"id": "RC002", "category": "Water Leak", "cause": "Sub-surface pipe leak", "prior": 0.45, "can_cause": ["Wet pavement saturation"], "requires": [], "evidence_required": ["Wet Soil", "Discoloration"]},
        {"id": "RC003", "category": "Water Leak", "cause": "Joint failure", "prior": 0.20, "can_cause": [], "requires": [], "evidence_required": ["Bubbling"]},
        
        # Pavement Subsidence
        {"id": "RC004", "category": "Pavement Subsidence", "cause": "Subgrade wash-out from water leak", "prior": 0.70, "can_cause": ["Pothole", "Road Collapse"], "requires": ["RC001", "RC002"], "evidence_required": ["Wet Soil", "Sunken pavement profile"]},
        {"id": "RC005", "category": "Pavement Subsidence", "cause": "Improper foundation soil compaction", "prior": 0.30, "can_cause": ["Pothole"], "requires": [], "evidence_required": ["Sunken pavement profile"]},

        # Pothole
        {"id": "RC006", "category": "Pothole", "cause": "Asphalt weathering and water infiltration", "prior": 0.60, "can_cause": [], "requires": ["RC002", "RC004"], "evidence_required": ["Cracked edges", "Asphalt fracturing"]},
        {"id": "RC007", "category": "Pothole", "cause": "Heavy traffic wear and tear", "prior": 0.40, "can_cause": [], "requires": [], "evidence_required": ["Bowl-shaped depression"]},

        # Broken Streetlight
        {"id": "RC008", "category": "Broken Streetlight", "cause": "Short-circuit or electrical wire decay", "prior": 0.50, "can_cause": [], "requires": [], "evidence_required": ["Sparking wiring"]},
        {"id": "RC009", "category": "Broken Streetlight", "cause": "Lamp or bulb failure", "prior": 0.50, "can_cause": [], "requires": [], "evidence_required": ["Broken lamp"]}
    ]
    try:
        supabase_client.table("root_cause_library").delete().neq("id", "0").execute()
        supabase_client.table("root_cause_library").insert(root_causes).execute()
        print(f"Seeded {len(root_causes)} root cause items.")
    except Exception as e:
        print(f"Root cause library seeding failed: {e}")

    # 2. Seed municipal policies
    policies = [
        {
            "id": "POL001",
            "rule_name": "Critical Water Main Rupture Policy",
            "category": "Water Leak",
            "dispatch_if": {"risk": "CRITICAL"},
            "minimum_confidence": 0.800,
            "minimum_reports": 1,
            "minimum_votes": 3,
            "max_response_time_hours": 2,
            "requires_human": False,
            "escalation_department": "Emergency Water Works Unit Division",
            "knowledge_version": "v1.4"
        },
        {
            "id": "POL002",
            "rule_name": "Standard Water Leak Policy",
            "category": "Water Leak",
            "dispatch_if": {"risk": "MEDIUM"},
            "minimum_confidence": 0.500,
            "minimum_reports": 1,
            "minimum_votes": 1,
            "max_response_time_hours": 24,
            "requires_human": True,
            "escalation_department": "Water Works and Sanitation Division",
            "knowledge_version": "v1.4"
        },
        {
            "id": "POL003",
            "rule_name": "Severe Subsidence Road Collapse Policy",
            "category": "Pavement Subsidence",
            "dispatch_if": {"risk": "CRITICAL"},
            "minimum_confidence": 0.750,
            "minimum_reports": 1,
            "minimum_votes": 2,
            "max_response_time_hours": 4,
            "requires_human": False,
            "escalation_department": "Public Safety & Civil Structural Engineering Team",
            "knowledge_version": "v1.4"
        },
        {
            "id": "POL004",
            "rule_name": "Standard Road Pavement Repair Policy",
            "category": "Pavement Subsidence",
            "category": "Pavement Subsidence",
            "dispatch_if": {"risk": "MEDIUM"},
            "minimum_confidence": 0.500,
            "minimum_reports": 1,
            "minimum_votes": 1,
            "max_response_time_hours": 72,
            "requires_human": True,
            "escalation_department": "Road Maintenance & Public Works",
            "knowledge_version": "v1.4"
        }
    ]
    try:
        supabase_client.table("municipal_policies").delete().neq("id", "0").execute()
        supabase_client.table("municipal_policies").insert(policies).execute()
        print(f"Seeded {len(policies)} policy items.")
    except Exception as e:
        print(f"Municipal policies seeding failed: {e}")

    # 3. Seed 25 Zones in Noida
    print("Generating Noida municipal zones grid...")
    zones_to_insert = []
    
    # Noida coordinates roughly: Lat 28.53 to 28.69, Lng 77.20 to 77.40
    # Let's create a 5x5 grid of administrative zones
    lat_steps = 5
    lng_steps = 5
    lat_min, lat_max = 28.53, 28.69
    lng_min, lng_max = 77.20, 77.40
    lat_width = (lat_max - lat_min) / lat_steps
    lng_width = (lng_max - lng_min) / lng_steps

    # Setup dedicated officers for assignment
    officer_res = supabase_client.table("officers").select("id, name").execute()
    officer_ids = [row["id"] for row in officer_res.data] if officer_res.data else []

    zone_id_idx = 1
    for i in range(lat_steps):
        for j in range(lng_steps):
            z_lat_min = lat_min + i * lat_width
            z_lat_max = z_lat_min + lat_width
            z_lng_min = lng_min + j * lng_width
            z_lng_max = z_lng_min + lng_width

            zone_name = f"Sector {zone_id_idx}A"
            if zone_id_idx == 7:
                zone_name = "Sector 7B" # Make sure Sector 7B exists exactly for target scenarios!
            elif zone_id_idx == 12:
                zone_name = "Sector 12"

            zone_id = f"Z{zone_id_idx:03d}"
            
            # 5-point closed polygon boundary (pentagon / box)
            boundary = [
                [z_lat_min, z_lng_min],
                [z_lat_max, z_lng_min],
                [z_lat_max, z_lng_max],
                [z_lat_min, z_lng_max],
                [z_lat_min, z_lng_min]
            ]
            
            zones_to_insert.append({
                "id": zone_id,
                "name": zone_name,
                "boundary_polygon": boundary,
                "assigned_officer_id": random.choice(officer_ids) if officer_ids else None,
                "soil_type": random.choice(["Clayey", "Sandy", "Mixed Loam", "Silt Clay"]),
                "is_active": True
            })
            zone_id_idx += 1

    try:
        supabase_client.table("zones").delete().neq("id", "0").execute()
        supabase_client.table("zones").insert(zones_to_insert).execute()
        print(f"Seeded {len(zones_to_insert)} admin zones spanning Noida municipal territory.")
    except Exception as e:
        print(f"Zones seeding failed: {e}")

    # 4. Generate 500+ Utility Assets with wear/maintenance correlations
    print("Generating correlated municipal assets...")
    assets_to_insert = []
    maintenance_records = []
    asset_types = ["WATER_MAIN", "STREETLIGHT", "DRAIN", "TRANSFORMER", "ROAD", "FOOTPATH"]
    materials = {
        "WATER_MAIN": ["Cast Iron", "Ductile Iron", "PVC", "HDPE"],
        "STREETLIGHT": ["Steel", "Aluminum", "Concrete"],
        "DRAIN": ["Reinforced Concrete", "Brick Masonry", "Clay"],
        "TRANSFORMER": ["Copper", "Silicon Steel"],
        "ROAD": ["Asphalt", "Concrete"],
        "FOOTPATH": ["Interlocking Pavers", "Concrete"]
    }

    asset_counter = 1
    for zone in zones_to_insert:
        # Determine center coordinate of the zone
        poly = zone["boundary_polygon"]
        lats = [pt[0] for pt in poly]
        lngs = [pt[1] for pt in poly]
        center_lat = sum(lats) / len(lats)
        center_lng = sum(lngs) / len(lngs)

        # Place 20 assets in each zone (20 * 25 = 500 assets)
        for _ in range(20):
            asset_type = random.choice(asset_types)
            asset_material = random.choice(materials[asset_type])
            
            # Asset wear correlation: older install year -> lower condition score
            install_year = random.randint(1975, 2022)
            current_year = 2026
            age = current_year - install_year
            
            # Condition score scales from 1 (broken) to 10 (brand new)
            base_score = 10 - int(age / 5.5)
            condition_score = max(1, min(10, base_score + random.randint(-1, 1)))

            # Status correlation
            if condition_score <= 3:
                status = "MAINTENANCE_REQUIRED" if random.random() > 0.3 else "OUT_OF_SERVICE"
            else:
                status = "OPERATIONAL"

            # Colocate asset slightly offset from zone center
            offset_lat = random.uniform(-0.003, 0.003)
            offset_lng = random.uniform(-0.003, 0.003)
            
            asset_id = f"{asset_type[:2]}-{asset_counter:05d}"
            
            asset_data = {
                "id": asset_id,
                "zone_id": zone["id"],
                "asset_type": asset_type,
                "material": asset_material,
                "diameter_mm": random.choice([150, 300, 450, 600]) if asset_type == "WATER_MAIN" else None,
                "pressure_rating": random.choice([6.0, 10.0, 16.0]) if asset_type == "WATER_MAIN" else None,
                "install_year": install_year,
                "condition_score": condition_score,
                "status": status,
                "lat": center_lat + offset_lat,
                "lng": center_lng + offset_lng,
                "is_active": True
            }
            assets_to_insert.append(asset_data)
            
            # Generate maintenance history records for older/decayed assets
            if age > 15:
                num_repairs = random.randint(1, 3)
                for r_idx in range(num_repairs):
                    repair_cost = float(random.randint(15000, 145000))
                    repair_date = (datetime.utcnow() - timedelta(days=random.randint(30, 720))).isoformat()
                    maintenance_records.append({
                        "asset_id": asset_id,
                        "inspection_date": repair_date,
                        "repair_type": "Joint Sealant" if asset_type == "WATER_MAIN" else "Component Replacement",
                        "failure_reason": "Corrosion & Age Wear" if random.random() > 0.4 else "Ground Shift Stress",
                        "crew": random.choice(["Urban Utility Crew Alpha", "Noida Maintenance Team 4B", "Civil Safety Taskforce"]),
                        "cost": repair_cost,
                        "success": True,
                        "resolved": True,
                        "notes": "Emergency joint reinforcing applied. Material degradation resolved."
                    })

            asset_counter += 1

    try:
        supabase_client.table("utility_assets").delete().neq("id", "0").execute()
        # Batch insert in chunks of 100 to stay well under API transaction limits
        for k in range(0, len(assets_to_insert), 100):
            supabase_client.table("utility_assets").insert(assets_to_insert[k:k+100]).execute()
        print(f"Seeded {len(assets_to_insert)} dynamic municipal utility assets.")
        
        # Batch insert maintenance records
        for k in range(0, len(maintenance_records), 100):
            supabase_client.table("maintenance_history").insert(maintenance_records[k:k+100]).execute()
        print(f"Seeded {len(maintenance_records)} historical asset maintenance inspections.")
    except Exception as e:
        print(f"Assets or maintenance seeding failed: {e}")

    # 5. Seed 200+ Historical Incidents with correlated category distributions & vector embeddings
    print("Generating 200+ correlated historical incidents (embedding generation active)...")
    incidents_to_insert = []
    
    # 40% Water Leak, 20% Pothole, 15% Streetlight, 15% Garbage, 10% Drain Blockage
    categories = ["Water Leak", "Pothole", "Broken Streetlight", "Garbage Pile", "Drain Blockage"]
    probabilities = [0.40, 0.20, 0.15, 0.15, 0.10]
    
    outcomes = ["Resolved", "False Alarm", "Manual Inspection", "Pipeline Replaced", "No Fault Found"]
    risk_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    descriptions_by_cat = {
        "Water Leak": [
            "Water main leakage bubbling up through joints.",
            "Water main rupture spraying water onto street pavement.",
            "Pipeline valve joint leaking slowly causing soil saturation.",
            "Bubbling water pooling on sidewalk near water valve box."
        ],
        "Pothole": [
            "Deep asphalt pothole causing tire damage to vehicles.",
            "Severe pothole crater on main sector transit road.",
            "Pothole causing vehicles to swerve dangerously.",
            "Series of small potholes forming along road shoulder seam."
        ],
        "Broken Streetlight": [
            "Streetlight flickering on and off intermittently at night.",
            "Completely dark streetlight fixture bulb failed.",
            "Utility pole wire short-circuit causing lamp to sparkle.",
            "Broken lamp post cover dangling from electrical pole."
        ],
        "Garbage Pile": [
            "Unauthorized commercial garbage dump pile accumulating.",
            "Garbage overflowing onto public pedestrian walkway.",
            "Debris and waste rotting outside sector collection bins."
        ],
        "Drain Blockage": [
            "Storm drain clogged with plastic garbage and dirt leaves.",
            "Drainage backing up causing local road waterlogging.",
            "Sewer drain inlet choked with sediment run-off."
        ]
    }

    # Map categories to root cause IDs
    cause_mapping = {
        "Water Leak": "RC002",
        "Pavement Subsidence": "RC004",
        "Pothole": "RC006",
        "Broken Streetlight": "RC009",
        "Garbage Pile": "RC007",
        "Drain Blockage": "RC001"
    }

    for idx in range(1, 205):
        # Pick category based on distribution
        category = random.choices(categories, weights=probabilities, k=1)[0]
        
        # Pick random Noida zone
        zone = random.choice(zones_to_insert)
        
        # Colocate incident coordinate inside the selected zone
        poly = zone["boundary_polygon"]
        lats = [pt[0] for pt in poly]
        lngs = [pt[1] for pt in poly]
        lat = random.uniform(min(lats), max(lats))
        lng = random.uniform(min(lngs), max(lngs))

        desc = random.choice(descriptions_by_cat[category])
        
        # Use EvidenceAgent to generate real 768-dim embeddings for historical incidents
        emb_768 = await evidence.generate_embedding(category, desc)
        # Pad to 3072 dimensions to match database schema constraints
        emb = emb_768 + [0.0] * (3072 - 768)
        
        # Correlate resolution cost and duration
        cost = float(random.randint(10000, 185000))
        days = random.randint(1, 10)
        
        incident_outcome = random.choice(outcomes)
        risk = random.choice(risk_levels)
        conf = float(round(random.uniform(0.60, 0.95), 2))

        incidents_to_insert.append({
            "zone_id": zone["id"],
            "category": category,
            "root_cause_id": cause_mapping.get(category, "RC002"),
            "incident_outcome": incident_outcome,
            "confidence": conf,
            "risk_level": risk,
            "resolution_summary": f"Historical case resolved: {desc} Managed via {incident_outcome}.",
            "resolution_days": days,
            "resolution_cost": cost,
            "resolution_method": "Replaced joint seals and repaired subgrade asphalt structure.",
            "verification_votes": random.randint(1, 12),
            "dispute_votes": random.randint(0, 1),
            "lat": lat,
            "lng": lng,
            "embedding": emb,
            "embedding_model": "text-embedding-004",
            "is_active": True,
            "created_at": (datetime.utcnow() - timedelta(days=random.randint(10, 365))).isoformat()
        })

        if idx % 50 == 0:
            print(f"Generated {idx} historical incidents...")

    try:
        supabase_client.table("historical_incidents").delete().neq("id", 0).execute()
        # Ingest in chunks of 50 to avoid payload size constraints
        for k in range(0, len(incidents_to_insert), 50):
            supabase_client.table("historical_incidents").insert(incidents_to_insert[k:k+50]).execute()
        print(f"Seeded {len(incidents_to_insert)} spatial historical incidents with vector embeddings.")
    except Exception as e:
        print(f"Historical incidents seeding failed: {e}")

    print("Municipal Seeding Completed Successfully! Database is fully operational.")

if __name__ == "__main__":
    asyncio.run(seed_db())
