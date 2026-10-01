import { useEffect, useState } from "react";
import {
  auditRows,
  comparisonRows,
  explanationRows,
  frameRows,
  limitationLines,
  personaCards,
  reasonRows,
  recoveryState,
} from "./evidence.js";

async function readApi(path) {
  const response = await fetch(path);
  const body = await response.json();
  if (!response.ok) {
    return { ok: false, error: body.error || "request-failed", detail: body.detail || "" };
  }
  return { ok: true, body };
}

export default function App() {
  const [health, setHealth] = useState(null);
  const [runs, setRuns] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [page, setPage] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([readApi("/api/health"), readApi("/api/runs")])
      .then(([healthResult, runsResult]) => {
        if (!healthResult.ok || !runsResult.ok) {
          setError(healthResult.detail || runsResult.detail || "The evidence API did not answer.");
          return;
        }
        setHealth(healthResult.body);
        setRuns(runsResult.body.runs || []);
      })
      .catch((err) => setError(String(err)));
  }, []);

  function openRun(runId) {
    setSelectedId(runId);
    setPage(null);
    setError("");
    const encoded = encodeURIComponent(runId);
    Promise.all([
      readApi(`/api/runs/${encoded}`),
      readApi(`/api/runs/${encoded}/kpis?limit=50`),
      readApi(`/api/runs/${encoded}/events?limit=20`),
      readApi(`/api/runs/${encoded}/graph-frames?limit=5`),
      readApi(`/api/runs/${encoded}/explanations?limit=20`),
      readApi(`/api/runs/${encoded}/audits?limit=20`),
      readApi(`/api/runs/${encoded}/citations?limit=20`),
      readApi(`/api/runs/${encoded}/limitations`),
    ])
      .then(([runResult, kpis, events, frames, explanations, audits, citations, limitations]) => {
        if (!runResult.ok) {
          setError(runResult.detail || "That run is not in a validated bundle.");
          return;
        }
        setPage({
          run: runResult.body,
          kpis,
          events,
          frames,
          explanations,
          audits,
          citations,
          limitations,
        });
      })
      .catch((err) => setError(String(err)));
  }

  const comparisons = page?.kpis.ok ? comparisonRows(page.kpis.body) : [];
  const reasons = page?.events.ok ? reasonRows(page.events.body) : [];
  const frames = page?.frames.ok ? frameRows(page.frames.body) : [];
  const explanations = page?.explanations.ok ? explanationRows(page.explanations.body) : [];
  const audits = page?.audits.ok ? auditRows(page.audits.body) : [];
  const limits = page?.limitations.ok ? limitationLines(page.limitations.body) : [];
  const people = personaCards({
    comparisons,
    reasons,
    frames,
    explanations,
    recovery: page?.events.ok ? recoveryState(page.events.body) : "",
    opened: Boolean(page),
  });

  return (
    <main>
      <p className="flag">
        Simulation evidence only. Not a live-city deployment. No lives saved. No measured air quality. No best-episode headline.
      </p>
      <h1>CoFlow-5 evidence</h1>
      <p>This page reads frozen API records. It cannot change a signal.</p>
      {health ? (
        <p>
          API {health.status}. Actuates: {String(health.actuates)}. SUMO in process: {String(health.sumo)}.
        </p>
      ) : (
        <p>Loading API health…</p>
      )}
      {error ? <p className="error">{error}</p> : null}

      <h2>People</h2>
      <p>Each card reads the open run. A name is not an interview.</p>
      <div className="people">
        {people.map((person) => (
          <article key={person.id}>
            <h3>{person.name}</h3>
            <p>{person.helps}</p>
            <p>{person.text}</p>
          </article>
        ))}
      </div>

      <h2>Runs</h2>
      {runs.length === 0 ? (
        <p>No validated runs are loaded.</p>
      ) : (
        <ul className="runs">
          {runs.map((run) => (
            <li key={run.run_id}>
              <button type="button" onClick={() => openRun(run.run_id)} aria-pressed={selectedId === run.run_id}>
                {run.run_id}
              </button>
              <span>
                {" "}
                {run.controller || "bundle"} · {run.scenario_hash || "no scenario hash"}
              </span>
            </li>
          ))}
        </ul>
      )}

      {page ? (
        <section>
          <h2>Run {page.run.run_id}</h2>
          <dl>
            <dt>Scenario</dt>
            <dd>{page.run.scenario_hash || "not in this record"}</dd>
            <dt>Graph</dt>
            <dd>{page.run.graph_hash || "not in this record"}</dd>
            <dt>Controller</dt>
            <dd>{page.run.controller || "matrix bundle"}</dd>
            <dt>Recovery</dt>
            <dd>{page.events.ok ? recoveryState(page.events.body) : page.events.detail}</dd>
          </dl>

          <h2>Controller comparison</h2>
          {page.kpis.ok ? (
            comparisons.length === 0 ? (
              <p>No KPI rows for this run.</p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Controller</th>
                    <th>Seed</th>
                    <th>Demand</th>
                    <th>Planned</th>
                    <th>Completed</th>
                    <th>Unfinished</th>
                  </tr>
                </thead>
                <tbody>
                  {comparisons.map((row) => (
                    <tr key={`${row.controller}-${row.seed}-${row.demandScale}`}>
                      <td>{row.controller}</td>
                      <td>{String(row.seed)}</td>
                      <td>{String(row.demandScale)}</td>
                      <td>{String(row.planned)}</td>
                      <td>{String(row.completed)}</td>
                      <td>{String(row.unfinished)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )
          ) : (
            <p>{page.kpis.detail || page.kpis.error}</p>
          )}

          <h2>Graph frames</h2>
          {page.frames.ok ? (
            frames.length === 0 ? (
              <p>No graph frames for this run.</p>
            ) : (
              frames.map((frame) => (
                <article key={`${frame.time}-${frame.mode}`}>
                  <p>
                    Time {String(frame.time)} s. Mode {frame.mode}. Freshness: {frame.freshness}.
                  </p>
                  <p>Graph {frame.graphHash}.</p>
                  <ul>
                    {(Array.isArray(frame.nodes) ? frame.nodes : []).map((node) => (
                      <li key={node.signal_id}>
                        {node.signal_id}: {node.phase_id}
                      </li>
                    ))}
                  </ul>
                  <ul>
                    {(Array.isArray(frame.edges) ? frame.edges : []).slice(0, 4).map((edge) => (
                      <li key={edge.edge_id}>
                        {edge.edge_id} occupancy {String(edge.occupancy_ratio)}
                      </li>
                    ))}
                  </ul>
                </article>
              ))
            )
          ) : (
            <p>{page.frames.detail || page.frames.error}</p>
          )}

          <h2>Messages and reasons</h2>
          {page.events.ok ? (
            reasons.length === 0 ? (
              <p>No decision events for this run.</p>
            ) : (
              <ul>
                {reasons.map((row) => (
                  <li key={row.eventId}>
                    {row.eventId}: {row.reason || "no reason code"} / {row.action || "no action"}. Message:{" "}
                    {row.messageId === null ? "none" : row.messageId}
                  </li>
                ))}
              </ul>
            )
          ) : (
            <p>{page.events.detail || page.events.error}</p>
          )}

          <h2>Explanations, citations, and abstentions</h2>
          {page.explanations.ok ? (
            explanations.length === 0 ? (
              <p>No explanations cite this run.</p>
            ) : (
              explanations.map((row) => (
                <article key={row.requestId}>
                  <p>
                    {row.requestId}: {row.status}
                    {row.abstentionReason ? ` — ${row.abstentionReason}` : ""}
                  </p>
                  <p>
                    Event {row.eventId}. Citations:{" "}
                    {row.citations.length === 0 ? "none" : row.citations.map((citation) => citation.chunkId).join(", ")}
                  </p>
                </article>
              ))
            )
          ) : (
            <p>{page.explanations.detail || page.explanations.error}</p>
          )}
          <h3>Audits</h3>
          {page.audits.ok ? (
            audits.length === 0 ? (
              <p>No audits for this run.</p>
            ) : (
              <ul>
                {audits.map((row) => (
                  <li key={row.requestId}>
                    {row.requestId}: {row.status}
                  </li>
                ))}
              </ul>
            )
          ) : (
            <p>{page.audits.detail || page.audits.error}</p>
          )}

          <h2>Limitations</h2>
          {page.limitations.ok ? (
            limits.length === 0 ? (
              <p>No limitation lines on this run.</p>
            ) : (
              <ul>
                {limits.map((line) => (
                  <li key={line}>{line}</li>
                ))}
              </ul>
            )
          ) : (
            <p>{page.limitations.detail || page.limitations.error}</p>
          )}
        </section>
      ) : null}
    </main>
  );
}
