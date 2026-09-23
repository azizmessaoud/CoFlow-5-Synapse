import assert from "node:assert/strict";
import test from "node:test";

import {
  auditRows,
  comparisonRows,
  explanationRows,
  frameRows,
  limitationLines,
  reasonRows,
  recoveryState,
} from "./evidence.js";

const RUN = "0db24e7b-133e-5b79-ba0c-171f1c0aaf34";
const EVENT = "9fa9db22-b826-53cc-92eb-319b50688327";
const CHUNK = "chunk-be5c0ee6ccf20069fa4c3dc6d7f4f052744c763bbc4f9d1c0591317317134a6a";

test("controller comparison keeps unfinished trips", () => {
  const rows = comparisonRows({
    items: [
      {
        controller: "graph-aware-cooperative-max-pressure",
        seed: 11,
        demand_scale: 1.5,
        planned_trips: 20,
        completed_trips: 12,
        unfinished_trips: 8,
      },
    ],
  });
  assert.equal(rows[0].unfinished, 8);
  assert.equal(rows[0].controller, "graph-aware-cooperative-max-pressure");
});

test("reason rows keep event and message identities", () => {
  const rows = reasonRows({
    items: [{ event_id: EVENT, message_id: null, reason_code: "GRAPH_NEIGHBOUR_USED", run_id: RUN }],
  });
  assert.equal(rows[0].eventId, EVENT);
  assert.equal(rows[0].messageId, null);
  assert.equal(rows[0].runId, RUN);
  assert.equal(recoveryState({ items: [] }), "No recovery transition is in this page.");
});

test("graph frames say when freshness was not recorded", () => {
  const rows = frameRows({
    items: [
      {
        simulation_time: 0,
        mode: "graph-aware-cooperative-max-pressure",
        run_id: RUN,
        scenario_hash: "sha256:scenario",
        graph_hash: "sha256:graph",
        nodes_json: JSON.stringify([{ signal_id: "J0", phase_id: "NS_GREEN" }]),
        edges_json: JSON.stringify([{ edge_id: "internal-0", occupancy_ratio: 0.4 }]),
      },
    ],
  });
  assert.equal(rows[0].freshness, "not recorded");
  assert.equal(rows[0].nodes[0].phase_id, "NS_GREEN");
  assert.equal(rows[0].graphHash, "sha256:graph");
});

test("explanations keep citations and abstentions", () => {
  const rows = explanationRows({
    items: [
      {
        request_id: "golden-s2-cited",
        status: "answered",
        abstention_reason: null,
        event_facts: { event_id: EVENT, run_id: RUN },
        citations: [{ chunk_id: CHUNK, source_id: "adr-0001" }],
      },
      {
        request_id: "golden-s2-abstain",
        status: "abstained",
        abstention_reason: "retrieval-miss",
        event_facts: { event_id: EVENT, run_id: RUN },
        citations: [],
      },
    ],
  });
  assert.equal(rows[0].citations[0].chunkId, CHUNK);
  assert.equal(rows[1].status, "abstained");
  assert.equal(rows[1].abstentionReason, "retrieval-miss");
  assert.deepEqual(auditRows({ items: [{ request_id: "golden-s3-abstain", status: "abstained" }] }), [
    { requestId: "golden-s3-abstain", status: "abstained" },
  ]);
});

test("limitations stay a list of source strings", () => {
  assert.deepEqual(limitationLines({ limitations: ["No lives saved."] }), ["No lives saved."]);
  assert.deepEqual(limitationLines({}), []);
});
