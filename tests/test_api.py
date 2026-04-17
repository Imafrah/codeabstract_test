from fastapi.testclient import TestClient

from codeabstract.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_abstract_and_translate_endpoints():
    source = "api_key='x'\ndef calc(amount):\n    return amount\n"
    response = client.post("/api/v1/abstract", json={"source_code": source, "privacy_level": "HIGH"})
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    abstract_code = response.json()["abstract_code"]
    assert "FUNCTION_" in abstract_code

    response2 = client.post(
        "/api/v1/translate",
        json={"session_id": session_id, "llm_response": "Issue in FUNCTION_0"},
    )
    assert response2.status_code == 200
    assert "calc" in response2.json()["translated_response"]


def test_translate_from_original_endpoint():
    source = "api_key='x'\ndef calc(a):\n    return a + api_key\n"
    llm_response = "There is a bug in FUNCTION_0."
    response = client.post(
        "/api/v1/translate-from-original",
        json={"source_code": source, "privacy_level": "HIGH", "llm_response": llm_response},
    )
    assert response.status_code == 200
    data = response.json()
    assert "calc" in data["translated_response"]

