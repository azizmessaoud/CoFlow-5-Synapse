from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


REQUIRED_CONTROLLERS = frozenset(
    {"cooperative-max-pressure", "actuated", "fixed-time"}
)
REQUIRED_ABLATIONS = frozenset({"A2", "A3", "A4", "A5"})
MINIMUM_MATCHED_SEEDS = 5


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
) -> J0CompletionAudit:
    """Validate the frozen J0 completion boundary without creating evidence.

    Inputs are already-produced immutable evidence rows. Missing evidence is
    retained as a finding so a partial pack cannot be presented as complete.
    """
    run_rows = tuple(runs)
    findings: list[J0CompletionFinding] = []
    scenario_hashes = {str(row.get("scenario_hash")) for row in run_rows}
    if len(scenario_hashes) != 1 or None in scenario_hashes:
        findings.append(J0CompletionFinding(
            "SCENARIO_NOT_MATCHED",
            "all controller rows must share exactly one scenario_hash",
        ))

    by_seed: dict[int, set[str]] = {}
    for row in run_rows:
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

    ablation_pairs = {
        (str(row.get("agent")), bool(row.get("enabled")))
        for row in ablations
    }
    for agent in sorted(REQUIRED_ABLATIONS):
        if (agent, True) not in ablation_pairs or (agent, False) not in ablation_pairs:
            findings.append(J0CompletionFinding(
                "ABLATION_PAIR_MISSING",
                f"{agent} requires explicit on and off cells",
            ))

    recovery_modes = {
        (str(row.get("previous_mode")), str(row.get("next_mode")))
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

    return J0CompletionAudit(
        pass_gate=not findings,
        matched_seeds=matched,
        findings=tuple(findings),
    )
