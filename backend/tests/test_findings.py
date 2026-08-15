import uuid

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_finding_invalid_severity():
    response = client.post(
        "/api/v1/findings/",
        json={
            "inspection_id": "13f9f740-495b-4cd7-ba38-214c084e285b",
            "component_id": "92420d46-6a96-4c6b-acf1-f16f6743d402",
            "defect_type": "Crack",
            "description": "Test finding",
            "severity": "banana",
            "confidence": 0.94,
        },
    )

    assert response.status_code == 422


def test_create_finding_invalid_confidence():
    response = client.post(
        "/api/v1/findings/",
        json={
            "inspection_id": "13f9f740-495b-4cd7-ba38-214c084e285b",
            "component_id": "92420d46-6a96-4c6b-acf1-f16f6743d402",
            "defect_type": "Crack",
            "description": "Test finding",
            "severity": "critical",
            "confidence": 1.5,
        },
    )

    assert response.status_code == 422