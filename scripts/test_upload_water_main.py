import sys
import os
import requests

def main():
    image_path = "test_images/water_main_rupture.png"
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        sys.exit(1)
        
    url = "http://localhost:8000/reports"
    
    data = {
        "lat": 28.570,
        "lng": 77.250,
        "description": "CRITICAL EMERGENCY: Massive main pipe burst spraying water 20 feet into the air. Flooding the entire street block near Sector 7B."
    }
    
    print(f"Sending water main burst test report using {image_path}...")
    with open(image_path, "rb") as f:
        files = {
            "image": ("water_main_rupture.png", f, "image/png")
        }
        try:
            r = requests.post(url, data=data, files=files)
            print(f"Response Status Code: {r.status_code}")
            if r.status_code == 200:
                print("Success! Response JSON:")
                import json
                print(json.dumps(r.json(), indent=2))
            else:
                print(f"Failed with response: {r.text}")
        except Exception as e:
            print(f"Connection error: {e}")

if __name__ == "__main__":
    main()
