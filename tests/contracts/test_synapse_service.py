from coflow5.synapse import EvidenceEvent, SynapseService


def _service() -> SynapseService:
    event = EvidenceEvent(
        run_id="run-1",
        scenario_hash="sha256:" + "a" * 64,
        event_id="event-1",
        message_id="message-1",
        bundle_digest="sha256:" + "b" * 64,
        facts={
            "simulation_time": 12.0,
            "selected_action": "NS_GREEN",
            "reason_code": "MAX_PRESSURE_LOCAL_ONLY",
        },
    )
    return SynapseService(
        events={"event-1": event},
        policies={"policy-safety": "Safety policy"},
        corpus_hash="sha256:" + "c" * 64,
    )


def test_verified_explanation_has_seven_provenance_fields_and_cache_key() -> None:
    result = _service().explain(
        "Why was NS_GREEN selected?", event_id="event-1", policy_id="policy-safety"
    )

    assert result.fallback == "verified"
    assert set(result.provenance.as_dict()) == {
        "run_id", "scenario_hash", "event_id", "message_id",
        "bundle_digest", "corpus_hash", "query_hash",
    }
    assert result.cache_key[0].startswith("sha256:")
    assert result.citations == ("policy-safety",)


def test_missing_policy_returns_marked_template() -> None:
    result = _service().explain("Explain this", event_id="event-1")

    assert result.fallback == "template"
    assert "policy support missing" in result.answer
    assert result.provenance.corpus_hash


def test_missing_event_and_unsupported_claim_abstain() -> None:
    service = _service()
    assert service.explain("Explain", event_id="missing").fallback == "abstain"
    assert service.audit(
        "The ambulance saved lives", event_id="event-1"
    ).fallback == "abstain"


def test_metrics_make_abstention_and_fallback_rates_first_class() -> None:
    service = _service()
    service.explain("Why?", event_id="event-1")
    service.explain("Why?", event_id="missing")

    metrics = service.metrics()
    assert metrics["request_count"] == 2
    assert metrics["abstention_rate"] == 0.5
    assert metrics["fallback_rate"] == 1.0
    assert metrics["cost_units"] > 0
