from fastapi.testclient import TestClient

from backend.main import app
from ai_core.gemini_generator import GeminiDocumentGenerator

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_generate_with_mock(monkeypatch):
    def fake_generate(self, document_type, parties, terms, effective_date):
        return "EMPLOYMENT CONTRACT\n\n1. PARTIES\nJane Doe"

    monkeypatch.setattr(
        GeminiDocumentGenerator,
        "generate_document",
        fake_generate,
    )

    response = client.post(
        "/generate",
        json={
            "document_type": "Employment Contract",
            "parties": "Jane Doe (Employee), ABC Corp (Employer)",
            "terms": "Payment monthly; Confidentiality applies",
            "effective_date": "2026-09-23",
        },
    )

    assert response.status_code == 200
    assert "EMPLOYMENT CONTRACT" in response.json()["content"]
