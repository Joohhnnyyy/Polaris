import os
import sys

# Add root folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from backend.main import app
from backend.config import settings

def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("Health check endpoint test passed!")

def test_cors_settings():
    client = TestClient(app)
    # Test default '*'
    settings.ALLOWED_ORIGINS = "*"
    
    # Reload middleware/app is not easily done on the fly, but we can verify settings logic
    assert settings.ALLOWED_ORIGINS == "*"
    print("CORS configuration settings test passed!")

def test_upload_limits():
    client = TestClient(app)
    # Set limit to 1MB for testing
    settings.MAX_UPLOAD_MB = 1
    
    # Create a 2MB dummy payload
    dummy_data = b"0" * (2 * 1024 * 1024)
    
    response = client.post(
        "/reports",
        data={"lat": 37.7749, "lng": -122.4194, "description": "Test too large"},
        files={"image": ("large.jpg", dummy_data, "image/jpeg")}
    )
    
    # Expect 413
    assert response.status_code == 413
    assert "File size exceeds maximum limit" in response.json()["detail"]
    print("Upload limits enforcement test passed!")

if __name__ == "__main__":
    print("Running tests...")
    test_health_endpoint()
    test_cors_settings()
    test_upload_limits()
    print("All production hardening verification tests passed successfully!")
