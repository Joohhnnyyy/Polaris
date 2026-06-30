import sys
import os
import requests

def main():
    image_path = "test_images/water_leak.png"
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        sys.exit(1)
        
    url = "http://localhost:8000/reports"
    
    data = {
        "lat": 28.580,
        "lng": 77.260,
        "description": "Continuous clean water bubbling up from expansion joints on the road near Sector 7B market."
    }
    
    print(f"Sending water leak test report using {image_path}...")
    with open(image_path, "rb") as f:
        files = {
            "image": ("water_leak.png", f, "image/png")
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
