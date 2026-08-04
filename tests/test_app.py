import io
import pytest
from unittest.mock import patch

from app1 import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ------------------------
# Home Page
# ------------------------
def test_index(client):
    response = client.get("/")
    assert response.status_code == 200


# ------------------------
# Translate API
# ------------------------
@patch("app1.GoogleTranslator")
def test_translate_success(mock_translator, client):
    mock_translator.return_value.translate.return_value = "नमस्ते"

    response = client.post(
        "/api/translate",
        json={
            "text": "Hello",
            "source": "en",
            "target": "hi"
        }
    )

    assert response.status_code == 200
    data = response.get_json()

    assert data["success"] is True
    assert data["translated_text"] == "नमस्ते"


def test_translate_empty_text(client):
    response = client.post(
        "/api/translate",
        json={
            "text": "",
            "source": "en",
            "target": "hi"
        }
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


@patch("app1.GoogleTranslator")
def test_translate_exception(mock_translator, client):
    mock_translator.return_value.translate.side_effect = Exception("Translation Error")

    response = client.post(
        "/api/translate",
        json={
            "text": "Hello",
            "source": "en",
            "target": "hi"
        }
    )

    assert response.status_code == 500


# ------------------------
# Text To Speech
# ------------------------
@patch("app1.gTTS")
def test_tts_success(mock_gtts, client):

    def fake_write(fp):
        fp.write(b"audio data")

    mock_gtts.return_value.write_to_fp.side_effect = fake_write

    response = client.post(
        "/api/tts",
        json={
            "text": "Hello",
            "lang": "en"
        }
    )

    assert response.status_code == 200
    assert response.mimetype == "audio/mpeg"


def test_tts_empty_text(client):
    response = client.post(
        "/api/tts",
        json={
            "text": "",
            "lang": "en"
        }
    )

    assert response.status_code == 400


@patch("app1.gTTS")
def test_tts_exception(mock_gtts, client):
    mock_gtts.side_effect = Exception("TTS Error")

    response = client.post(
        "/api/tts",
        json={
            "text": "Hello",
            "lang": "en"
        }
    )

    assert response.status_code == 500


@patch("app1.gTTS")
def test_tts_invalid_language(mock_gtts, client):

    def fake_write(fp):
        fp.write(b"audio")

    mock_gtts.return_value.write_to_fp.side_effect = fake_write

    response = client.post(
        "/api/tts",
        json={
            "text": "Hello",
            "lang": "invalid_lang"
        }
    )

    assert response.status_code == 200