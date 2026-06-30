import sys
import os
import requests

def main():
    image_path = "/Users/anshjohnson/Polaris/road_water.jpeg"
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        sys.exit(1)
        
    url = "http://localhost:8000/reports"
    
    data = {
        "lat": 28.6850,
        "lng": 77.4800,
        "description": "Heavy water leak and bubbling road deformation observed near block A main lane."
    }
    
    print(f"Sending test report with image {image_path}...")
    with open(image_path, "rb") as f:
        files = {
            "image": ("road_water.jpeg", f, "image/jpeg")
        }
        try:
            r = requests.post(url, data=data, files=files)
            print(f"Response Status Code: {r.status_code}")
            if r.status_code == 200:
                print("Success! Response JSON:")
                print(r.json())
            else:
                print(f"Failed with response: {r.text}")
        except Exception as e:
            print(f"Connection error: {e}")

if __name__ == "__main__":
    main()
