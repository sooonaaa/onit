import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    # Проверяем, что главная страница открывается (код 200)
    response = client.get("/")
    assert response.status_code == 200
    assert "CRUD App" in response.text

def test_api_status():
    # Проверяем функциональность JSON эндпоинта
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "node_name" in data