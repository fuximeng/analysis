from app import app


def test_index():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200

    data = response.get_json()

    assert data["code"] == 200
    assert data["message"] == "E-commerce Analysis System is running"


def test_health():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["code"] == 200
    assert data["message"] == "ok"
    assert data["data"]["service"] == "flask"