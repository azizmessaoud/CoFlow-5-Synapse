import { useEffect, useState } from "react";

export default function App() {
  const [health, setHealth] = useState(null);
  const [runs, setRuns] = useState([]);
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      fetch("/api/health").then((r) => r.json()),
      fetch("/api/runs").then((r) => r.json()),
    ])
      .then(([healthBody, runsBody]) => {
        setHealth(healthBody);
        setRuns(runsBody.runs || []);
      })
      .catch((err) => setError(String(err)));
  }, []);

  function openRun(runId) {
    fetch(`/api/runs/${runId}`)
      .then((r) => r.json())
      .then(setSelected)
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
          <pre>{JSON.stringify(selected, null, 2)}</pre>
        </section>
      ) : null}
    </main>
  );
}
