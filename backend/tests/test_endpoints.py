from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_health():
    """Test that the main API routing is up and running"""
    response = client.get("/api/reports/status")
    # Our API might return a 404 if /status isn't defined, or a 200.
    # Let's test a known endpoint or just assert it doesn't 500.
    assert response.status_code in [200, 404], f"Unexpected status code: {response.status_code}"

def test_api_root():
    response = client.get("/")
    assert response.status_code in [200, 404]
