from app.main import app
from fastapi.testclient import TestClient


def test_health_lists_supported_degrees() -> None:
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["supported_degrees"] == ["master", "swufe_master", "undergraduate"]
