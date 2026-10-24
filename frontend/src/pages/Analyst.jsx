import { useEffect, useState } from "react";
import { api, useOnce } from "../api.js";
import { Waiting } from "../components/Feed.jsx";
import { dirOf, useLang } from "../i18n.js";

export default function Analyst({ live }) {
  const [q, setQ] = useState("");
  const [rows, setRows] = useState([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [error, setError] = useState("");
  const [checks, setChecks] = useState({});
  const metrics = useOnce("/models");
  const { lang } = useLang();
  const hasEmergency = ["emergency", "combined"].includes(live.scenario);
  const examples = hasEmergency
    ? ["Why did the ambulance get green?", "Was any emergency vehicle denied?",
       "How did traffic recover after the ambulance?"]
    : ["Why did the late buses get priority?", "What happened with the incident?", "Why was the walk signal delayed at J2?",
       "What did the rain change?"];
  useEffect(() => { setQuestion(examples[0]); setAnswer(null); }, [live.scenario]);
  useEffect(() => {
    if (live.status !== "running" && live.status !== "finished") return;
    const id = setTimeout(() => api(`/decisions?limit=150&q=${encodeURIComponent(q)}`).then(setRows).catch(() => {}), 300);
    return () => clearTimeout(id);
  }, [q, live.counts?.decisions]);
  const ask = async () => {
    if (!question.trim()) { setError("Type a question first"); return; }
    setError("");
    try { setAnswer(await api("/ask", { method: "POST", headers: { "Content-Type": "application/json" },
                                         body: JSON.stringify({ question, lang }) })); }
    catch (e) { setError(String(e)); }
  };
  // CoFlow Synapse: verified / template / abstain, with seven-field provenance.
  const verify = async (id) => {
    try {
      const r = await api("/synapse/explain", { method: "POST", headers: { "Content-Type": "application/json" },
                                                 body: JSON.stringify({ decision_id: id }) });
      setChecks((c) => ({ ...c, [id]: r }));
    } catch (e) { setChecks((c) => ({ ...c, [id]: { fallback: "abstain", answer: String(e), provenance: {} } })); }
  };
  return (
    <>
      <div><h1>Why did the system do that?</h1>
        <p className="muted">Tahani · every decision has a reason code. Synapse explains with citations or abstains.</p></div>
      <Waiting live={live} />
      <div className="card">
        <h2>Ask Synapse</h2>
        <div style={{ display: "flex", gap: 8 }}>
          <input style={{ flex: 1 }} value={question} onChange={(e) => { setQuestion(e.target.value); setError(""); }} />
          <button className="primary" onClick={ask}>Ask</button>
        </div>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          {examples.map((x) => (
            <button key={x} style={{ fontSize: 12, padding: "3px 10px" }} onClick={() => setQuestion(x)}>{x}</button>
          ))}
        </div>
        {error && <span style={{ color: "#f4a497", fontSize: 13 }}>{error}</span>}
        {answer && <div className="answer" dir={dirOf(lang)}>
          <span className={`pill ${answer.abstained ? "warn" : "ok"}`}>{answer.abstained ? "abstained" : `${answer.citations.length} citations`}</span>
          <span className="muted" style={{ fontSize: 12, marginInlineStart: 8 }}>{answer.engine === "llm-agent"
            ? `LLM agent · ${answer.tool_calls?.length || 0} tool calls` : "templates"}</span>{"\n"}{answer.answer}</div>}
      </div>
      <div className="split">
        <div className="card">
          <h2>Decision log</h2>
          <input placeholder="Filter: ambulance, J1, bus, crossing, rain..." value={q} onChange={(e) => setQ(e.target.value)} />
          <div className="feed">
            <table><tbody>
              {rows.map((e) => (
                <tr key={e.id}>
                  <td className="mono muted" style={{ whiteSpace: "nowrap" }}>{e.clock || `${Math.round(e.t)}s`}</td>
                  <td>
                    <div>{e.text || e.reason}</div>
                    <details style={{ marginTop: 3 }}>
                      <summary className="muted" style={{ fontSize: 12, cursor: "pointer" }}>#{e.id} · {e.agent} · {e.reason}</summary>
                      <span className="muted mono" style={{ fontSize: 12, wordBreak: "break-all" }}>{JSON.stringify(e.details)}</span>
                      <div style={{ marginTop: 4 }}>
                        <button style={{ fontSize: 12, padding: "2px 8px" }} onClick={() => verify(e.id)}>Verify with CoFlow Synapse</button>
                        {checks[e.id] && <div className="answer" style={{ marginTop: 4 }}>
                          <span className={`pill ${checks[e.id].fallback === "verified" ? "ok" : "warn"}`}>{checks[e.id].fallback}</span>
                          {" "}{checks[e.id].explanation || checks[e.id].answer}
                          <div className="muted mono" style={{ fontSize: 11, wordBreak: "break-all" }}>
                            {checks[e.id].citations?.length ? `cites ${checks[e.id].citations.join(", ")} · ` : ""}
                            run {checks[e.id].provenance.run_id} · bundle {checks[e.id].provenance.bundle_digest?.slice(7, 19)}
                            {" "}· corpus {checks[e.id].provenance.corpus_hash?.slice(7, 19)}</div>
                        </div>}
                      </div>
                    </details>
                  </td>
                </tr>
              ))}
            </tbody></table>
          </div>
        </div>
        <div className="card">
          <h2>Trained models</h2>
          {!metrics || !Object.keys(metrics).length ? <span className="muted">Run python scripts/train.py</span> :
            <table><tbody>
              {Object.entries(metrics).filter(([k]) => !k.startsWith("_")).map(([k, v]) => (
                <tr key={k}><td><b>{k.replaceAll("_", " ")}</b></td>
                  <td className="mono">{Object.entries(v).filter(([, x]) => typeof x !== "object").slice(0, 4)
                    .map(([a, b]) => `${a}: ${b}`).join(" · ")}</td></tr>
              ))}
            </tbody></table>}
        </div>
      </div>
    </>
  );
}
