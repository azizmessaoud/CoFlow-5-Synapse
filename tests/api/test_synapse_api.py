from fastapi.testclient import TestClient

from coflow5.api.app import create_app
from coflow5.synapse import EvidenceEvent, SynapseService


def _client() -> TestClient:
    service = SynapseService(
        events={
            "event-1": EvidenceEvent(
                "run-1", "scenario-1", "event-1", "message-1", "bundle-1",
                {"selected_action": "NS_GREEN", "reason_code": "pressure"},
            )
        },
        policies={"policy-1": "policy"},
        corpus_hash="corpus-1",
    )
    return TestClient(create_app(synapse_service=service))


def test_explanation_requires_idempotency_and_returns_typed_abstention() -> None:
    client = _client()
    request = {"question": "Explain", "event_id": "missing"}

    assert client.post("/explanations", json=request).status_code == 400
    response = client.post(
        "/explanations",
        json=request,
        headers={"Idempotency-Key": "key-1"},
    )

    assert response.status_code == 200
    assert response.json()["fallback"] == "abstain"
    assert set(response.json()["provenance"]) == {
        "run_id", "scenario_hash", "event_id", "message_id",
        "bundle_digest", "corpus_hash", "query_hash",
    }


def test_idempotency_replays_the_same_product_response() -> None:
    client = _client()
    request = {"question": "Why?", "event_id": "event-1"}
    first = client.post(
        "/explanations", json=request, headers={"Idempotency-Key": "same"}
    )
    second = client.post(
        "/explanations", json=request, headers={"Idempotency-Key": "same"}
    )

    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()


def test_question_length_is_an_explicit_client_error() -> None:
    response = _client().post(
        "/explanations",
        json={"question": "x" * 2001, "event_id": "event-1"},
        headers={"Idempotency-Key": "long"},
    )

    assert response.status_code == 422
