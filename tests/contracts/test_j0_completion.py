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
            })
    return rows


def _ablations() -> list[dict[str, object]]:
    return [
        {"agent": agent, "enabled": enabled}
        for agent in ("A2", "A3", "A4", "A5")
        for enabled in (True, False)
    ]


def _recovery() -> list[dict[str, object]]:
    return [
        {"previous_mode": "cooperative", "next_mode": "actuated"},
        {"previous_mode": "actuated", "next_mode": "fixed-time"},
    ]


def test_j0_completion_passes_only_with_five_matched_seeds_and_all_evidence() -> None:
    audit = audit_j0_completion(_runs((37, 41, 43, 47, 53)), _ablations(), _recovery())

    assert audit.pass_gate
    assert audit.matched_seeds == (37, 41, 43, 47, 53)
    assert audit.findings == ()


def test_j0_completion_retains_missing_cells_as_blocking_findings() -> None:
    audit = audit_j0_completion(
        _runs((37,)),
        [row for row in _ablations() if not (row["agent"] == "A5" and row["enabled"] is False)],
        [{"previous_mode": "cooperative", "next_mode": "actuated"}],
    )

    assert not audit.pass_gate
    codes = {finding.code for finding in audit.findings}
    assert {
        "MATCHED_SEEDS_INSUFFICIENT",
        "ABLATION_PAIR_MISSING",
        "RECOVERY_TRANSITION_MISSING",
    } <= codes
