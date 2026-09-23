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
