from coflow5.evaluation.j0_completion import audit_j0_completion


def _runs(seeds: tuple[int, ...]) -> list[dict[str, object]]:
    rows = []
    for seed in seeds:
        for controller in ("cooperative-max-pressure", "actuated", "fixed-time"):
            rows.append({
                "run_id": f"{controller}-{seed}",
                "scenario_hash": "sha256:" + "a" * 64,
                "seed": seed,
                "controller": controller,
                "event_ids": [f"event-{controller}-{seed}"],
                "message_ids": [f"message-{controller}-{seed}"],
            })
    return rows


def _ablations() -> list[dict[str, object]]:
    return [
        {"agent": agent, "enabled": enabled}
        for agent in ("A2", "A3", "A4", "A5")
        for enabled in (True, False)
    ]


def _ablations_with_kpis() -> list[dict[str, object]]:
    return [
        {
            **row,
            "kpis": {"mean_waiting_time_s": 10.0 if row["enabled"] else 12.0},
        }
        for row in _ablations()
    ]


def _recovery() -> list[dict[str, object]]:
    return [
        {"previous_mode": "cooperative", "next_mode": "actuated"},
        {"previous_mode": "actuated", "next_mode": "fixed-time"},
    ]


def test_j0_completion_passes_only_with_five_matched_seeds_and_all_evidence() -> None:
    audit = audit_j0_completion(
        _runs((37, 41, 43, 47, 53)), _ablations_with_kpis(), _recovery()
    )

    assert audit.pass_gate
    assert audit.matched_seeds == (37, 41, 43, 47, 53)
    assert audit.findings == ()


def test_j0_completion_retains_missing_cells_as_blocking_findings() -> None:
    audit = audit_j0_completion(
        _runs((37,)),
        [
            row
            for row in _ablations_with_kpis()
            if not (row["agent"] == "A5" and row["enabled"] is False)
        ],
        [{"previous_mode": "cooperative", "next_mode": "actuated"}],
    )

    assert not audit.pass_gate
    codes = {finding.code for finding in audit.findings}
    assert {
        "MATCHED_SEEDS_INSUFFICIENT",
        "ABLATION_PAIR_MISSING",
        "RECOVERY_TRANSITION_MISSING",
    } <= codes


def test_j0_completion_rejects_missing_scenario_hash() -> None:
    rows = _runs((37, 41, 43, 47, 53))
    rows[0].pop("scenario_hash")

    audit = audit_j0_completion(rows, _ablations_with_kpis(), _recovery())

    assert not audit.pass_gate
    assert "SCENARIO_NOT_MATCHED" in {finding.code for finding in audit.findings}


def test_j0_completion_normalizes_native_recovery_mode_names() -> None:
    recovery = [
        {
            "previous_mode": "COOPERATIVE_MAX_PRESSURE",
            "next_mode": "ACTUATED",
        },
        {"previous_mode": "ACTUATED", "next_mode": "FIXED_TIME"},
    ]

    audit = audit_j0_completion(
        _runs((37, 41, 43, 47, 53)), _ablations_with_kpis(), recovery
    )

    assert audit.pass_gate


def test_j0_completion_requires_join_identifiers_on_every_run() -> None:
    rows = _runs((37, 41, 43, 47, 53))
    rows[0].pop("message_ids")

    audit = audit_j0_completion(rows, _ablations_with_kpis(), _recovery())

    assert not audit.pass_gate
    assert "RUN_PROVENANCE_MISSING" in {finding.code for finding in audit.findings}


def test_j0_completion_requires_pairwise_numeric_kpis() -> None:
    ablations = _ablations_with_kpis()
    ablations[0].pop("kpis")

    audit = audit_j0_completion(_runs((37, 41, 43, 47, 53)), ablations, _recovery())

    assert not audit.pass_gate
    assert "ABLATION_KPI_COMPARISON_MISSING" in {
        finding.code for finding in audit.findings
    }
