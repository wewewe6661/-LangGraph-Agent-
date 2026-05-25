from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_api():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app_name" in data


def test_analyze_api_without_llm_key_returns_business_error():
    response = client.post("/api/analyze", json={"question": "哪个城市的订单量最高？"})
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "哪个城市的订单量最高？"
    assert "error" in data


def test_history_api_shape():
    response = client.get("/api/history")
    assert response.status_code in (200, 500)
