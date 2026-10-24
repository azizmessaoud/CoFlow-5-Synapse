import { useEffect, useState } from "react";
import { api, useOnce } from "../api.js";
import { LANGS, useLang } from "../i18n.js";

export default function ScenarioBar({ live }) {
  const scenarios = useOnce("/scenarios") || [];
  const [choice, setChoice] = useState("morning_peak");
  const [speed, setSpeed] = useState(4);
  const [controller, setController] = useState("traffix");
  const [failed, setFailed] = useState("");
  const { lang, setLang } = useLang();
  useEffect(() => { if (live.scenario) setChoice(live.scenario); }, [live.scenario]);
  useEffect(() => { if (live.speed) setSpeed(live.speed); }, [live.speed]);
  useEffect(() => { if (live.controller) setController(live.controller); }, [live.controller]);
  const start = () => {
    setFailed("");
    api(`/start?scenario=${choice}&speed=${speed}&controller=${controller}`, { method: "POST" })
      .catch((e) => setFailed(`Start failed: ${e.message}`));
  };
  const stop = () => api("/stop", { method: "POST" }).catch((e) => setFailed(`Stop failed: ${e.message}`));
  const status = live.status;
  return (
    <div className="bar">
      <select value={choice} onChange={(e) => setChoice(e.target.value)} aria-label="Scenario">
        {scenarios.map((s) => <option key={s.id} value={s.id}>{s.id.replaceAll("_", " ")}</option>)}
      </select>
      <select value={speed} onChange={(e) => setSpeed(e.target.value)} aria-label="Speed">
        {[1, 2, 4, 8, 16].map((s) => <option key={s} value={s}>{s}× speed</option>)}
      </select>
      <select value={controller} onChange={(e) => setController(e.target.value)} aria-label="Traffic light agent">
        <option value="traffix">Max-pressure agent</option>
        <option value="traffix_predictive">Predictive agent (MPC)</option>
        <option value="traffix_rl">Reinforcement learning agent</option>
        <option value="traffix_rules">Rules only (no models)</option>
        <option value="junction_only">No supermaster</option>
      </select>
      <button className="primary" onClick={start}>Start</button>
      <button onClick={stop}>Stop</button>
      <span style={{ flex: 1 }} />
      {status === "running" && <>
        <span className="muted">{live.scenario?.replaceAll("_", " ")} · {
          { traffix: "max-pressure", traffix_predictive: "predictive", traffix_rl: "RL",
            traffix_rules: "rules only", junction_only: "no supermaster" }[live.controller] || live.controller}</span>
        <span className="clock">{live.clock}</span>
        <span className="pill ok">live</span>
      </>}
      {status === "starting" && <span className="pill info">starting SUMO…</span>}
      {status === "error" && <span className="pill bad">simulation stopped: {live.error}</span>}
      {failed && <span className="pill bad">{failed}</span>}
      {status === "finished" && <span className="pill info">finished</span>}
      {status === "idle" && <span className="muted">No simulation running</span>}
      <select value={lang} onChange={(e) => setLang(e.target.value)} aria-label="Language of alerts and answers">
        {LANGS.map((l) => <option key={l.id} value={l.id}>{l.label}</option>)}
      </select>
      {status === "offline" && <span className="pill bad">backend offline: run python scripts/run_live.py</span>}
    </div>
  );
}
