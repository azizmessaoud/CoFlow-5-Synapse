from __future__ import annotations

from collections import Counter
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / ".scratch" / "coflow5-ideate-finalize" / "spec.md"

PERSONAS = ("Amara", "David", "Chidi", "Rosa", "Marcus", "Yuki", "Omar")
PREFIXES = {
    "Amara": "AM",
    "David": "DV",
    "Chidi": "CH",
    "Rosa": "RO",
    "Marcus": "MC",
    "Yuki": "YK",
    "Omar": "OM",
}
EXPECTED_NOW = {"AM-02", "DV-02", "CH-03", "RO-02", "MC-02", "YK-02", "OM-02"}
MATRIX_HEADERS = [
    "idea_id",
    "persona",
    "pain / HMW",
    "insight",
    "data needed",
    "honesty label",
    "agent (A1–A5 / Synapse±sub)",
    "evidence / metric",
    "architecture fit (Carry / Stretch / Break)",
    "future risk if shipped",
    "Now / Later / Reject",
    "reason",
]
ALLOWED_AGENTS = {
    "A1",
    "A2",
    "A3",
    "A4",
    "A5",
    "Synapse",
    "Synapse-data-quality",
    "Synapse-research",
    "Synapse-explanation",
}


def text() -> str:
    assert SPEC.exists(), f"missing Ideate artifact: {SPEC}"
    return SPEC.read_text(encoding="utf-8")


def table_after(source: str, header_start: str) -> tuple[list[str], list[dict[str, str]]]:
    lines = source.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(header_start))
    headers = [cell.strip() for cell in lines[start].strip("|").split("|")]
    assert set(lines[start + 1]) <= {"|", "-", ":"}, lines[start + 1]
    rows: list[dict[str, str]] = []
    for line in lines[start + 2 :]:
        if not line.startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        assert len(cells) == len(headers), (line, len(cells), len(headers))
        rows.append(dict(zip(headers, cells, strict=True)))
    return headers, rows


def test_capture_roster_and_required_sections() -> None:
    source = text()
    for required in (
        "**CAPTURE 1=d:**",
        "**CAPTURE 2=b:**",
        "**CAPTURE 3=b:**",
        "**HMW:**",
        "**ADR-0001:**",
        "## A. Decision matrix — source of truth",
        "## B. Per-persona ideation — architecture lens",
        "## C. Omar / A4 anomaly detection — Ideate on its own",
        "## D. Data collection ideation — Now versus Later",
        "## E. Future problems the architecture has not yet faced",
        "## F. Architecture convergence — finalized card",
        "## G. Ideate techniques and convergence record",
    ):
        assert required in source
    for index, persona in enumerate(PERSONAS, start=1):
        assert f"P{index}" in source and persona in source
    assert "Maria and Leila are not personas" in source
    assert "I-7 is a deferred optional A5 system KPI with no persona" in source


def test_decision_matrix_has_eight_traceable_ideas_per_persona() -> None:
    headers, rows = table_after(text(), "| idea_id | persona | pain / HMW |")
    assert headers == MATRIX_HEADERS
    assert len(rows) == 56
    assert len({row["idea_id"] for row in rows}) == 56

    counts = Counter(row["persona"] for row in rows)
    assert counts == Counter({persona: 8 for persona in PERSONAS})
    assert not ({"Maria", "Leila"} & counts.keys())

    for row in rows:
        persona = row["persona"]
        assert row["idea_id"].startswith(PREFIXES[persona] + "-")
        assert re.fullmatch(r"[A-Z]{2}-\d{2}", row["idea_id"])
        insights = row["insight"].split(",")
        assert insights and all(re.fullmatch(r"I-(?:10|[1-9])", item) for item in insights)
        assert row["agent (A1–A5 / Synapse±sub)"] in ALLOWED_AGENTS
        assert row["architecture fit (Carry / Stretch / Break)"] in {"Carry", "Stretch", "Break"}
        assert row["Now / Later / Reject"] in {"Now", "Later", "Reject"}
        for required_column in MATRIX_HEADERS[2:]:
            assert row[required_column], (row["idea_id"], required_column)
        if row["architecture fit (Carry / Stretch / Break)"] == "Break":
            assert row["Now / Later / Reject"] == "Reject"

    now_rows = {row["idea_id"] for row in rows if row["Now / Later / Reject"] == "Now"}
    assert now_rows == EXPECTED_NOW
    assert all(row["insight"] != "I-7" for row in rows)


