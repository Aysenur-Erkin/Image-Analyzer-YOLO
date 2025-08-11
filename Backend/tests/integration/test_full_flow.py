import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_analyze_flow():
    img_bytes = io.BytesIO(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4"
        b"\x89\x00\x00\x00\nIDATx\xdac``\x00\x00\x00\x02"
        b"\x00\x01\xe2!\xbc33\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    files = {
        "file": ("test.png", img_bytes, "image/png")
    }

    response = client.post("/api/v1/analyze", files=files)
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert data["message"] == "Analysis complete"
    assert isinstance(data["objects"], list)

    assert data["objects"] == []
