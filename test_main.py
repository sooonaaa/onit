import pytest
import psycopg2
import os
from fastapi.testclient import TestClient
from main import app, get_db_conn

client = TestClient(app)

# Исправлено: autouse=True (автоматический запуск)
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS tasks (id SERIAL PRIMARY KEY, title TEXT);")
    conn.commit()
    cur.close()
    conn.close()

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "Список задач" in response.text

def test_api_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    assert response.json()["status"] == "online"