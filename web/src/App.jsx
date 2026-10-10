import { useEffect, useState } from "react";

export default function App() {
  const [health, setHealth] = useState(null);
  const [runs, setRuns] = useState([]);
  const [selected, setSelected] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [eventId, setEventId] = useState("");
  const [question, setQuestion] = useState("");
  const [explanation, setExplanation] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      fetch("/api/health").then((r) => r.json()),
      fetch("/api/runs").then((r) => r.json()),
      fetch("/api/metrics").then((r) => r.json()),
    ])
      .then(([healthBody, runsBody, metricsBody]) => {
        setHealth(healthBody);
        setRuns(runsBody.runs || []);
        setMetrics(metricsBody);
      })
      .catch((err) => setError(String(err)));
  }, []);

  function openRun(runId) {
    fetch(`/api/runs/${runId}`)
      .then((r) => r.json())
      .then(setSelected)
      .catch((err) => setError(String(err)));
  }

  function requestExplanation(event) {
    event.preventDefault();
    setExplanation(null);
    fetch("/api/explanations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Idempotency-Key": `dashboard-${Date.now()}`,
      },
      body: JSON.stringify({ event_id: eventId, question }),
    })
      .then((response) => response.json().then((body) => ({ response, body })))
      .then(({ response, body }) => {
        if (!response.ok) throw new Error(body.detail || "Explanation request failed");
        setExplanation(body);
      })
      .catch((err) => setError(String(err)));
  }

  return (
    <main>
      <p className="flag">
        Simulation evidence only. Not a live-city deployment. No lives saved. No
        measured air quality. No best-episode headline.
      </p>
      <h1>CoFlow-5 Synapse</h1>
      <p>Read-only view of tagged evidence bundles. This UI cannot reach TraCI.</p>
      {error ? <p className="error">{error}</p> : null}
      {health ? (
        <p>
          API health: {health.status}. Actuates: {String(health.actuates)}. SUMO
          in process: {String(health.sumo)}.
        </p>
      ) : (
        <p>Loading API health…</p>
      )}
      <section className="metrics" aria-label="Synapse metrics">
        <h2>Explanation quality</h2>
        <div className="metric-grid">
          <div><strong>{metrics?.abstention_rate ?? "—"}</strong><span>abstention rate</span></div>
          <div><strong>{metrics?.fallback_rate ?? "—"}</strong><span>fallback rate</span></div>
          <div><strong>{metrics?.average_latency_ms ?? "—"}</strong><span>average latency ms</span></div>
          <div><strong>{metrics?.cost_units ?? "—"}</strong><span>cost units</span></div>
        </div>
      </section>
      <section className="explanation" aria-label="Evidence explanation">
        <h2>Explain a frozen decision</h2>
        <form onSubmit={requestExplanation}>
          <label>
            Event ID
            <input value={eventId} onChange={(event) => setEventId(event.target.value)} required />
          </label>
          <label>
            Question
            <input value={question} onChange={(event) => setQuestion(event.target.value)} required maxLength={2000} />
          </label>
          <button type="submit">Request explanation</button>
        </form>
        {explanation ? (
          <div className="result">
            <strong>{explanation.fallback}</strong>
            <p>{explanation.answer}</p>
            <p>Citations: {explanation.citations?.join(", ") || "none"}</p>
            <pre>{JSON.stringify(explanation.provenance, null, 2)}</pre>
          </div>
        ) : null}
      </section>
      <h2>Runs</h2>
      {runs.length === 0 ? (
        <p>No tagged bundles in the evidence root yet.</p>
      ) : (
        <ul>
          {runs.map((run) => (
            <li key={run.run_id}>
              <button type="button" onClick={() => openRun(run.run_id)}>
                {run.run_id}
              </button>
              <span>
                {" "}
                {run.status} · {run.scenario_hash}
              </span>
            </li>
          ))}
        </ul>
      )}
      {selected ? (
        <section>
          <h2>Manifest {selected.run_id}</h2>
          <p className="label">Measured J0 evidence: frozen simulation artifact; not deployment evidence.</p>
          <pre>{JSON.stringify(selected, null, 2)}</pre>
        </section>
      ) : null}
    </main>
  );
}
