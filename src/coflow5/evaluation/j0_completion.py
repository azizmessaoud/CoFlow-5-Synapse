from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

REQUIRED_CONTROLLERS = frozenset(
    {"cooperative-max-pressure", "actuated", "fixed-time"}
)
REQUIRED_ABLATIONS = frozenset({"A2", "A3", "A4", "A5"})
MINIMUM_MATCHED_SEEDS = 5
REQUIRED_RUN_PROVENANCE = frozenset({"event_ids", "message_ids"})
REQUIRED_FAILURE_KINDS = frozenset(
    {"specialist", "controller", "communication", "forecast", "synapse"}
)


@dataclass(frozen=True)
class J0CompletionFinding:
    code: str
    detail: str


@dataclass(frozen=True)
class J0CompletionAudit:
    pass_gate: bool
    matched_seeds: tuple[int, ...]
    findings: tuple[J0CompletionFinding, ...]


def audit_j0_completion(
    runs: Iterable[Mapping[str, object]],
    ablations: Iterable[Mapping[str, object]],
    recovery_events: Iterable[Mapping[str, object]],
    *,
    repeat_checks: Iterable[Mapping[str, object]] = (),
) -> J0CompletionAudit:
    """Validate the frozen J0 completion boundary without creating evidence.

    Inputs are already-produced immutable evidence rows. Missing evidence is
    retained as a finding so a partial pack cannot be presented as complete.
    """
    run_rows = tuple(runs)
    findings: list[J0CompletionFinding] = []
    scenario_hash_values = [row.get("scenario_hash") for row in run_rows]
    scenario_hashes = {str(value) for value in scenario_hash_values}
    if (
        not scenario_hash_values
        or any(not isinstance(value, str) or not value for value in scenario_hash_values)
        or len(scenario_hashes) != 1
    ):
        findings.append(J0CompletionFinding(
            "SCENARIO_NOT_MATCHED",
            "all controller rows must share exactly one scenario_hash",
        ))

    by_seed: dict[int, set[str]] = {}
    for row in run_rows:
        if (
            not row.get("run_id")
            or any(
                not isinstance(row.get(field), (list, tuple))
                for field in REQUIRED_RUN_PROVENANCE
            )
        ):
            findings.append(J0CompletionFinding(
                "RUN_PROVENANCE_MISSING",
                "each run requires run_id, event_ids, and message_ids",
            ))
        try:
            seed = int(row["seed"])
            controller = str(row["controller"])
        except (KeyError, TypeError, ValueError):
            findings.append(J0CompletionFinding(
                "RUN_IDENTITY_INVALID",
                "each run requires integer seed and controller",
            ))
            continue
        by_seed.setdefault(seed, set()).add(controller)

    matched = tuple(sorted(
        seed for seed, controllers in by_seed.items()
        if REQUIRED_CONTROLLERS <= controllers
    ))
    if len(matched) < MINIMUM_MATCHED_SEEDS:
        findings.append(J0CompletionFinding(
            "MATCHED_SEEDS_INSUFFICIENT",
            f"required {MINIMUM_MATCHED_SEEDS}, observed {len(matched)}",
        ))

    for seed, controllers in sorted(by_seed.items()):
        missing = sorted(REQUIRED_CONTROLLERS - controllers)
        if missing:
            findings.append(J0CompletionFinding(
                "CONTROLLER_CELL_MISSING",
                f"seed {seed} missing {', '.join(missing)}",
            ))

    ablation_rows = tuple(ablations)
    ablation_pairs = {
        (str(row.get("agent")), row.get("enabled"))
        for row in ablation_rows
        if isinstance(row.get("enabled"), bool)
    }
    for agent in sorted(REQUIRED_ABLATIONS):
        if (agent, True) not in ablation_pairs or (agent, False) not in ablation_pairs:
            findings.append(J0CompletionFinding(
                "ABLATION_PAIR_MISSING",
                f"{agent} requires explicit on and off cells",
            ))
        pair_rows = [
            row for row in ablation_rows if str(row.get("agent")) == agent
        ]
        if any(
            not row.get("run_id")
            or not isinstance(row.get("event_ids"), (list, tuple))
            or not isinstance(row.get("message_ids"), (list, tuple))
            for row in pair_rows
        ):
            findings.append(J0CompletionFinding(
                "ABLATION_PROVENANCE_MISSING",
                f"{agent} on/off cells require run_id, event_ids, and message_ids",
            ))
        pair_kpis = [
            row.get("kpis")
            for row in pair_rows
            if isinstance(row.get("kpis"), Mapping)
        ]
        if len(pair_kpis) < 2 or not _has_numeric_kpi_pair(pair_kpis):
            findings.append(J0CompletionFinding(
                "ABLATION_KPI_COMPARISON_MISSING",
                f"{agent} requires numeric KPI values for on and off cells",
            ))

    def _mode(value: object) -> str:
        normalized = str(value).strip().lower().replace("_", "-")
        return {
            "cooperative-max-pressure": "cooperative",
            "max-pressure": "cooperative",
        }.get(normalized, normalized)

    recovery_modes = {
        (_mode(row.get("previous_mode")), _mode(row.get("next_mode")))
        for row in recovery_events
    }
    required_transitions = {
        ("cooperative", "actuated"),
        ("actuated", "fixed-time"),
    }
    missing_transitions = sorted(required_transitions - recovery_modes)
    if missing_transitions:
        findings.append(J0CompletionFinding(
            "RECOVERY_TRANSITION_MISSING",
            f"missing transitions: {missing_transitions}",
        ))
    failure_kinds = {
        str(row.get("failure_kind")).strip().lower()
        for row in recovery_events
        if row.get("failure_kind")
    }
    recovery_event_ids = [
        row.get("event_id") for row in recovery_events if row.get("event_id")
    ]
    if len(recovery_event_ids) != len(set(recovery_event_ids)):
        findings.append(J0CompletionFinding(
            "RECOVERY_EVENT_ID_DUPLICATE",
            "recovery rows require unique event_id values",
        ))
    missing_failures = sorted(REQUIRED_FAILURE_KINDS - failure_kinds)
    if missing_failures:
        findings.append(J0CompletionFinding(
            "FAILURE_CASE_MISSING",
            f"missing failure cases: {missing_failures}",
        ))

    checks = tuple(repeat_checks)
    if not checks or any(
        not bool(check.get("compatible"))
        or not bool(check.get("action_hash_equal"))
        or not bool(check.get("within_tolerance"))
        for check in checks
    ):
        findings.append(J0CompletionFinding(
            "DETERMINISM_CHECK_MISSING",
            "compatible repeated runs must have equal action hashes within tolerance",
        ))

    return J0CompletionAudit(
        pass_gate=not findings,
        matched_seeds=matched,
        findings=tuple(findings),
    )


def _has_numeric_kpi_pair(kpis: list[Mapping[str, object]]) -> bool:
    shared_keys = set(kpis[0]).intersection(kpis[1])
    return any(
        isinstance(kpis[0][key], (int, float))
        and isinstance(kpis[1][key], (int, float))
        for key in shared_keys
    )
