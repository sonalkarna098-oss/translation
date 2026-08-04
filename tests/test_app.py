import pytest
from app1 import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200


def test_translate_empty(client):
    response = client.post(
        "/api/translate",
        json={
            "text": "",
            "source": "en",
            "target": "hi"
        }
    )

    assert response.status_code == 400


def test_tts_empty(client):
    response = client.post(
        "/api/tts",
        json={
            "text": "",
            "lang": "en"
        }
    )

    assert response.status_code == 400