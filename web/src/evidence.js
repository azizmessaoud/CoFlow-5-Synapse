export function comparisonRows(kpis) {
  const items = Array.isArray(kpis?.items) ? kpis.items : [];
  return items.map((row) => ({
    controller: row.controller ?? "",
    seed: row.seed ?? "",
    demandScale: row.demand_scale ?? "",
    planned: row.planned_trips ?? null,
    completed: row.completed_trips ?? null,
    unfinished: row.unfinished_trips ?? null,
  }));
}

export function reasonRows(events) {
  const items = Array.isArray(events?.items) ? events.items : [];
  return items.map((row) => ({
    eventId: row.event_id,
    messageId: Object.prototype.hasOwnProperty.call(row, "message_id") ? row.message_id : null,
    reason: row.reason_code ?? "",
    action: row.accepted_action ?? "",
    downstreamBlocked: Object.prototype.hasOwnProperty.call(row, "downstream_blocked")
      ? row.downstream_blocked
      : null,
    runId: row.run_id,
  }));
}

export function recoveryState(events) {
  const rows = reasonRows(events);
  const hit = rows.find((row) => /fallback|recover/i.test(row.reason));
  if (!hit) {
    return "No recovery transition is in this page.";
  }
  return `${hit.reason} on event ${hit.eventId}`;
}

function parsed(value) {
  if (typeof value !== "string") {
    return value ?? [];
  }
  try {
    return JSON.parse(value);
  } catch {
    return [];
  }
}

export function frameRows(frames) {
  const items = Array.isArray(frames?.items) ? frames.items : [];
  return items.map((row) => ({
    time: row.simulation_time,
    mode: row.mode ?? "",
    freshness: row.freshness ?? row.graph_freshness ?? "not recorded",
    runId: row.run_id,
    scenarioHash: row.scenario_hash,
    graphHash: row.graph_hash,
    nodes: parsed(row.nodes_json),
    edges: parsed(row.edges_json),
  }));
}

export function explanationRows(explanations) {
  const items = Array.isArray(explanations?.items) ? explanations.items : [];
  return items.map((row) => ({
    requestId: row.request_id,
    status: row.status ?? "",
    abstentionReason: row.abstention_reason ?? null,
    eventId: row.event_facts?.event_id,
    runId: row.event_facts?.run_id ?? row.run_id,
    citations: Array.isArray(row.citations)
      ? row.citations.map((citation) => ({
          chunkId: citation.chunk_id,
          sourceId: citation.source_id ?? "",
        }))
      : [],
  }));
}

export function auditRows(audits) {
  const items = Array.isArray(audits?.items) ? audits.items : [];
  return items.map((row) => ({
    requestId: row.request_id,
    status: row.status ?? "",
  }));
}

export function limitationLines(payload) {
  return Array.isArray(payload?.limitations) ? payload.limitations : [];
}

export function unavailableDetail(body) {
  if (body && body.error === "unavailable") {
    return body.detail || "unavailable";
  }
  return "";
}

const PEOPLE = [
  ["amara", "Amara", "Enough time to finish the crossing."],
  ["david", "David", "A trip time he can plan around, including trips that do not finish."],
  ["chidi", "Chidi", "A bus helped only after an unusual gap."],
  ["rosa", "Rosa", "Why a request was granted or refused, or an abstention."],
  ["marcus", "Marcus", "Room at the exit, then recovery after the ambulance."],
  ["yuki", "Yuki", "Whether control is healthy or has fallen back."],
  ["omar", "Omar", "Whether the sensors can see, without naming a cause."],
];

function matchingReasons(reasons, pattern) {
  return reasons.filter((row) => pattern.test(row.reason || ""));
}

export function personaCards({ comparisons = [], reasons = [], frames = [], explanations = [], recovery = "", opened = false }) {
  return PEOPLE.map(([id, name, helps]) => ({
    id,
    name,
    helps,
    text: opened ? personaText(id, { comparisons, reasons, frames, explanations, recovery }) : "Open a run. This card reads that record.",
  }));
}

function personaText(id, view) {
  if (id === "amara") {
    const hits = matchingReasons(view.reasons, /pedestrian|clearance|crossing/i);
    if (hits.length === 0) {
      return "No crossing record is in this run.";
    }
    return `${hits[0].reason} on event ${hits[0].eventId}.`;
  }
  if (id === "david") {
    if (view.comparisons.length === 0) {
      return "No trip counts are in this run.";
    }
    const row = view.comparisons[0];
    return `${row.controller}: ${row.unfinished} unfinished of ${row.planned} planned, ${row.completed} completed.`;
  }
  if (id === "chidi") {
    const hits = matchingReasons(view.reasons, /bus|headway|transit/i);
    if (hits.length === 0) {
      return "No bus request is in this run.";
    }
    return `${hits[0].reason} on event ${hits[0].eventId}.`;
  }
  if (id === "rosa") {
    if (view.explanations.length === 0) {
      return "No explanation cites this run.";
    }
    return view.explanations.map((row) => {
      if (row.status === "abstained") {
        return `${row.requestId} abstained${row.abstentionReason ? `: ${row.abstentionReason}` : ""}.`;
      }
      const cited = row.citations.length;
      return `${row.requestId} ${row.status} with ${cited} citation${cited === 1 ? "" : "s"}.`;
    }).join(" ");
  }
  if (id === "marcus") {
    const blocked = view.reasons.filter((row) => row.downstreamBlocked === true);
    if (blocked.length > 0) {
      return `Exit blocked on event ${blocked[0].eventId}.`;
    }
    const named = matchingReasons(view.reasons, /emergency|ambulance/i);
    if (named.length > 0) {
      return `${named[0].reason} on event ${named[0].eventId}.`;
    }
    if (view.reasons.some((row) => row.downstreamBlocked === false)) {
      return "Recorded exits were open. No ambulance request is in this run.";
    }
    return "No exit check is in this run.";
  }
  if (id === "yuki") {
    return view.recovery || "No recovery transition is in this page.";
  }
  const stale = matchingReasons(view.reasons, /stale|insufficient/i);
  if (stale.length > 0) {
    return `${stale[0].reason}. The class does not name a cause.`;
  }
  const freshness = view.frames.map((frame) => frame.freshness).filter(Boolean);
  if (freshness.length === 0) {
    return "No sensor-freshness record is in this run.";
  }
  if (freshness.every((value) => value === "not recorded")) {
    return "Freshness was not recorded. That is not a statement that the road is healthy.";
  }
  return `Freshness: ${freshness[0]}. The class does not name a cause.`;
}