def test_persona_sections_and_presentation_derive_from_now_rows() -> None:
    source = text()
    persona_headings = re.findall(r"^### B\.\d+ (\w+) —", source, flags=re.MULTILINE)
    assert tuple(persona_headings) == PERSONAS
    for persona, prefix in PREFIXES.items():
        section_start = source.index(next(line for line in source.splitlines() if line.startswith("### B.") and f" {persona} —" in line))
        next_start = source.find("\n### B.", section_start + 1)
        section = source[section_start : next_start if next_start >= 0 else source.index("\n---\n\n## C.")]
        idea_ids = set(re.findall(rf"\b{prefix}-\d{{2}}\b", section))
        assert idea_ids == {f"{prefix}-{number:02d}" for number in range(1, 9)}
        for field in (
            "Need / HMW",
            "Insight IDs",
            "Brainstorm 8",
            "Worst Possible Idea -> invert",
            "Chosen Now line",
            "Later / Reject",
            "Data it needs",
            "Metric",
            "Future problem they hit first",
        ):
            assert f"| {field} |" in section

    _, presentation = table_after(source, "| Persona | Say this | Agent | Metric | First failure |")
    assert [
        (row["Persona"], row["Say this"], row["Agent"], row["Metric"], row["First failure"])
        for row in presentation
    ] == [
        ("Amara", "A wait deadline, and the crossing stays protected until she finishes", "A3", "Wait tail, and zero clearance truncations", "A bad occupancy sensor can look like an empty crossing"),
        ("David", "Neighbouring junctions coordinate, and a blocked exit counts", "A1", "P95 travel time, stops, spillback", "Stale news from the next junction can make the queue worse"),
        ("Chidi", "A bus asks for green only after an unusual gap", "A3", "Headway variation, passenger wait, extra car delay", "A storm of bus requests can starve everyone else"),
        ("Rosa", "The page explains why a request was granted or denied, with a citation, or it abstains", "Synapse explanation", "Supported explanation, and abstention", "Fluent text can hide a missing event"),
        ("Marcus", "An authenticated corridor request, then recovery after he passes", "A2", "Ambulance time, civilian delay, recovery, safety", "A spoofed or replayed request can disrupt the corridor"),
        ("Yuki", "Health, fallback, and the safety interlock stay visible", "A1", "Fallback time, complete log, interlock intact", "A frozen screen can look healthy while control has already fallen back"),
        ("Omar", "A residual alert with an explicit statement of whether the sensors can see", "A4", "Detection delay, false alarms, misses, recovery, by severity", "Stale, missing, invalid, or poisoned data can be shown as a normal road"),
    ]
    source_rows = source[source.index("**Source rows:**") : source.index("\n\n**Close on Omar:**")]
    assert set(re.findall(r"[A-Z]{2}-\d{2}", source_rows)) == EXPECTED_NOW
    assert "**Close on Omar:** The highest-risk failure is presenting a network we cannot see as a healthy network." in source
    assert "**Roster and authority:** The roster is seven personas. Yuki is P6. Maria and Leila are not personas. A1 still writes every signal. The explanation page never reaches the simulator." in source


def test_omar_alert_contract_and_data_roadmap_are_honest() -> None:
    source = text()
    for anomaly_class in (
        "Incident injection",
        "Sensor failure",
        "Demand surge",
        "Weather regime shift",
        "Stale data",
        "Message loss",
        "Unusual headway",
        "Spillback onset",
    ):
        assert anomaly_class in source
    for method in (
        "EWMA on forecast residual",
        "CUSUM on forecast residual",
        "Change-point detection",
        "Isolation method",
        "Weather-conditioned baseline",
        "Multi-source fusion",
    ):
        assert method in source
    for field in (
        "run_id",
        "scenario_hash",
        "message_id",
        "expires_at",
        "anomaly_class",
        "alert_state",
        "severity",
        "observed_values",
        "expected_values",
        "residual_values",
        "detector_method",
        "confidence",
        "data_quality_state",
        "max_data_age_seconds",
        "alternate_explanations",
        "reason_codes",
        "bounded_recommendation",
        "recovery_state",
    ):
        assert re.search(rf"^  {re.escape(field)}(?:\s|$)", source, flags=re.MULTILINE)
    assert "`normal` is forbidden when a required source is stale, missing, invalid, or untrusted" in source
    assert "it never contains a signal command" in source

    _, data_rows = table_after(source, "| Data class | Now source | Later connector |")
    expected_classes = {
        "Road geometry / maps",
        "Intersections / plans",
        "Scheduled transit",
        "Accidents / incidents",
        "Weather",
        "Volumes / speeds",
        "Spacing / headway",
        "Pedestrian demand",
        "Emission proxies",
        "Heatmaps",
    }
    assert len(data_rows) == 10
    assert {row["Data class"] for row in data_rows} == expected_classes
    for row in data_rows:
        assert row["Now source"] and row["Later connector"]
        assert row["Dirty-data risk"] and row["Honesty label"]
    for official_rule in ("**OSM:**", "**GTFS Schedule:**", "**Open-Meteo history:**", "**FHWA TIM:**", "**TRANSTU:**"):
        assert official_rule in source


def test_future_risks_convergence_and_claim_flags() -> None:
    source = text()
    _, risks = table_after(source, "| risk_id | Cluster | Future problem |")
    assert len(risks) == 24
    assert {row["risk_id"] for row in risks} == {f"FP-{number:02d}" for number in range(1, 25)}
    assert {row["Cluster"] for row in risks} == {
        "Data / sensing",
        "Control / safety",
        "Multi-agent coordination",
        "Anomaly / trust",
        "Burden / trade-offs",
        "Operations / adoption",
        "Evaluation honesty",
        "Security / misuse",
    }
    assert all(row["First persona affected"] in PERSONAS for row in risks)
    assert all(row["Architecture stress"] in {"Carry", "Stretch", "Break"} for row in risks)

    for boundary in (
        "A1 Flow | Sole actuator; cooperative Max-Pressure; deterministic safety mask",
        "A2 Emergency | Publishes authenticated, expiring corridor pre-clear",
        "A3 Multimodal | Publishes pedestrian clearance/deadline state",
        "A4 Situation | Publishes forecast residuals, anomaly/degradation alerts",
        "A5 Sustainability | Publishes optional stop/emission-proxy",
        "Synapse plus bounded sub-agents | Retrieve, research allow-listed sources",
        "No TraCI, executor, active mutation",
    ):
        assert boundary in source
    assert source.count("| Reject |") >= 3
    assert "Safety 25%, Honesty 20%, Persona fit 20%, Feasibility 15%, Auditability 10%, Architecture fit 10%" in source
    assert "Any `Break` or failed safety/honesty condition is rejected regardless of total" in source

    for claim_flag in (
        "No lives saved are inferred from simulated emergency travel time.",
        "emission proxies, not measured air quality or exposure.",
        "Scraped news and map displays are not ground-truth incidents",
        "it does not establish accident prevention.",
        "No best-episode or one-seed superiority headline is allowed.",
    ):
        assert claim_flag in source
