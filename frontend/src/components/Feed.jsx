import { dirOf, noteText, useLang } from "../i18n.js";

// filter: optional (notification) => bool, to keep only alerts on the user's trip, stop or line
export function Notifications({ live, persona, filter, title = "Notifications", empty = "No notifications yet" }) {
  const { lang } = useLang();
  const items = (live.notifications || []).filter((n) => n.persona === persona && (!filter || filter(n)))
    .slice().reverse();
  return (
    <div className="card">
      <h2>{title}</h2>
      <div className="feed" dir={dirOf(lang)}>
        {items.length === 0 && <span className="muted">{empty}</span>}
        {items.map((n, i) => (
          <div key={i} className={`note ${n.severity}`}><time>{n.time}</time>{noteText(n, lang)}</div>
        ))}
      </div>
    </div>
  );
}

export function Stat({ label, value, tone }) {
  return (
    <div className="card stat">
      <b style={tone ? { color: tone } : undefined}>{value}</b>
      <span>{label}</span>
    </div>
  );
}

export function Waiting({ live }) {
  if (live.status === "running" || live.status === "finished") return null;
  if (live.status === "starting")
    return <div className="card empty">Starting SUMO and the agents… the map fills in within a few seconds.</div>;
  if (live.status === "error")
    return <div className="card empty">The simulation stopped: {live.error} Press Start to try again.</div>;
  return <div className="card empty">Start a scenario above to bring this page to life.</div>;
}
