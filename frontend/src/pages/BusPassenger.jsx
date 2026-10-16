import { useState } from "react";
import { Notifications, Waiting } from "../components/Feed.jsx";
import NetworkMap from "../components/NetworkMap.jsx";
import { useOnce } from "../api.js";

export default function BusPassenger({ live }) {
  const lines = live.lines || {};
  const lineIds = Object.keys(lines);
  const [chosen, setLine] = useState(null);
  const line = lineIds.includes(chosen) ? chosen : lineIds[0] || "";
  const [stop, setStop] = useState("");
  const geo = useOnce(live.scenario ? "/network" : null, [live.scenario]);
  const info = geo?.line_info?.[line];
  const lineLabel = (l) => {
    const i = geo?.line_info?.[l];
    return i ? `${i.name} ${i.direction === "retour" ? "←" : "→"} ${i.to}` : l.replace("_", " ");
  };
  const headway = geo?.transit?.headway_s, lateAfter = headway && geo.transit.late_factor * headway;
  // real TRANSTU stops of this line when the network has them, else the stop before each light
  const realStops = info?.stops || [];
  const stops = realStops.length ? realStops : lines[line] || [];
  const myStop = stops.includes(stop) ? stop : stops[0];
  const stopInfo = (geo?.bus_stops || []).find((b) => b.id === myStop);
  const stopName = (s) => {
    const st = (geo?.bus_stops || []).find((b) => b.id === s || (b.junction === s && b.lines.includes(line)));
    return realStops.length ? (st ? st.name : s) : st ? `Stop before ${s} · ${st.name}` : s;
  };
  // each bus of this line heading for my stop: [id, bus, [[stop, metres], ...]] -> arrival row
  const busOf = Object.fromEntries((live.vehicles || []).filter((v) => v.kind === "bus").map((v) => [v.id, v]));
  const ahead = realStops.length
    ? Object.entries(live.bus_next_stops || {}).filter(([id]) => busOf[id]?.line === line)
        .map(([id, rows]) => [id, { ...(live.buses || {})[id], speed: busOf[id].speed }, rows])
    : Object.entries(live.buses || {}).filter(([, b]) => b.line === line).map(([id, b]) => [id, b, b.upcoming || []]);
  const coming = ahead.map(([id, b, rows]) => {
    const hit = rows.find(([s]) => s === myStop);
    return hit && { id, ...b, dist: hit[1], eta: Math.round(hit[1] / Math.max(b.speed || 0, 6)) };
  }).filter(Boolean).sort((a, b) => a.eta - b.eta);
  const myJunction = realStops.length ? stopInfo?.junction : myStop;
  const mine = (n) => n.where?.line === line || (myJunction && (n.where?.junctions || []).includes(myJunction))
    || n.type === "RAIN" || n.type === "FLOOD";
  return (
    <>
      <div><h1>When is my bus coming?</h1>
        <p className="muted">Mamadou · choose your line and stop to see the next buses and alerts that concern you.</p></div>
      <Waiting live={live} />
      <div className="bar">
        <span className="muted">Line</span>
        <select value={line} onChange={(e) => setLine(e.target.value)} aria-label="Bus line">
          {lineIds.map((l) => <option key={l} value={l}>{lineLabel(l)}</option>)}
        </select>
        <span className="muted" style={{ marginLeft: 12 }}>My stop</span>
        <select value={myStop || ""} onChange={(e) => setStop(e.target.value)}>
          {stops.map((s) => <option key={s} value={s}>{stopName(s)}</option>)}
        </select>
      </div>
      <div className="split">
        <div className="card">
          <NetworkMap live={live} lines={[line]} focus={coming.map((b) => b.id)} height={300} />
          <h2>Next buses at {myStop ? stopName(myStop) : "your stop"}</h2>
          {coming.length === 0 && <span className="muted">No bus of this line is on its way to this stop yet.</span>}
          <table>
            {coming.length > 0 && <thead><tr><th>Bus</th><th>Arrives in</th><th>Distance</th><th>Gap to previous</th><th>Status</th></tr></thead>}
            <tbody>
              {coming.map((b) => (
                <tr key={b.id}>
                  <td className="mono">{b.id.replace("bus_", "")}</td>
                  <td><b>{b.eta < 60 ? `${b.eta} s` : `${Math.round(b.eta / 60)} min`}</b></td>
                  <td>{b.dist} m</td>
                  <td>{b.gap_s == null ? "—" : `${Math.round(b.gap_s / 60)} min`}</td>
                  <td>{b.late ? <span className="pill warn">late</span> : <span className="pill ok">regular</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <span className="muted">
            {info && <>TRANSTU {info.name}, {info.from} → {info.to}. </>}
            {headway ? <>Assumed one bus every {Math.round(headway / 60)} minutes; a gap above {Math.round(lateAfter / 60)} minutes
              counts as late. </> : null}Arrival times are estimates.
          </span>
        </div>
        <Notifications live={live} persona="bus_passenger" filter={mine} title={`Alerts for ${lineLabel(line)}`}
                       empty="Nothing affecting your line or stop" />
      </div>
    </>
  );
}
