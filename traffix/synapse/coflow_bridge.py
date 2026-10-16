"""
CoFlow Synapse over the traffix decision log.

The traffix hierarchy (masters + supermaster) writes one decision log per run.
This bridge turns each logged decision into a CoFlow `EvidenceEvent` and hands
them to CoFlow's `SynapseService`, which answers with:

  verified   the decision's reason code is in the policy corpus (REASON_CODES)
  template   no policy citation, answer built from the recorded facts only
  abstain    the decision id is not in this run's log, or a claim is unsupported

Every answer carries seven-field provenance (run, scenario hash, event, message,
bundle digest, corpus hash, query hash). Like the rest of traffix/synapse/, it
only reads a finished or live decision log: no path to the simulation, the
executor or a master (scripts/check_architecture.py enforces this).
"""
import hashlib
import json
import os
import sys

from ..core.decision_log import REASON_CODES

try:
    from coflow5.synapse import EvidenceEvent, SynapseService
except ImportError:  # running from scripts/ without `pip install -e .`
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), "src"))
    from coflow5.synapse import EvidenceEvent, SynapseService


def _digest(value):
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


CORPUS_HASH = _digest(REASON_CODES)


class TraffixSynapse:
    """Read-only explanations of one run's decisions, keyed by decision id."""

    def __init__(self, entries, *, run_id, scenario=None, tally=None):
        self.run_id = run_id
        self.scenario = scenario
        # Request counters shared by every refresh of the same live run.
        self.tally = tally if tally is not None else {"verified": 0, "template": 0, "abstain": 0}
        self.entries = {e["id"]: dict(e) for e in entries}
        self.scenario_hash = _digest(scenario or {})
        self.bundle_digest = _digest(list(self.entries.values()))
        events = {self.event_id(i): self._event(e) for i, e in self.entries.items()}
        self.service = SynapseService(events=events, policies=REASON_CODES, corpus_hash=CORPUS_HASH,
                                      endpoint="traffix-decisions")

    def refreshed(self, entries):
        """Same run with a longer log: new evidence bundle, same request counters."""
        return TraffixSynapse(entries, run_id=self.run_id, scenario=self.scenario, tally=self.tally)

    @classmethod
    def from_log_file(cls, path, events_file=None):
        with open(path, encoding="utf-8") as f:
            entries = [json.loads(line) for line in f if line.strip()]
        scenario = None
        if events_file and os.path.exists(events_file):
            with open(events_file, encoding="utf-8") as f:
                scenario = json.load(f)
        run_id = os.path.basename(path).removeprefix("decisions_").removesuffix(".jsonl")
        return cls(entries, run_id=run_id, scenario=scenario)

    def event_id(self, decision_id):
        return f"{self.run_id}#{decision_id}"

    def _event(self, e):
        where = f" at {e['tls']}" if e.get("tls") else ""
        return EvidenceEvent(
            run_id=self.run_id,
            scenario_hash=self.scenario_hash,
            event_id=self.event_id(e["id"]),
            message_id=None,
            bundle_digest=self.bundle_digest,
            # Only distinctive facts: SynapseService.audit accepts a claim that
            # mentions any fact, so a bare junction id or number would let
            # unrelated claims through. Details stay in the returned decision.
            facts={"simulation_time": f"t={e['t']}s", "selected_action": f"{e['event']}{where}",
                   "reason_code": e["reason"], "agent": e["agent"]},
        )

    def explain(self, question, decision_id):
        result = self.service.explain(question, event_id=self.event_id(decision_id),
                                      policy_id=self.entries.get(decision_id, {}).get("reason"))
        return self._payload(result, decision_id)

    def audit(self, claim, decision_id):
        result = self.service.audit(claim, event_id=self.event_id(decision_id),
                                    policy_id=self.entries.get(decision_id, {}).get("reason"))
        return self._payload(result, decision_id)

    def metrics(self):
        requests = sum(self.tally.values())
        return {"request_count": requests, **{f"{k}_count": v for k, v in self.tally.items()},
                "abstention_rate": self.tally["abstain"] / requests if requests else 0.0,
                "fallback_rate": (self.tally["template"] + self.tally["abstain"]) / requests
                if requests else 0.0,
                "decisions": len(self.entries), "bundle_digest": self.bundle_digest}

    def _payload(self, result, decision_id):
        self.tally[result.fallback] += 1
        e = self.entries.get(decision_id)
        out = {"fallback": result.fallback, "answer": result.answer,
               "citations": list(result.citations), "provenance": result.provenance.as_dict()}
        if e is not None and result.fallback != "abstain":
            where = f" at {e['tls']}" if e.get("tls") else ""
            out["decision"] = e
            out["explanation"] = (f"[#{e['id']}] t={e['t']}s, {e['agent']} {e['event']}{where}: "
                                  f"{REASON_CODES[e['reason']]}")
        return out
