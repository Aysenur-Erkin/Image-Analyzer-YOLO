from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_analyze_invalid_type():
    response = client.post(
        "/api/v1/analyze",
        files={"file": ("test.txt", b"hello", "text/plain")}
    )
    assert response.status_code == 400
