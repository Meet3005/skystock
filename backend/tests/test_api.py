
from backend.app import app


def test_home_endpoint():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json()["app"] == "SkyStock"


def test_missing_sku():
    client = app.test_client()

    response = client.post("/api/products", json={
        "name": "Test Product",
        "price": "10.00",
        "quantity": 5
    })

    assert response.status_code == 400


def test_negative_quantity():
    client = app.test_client()

    response = client.post("/api/products", json={
        "sku": "TEST-001",
        "name": "Test Product",
        "price": "10.00",
        "quantity": -5
    })

    assert response.status_code == 400


def test_invalid_price():
    client = app.test_client()

    response = client.post("/api/products", json={
        "sku": "TEST-002",
        "name": "Test Product",
        "price": "12.345",
        "quantity": 5
    })

    assert response.status_code == 400


def test_zero_stock_adjustment():
    client = app.test_client()

    response = client.post(
        "/api/products/1/adjust",
        json={
            "quantity_change": 0,
            "reason": "Invalid adjustment"
        }
    )

    assert response.status_code == 400
