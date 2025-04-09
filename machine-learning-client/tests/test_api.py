import pytest
from unittest.mock import patch
from api import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@patch("api.detector.detect_food")
def test_detect_food_success(mock_detect_food, client):
    mock_detect_food.return_value = ("Success", ["apple", "banana"])
    response = client.post(
        "/detect-food",
        json={
            "image_data": "fake_base64_data",
            "image_id": "123",
            "image_url": "http://example.com/image.jpg",
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["food_detected"] == ["apple", "banana"]
    assert data["image_id"] == "123"


@patch("api.detector.detect_food")
def test_detect_food_failure(mock_detect_food, client):
    mock_detect_food.return_value = ("Fail", [])
    response = client.post(
        "/detect-food",
        json={
            "image_data": "fake_base64_data",
            "image_id": "123",
            "image_url": "http://example.com/image.jpg",
        },
    )

    assert response.status_code == 500
    data = response.get_json()
    assert data["status"] == "error"


@pytest.mark.parametrize(
    "payload,missing_key",
    [
        ({"image_id": "123", "image_url": "http://example.com"}, "image data"),
        ({"image_data": "abc", "image_url": "http://example.com"}, "image id"),
        ({"image_data": "abc", "image_id": "123"}, "image url"),
    ],
)
def test_detect_food_missing_fields(client, payload, missing_key):
    response = client.post("/detect-food", json=payload)
    assert response.status_code == 400
    assert missing_key in response.get_json()["message"].lower()
