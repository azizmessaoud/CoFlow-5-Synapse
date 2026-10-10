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


def test_hosted_has_no_proposal_mutation_surface() -> None:
    response = _client().post("/proposals", json={"run_id": "run-1"})

    assert response.status_code == 405


def test_local_proposal_approval_creates_new_run_lineage() -> None:
    client = TestClient(create_app(profile="LOCAL_RUNNER"))
    # The local profile contract is tested through the API boundary; no signal
    # executor is installed in this app.
    created = client.post("/proposals", json={"run_id": "run-1"})
    assert created.status_code == 201
    proposal_id = created.json()["proposal_id"]
    approved = client.post(f"/proposals/{proposal_id}/approve")
    assert approved.status_code == 200
    assert approved.json()["approved_run_id"] != "run-1"


def test_api_rejects_unbounded_event_and_comparison_requests() -> None:
    client = _client()

    events = client.get("/events", params=[("event_ids", str(i)) for i in range(101)])
    comparisons = client.get(
        "/comparisons", params=[("run_ids", str(i)) for i in range(6)]
    )

    assert events.status_code == 422
    assert comparisons.status_code == 422
