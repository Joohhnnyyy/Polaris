import sys
import os
import requests

def main():
    image_path = "test_images/pothole_emergency.png"
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        sys.exit(1)
        
    url = "http://localhost:8000/reports"
    
    data = {
        "lat": 28.590,
        "lng": 77.270,
        "description": "Severe deep pothole filled with rain water on the main sector roadway near the crossroad. Cars are swerving to avoid it, creating unsafe traffic conditions."
    }
    
    print(f"Sending pothole test report using {image_path}...")
    with open(image_path, "rb") as f:
        files = {
            "image": ("pothole_emergency.png", f, "image/png")
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
