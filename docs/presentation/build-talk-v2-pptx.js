'use strict';

const path = require('path');
const pptxgen = require('pptxgenjs');

const pptx = new pptxgen();
pptx.defineLayout({ name: 'TALK', width: 13.333, height: 7.5 });
pptx.layout = 'TALK';
pptx.author = 'CoFlow-5 Synapse · ESPRIT 4DS';
pptx.title = 'CoFlow-5 Synapse — Short Professor Talk';
pptx.subject = 'Visual Design Thinking story and proposed solution';
pptx.lang = 'en-US';
pptx.theme = { headFontFace: 'Aptos Display', bodyFontFace: 'Aptos', lang: 'en-US' };

const C = {
  navy: '081B2B', navy2: '102C3E', card: '123246', white: 'FFFFFF', ink: 'F4F8FA',
  mute: '9CB3BF', teal: '35C8BC', cyan: '45B8D1', amber: 'F2A44C', red: 'E56E72',
  green: '54C38A', purple: 'A892E8', line: '285064', black: '000000',
};
const W = 13.333, H = 7.5;
const PHOTO = (file) => path.join(__dirname, 'personas', file);
const faces = [
  ['p1-amara.png', 'Amara', 'TIME'], ['p2-david.png', 'David', 'PREDICT'],
  ['p3-chidi.png', 'Chidi', 'REGULAR'], ['p4-rosa.png', 'Rosa', 'EXPLAIN'],
  ['p5-marcus.png', 'Marcus', 'PASS'], ['p6-yuki.png', 'Yuki', 'CONTROL'],
  ['p7-maria.png', 'Maria', 'HOME'], ['p8-omar.png', 'Omar', 'TRUST'],
];
let count = 0;

function slide(note) {
  const s = pptx.addSlide(); count += 1; s.background = { color: C.navy };
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 0.12, h: H, fill: { color: C.teal }, line: { color: C.teal } });
  s.addNotes(note); return s;
}
function text(s, value, x, y, w, h, size = 18, color = C.ink, extra = {}) {
  s.addText(value, { x, y, w, h, fontFace: 'Aptos', fontSize: size, color, margin: 0, fit: 'shrink', valign: 'mid', ...extra });
}
function label(s, value, x = 0.65, y = 0.45, w = 4) {
  text(s, value.toUpperCase(), x, y, w, 0.25, 10, C.teal, { bold: true, charSpacing: 2 });
}
function heading(s, value, y = 0.9, size = 35, w = 12) {
  text(s, value, 0.65, y, w, 0.8, size, C.white, { bold: true, fontFace: 'Aptos Display' });
}
function card(s, x, y, w, h, fill = C.card, line = C.line, radius = 0.1) {
  s.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius: radius, fill: { color: fill }, line: { color: line, width: 0.8 } });
}
function photo(s, file, x, y, w, h) {
  s.addImage({ path: PHOTO(file), x, y, w, h, sizing: { type: 'cover', w, h } });
}
function footer(s, value = 'CoFlow-5 · evidence before claims') {
  text(s, value, 0.65, 7.12, 12, 0.18, 8.5, C.mute, { align: 'right' });
}
function arrow(s, x, y, w = 0.55, color = C.teal) {
  s.addShape(pptx.ShapeType.chevron, { x, y, w, h: 0.42, fill: { color }, line: { color } });
}

// 1 — Cover
{
  const s = slide('Open on the faces. Say: traffic is not an average car. These are illustrations of research-informed personas, not stakeholder interviews.');
  faces.forEach((f, i) => photo(s, f[0], i * W / 8, 0, W / 8, H));
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: W, h: H, fill: { color: C.navy, transparency: 34 }, line: { color: C.navy } });
  label(s, 'ESPRIT · 4DS · DESIGN THINKING', 0.7, 1.45, 7);
  heading(s, 'The light should see a person.', 2.0, 42);
  text(s, 'CoFlow-5 Synapse', 0.7, 3.2, 6, 0.45, 23, C.teal, { bold: true });
  text(s, '8 personas  ·  5 agents  ·  1 signal writer', 0.7, 3.8, 9, 0.4, 19, C.white);
  text(s, 'Illustrations—not interviews. [C02]', 0.7, 6.75, 6, 0.3, 12, C.mute);
}

// 2 — Challenge
{
  const s = slide('Read the course question once. Then say the course expects a prototype, different conditions, a baseline comparison, and honest strengths and limitations. [C01]');
  label(s, 'Course challenge · [C01]');
  heading(s, 'Not “build AI.”  Prove a better decision.', 0.85, 35);
  card(s, 0.8, 1.95, 11.75, 1.25, C.navy2, C.teal);
  text(s, 'How might we use data and intelligent agents to make urban traffic more efficient, adaptive and sustainable?', 1.15, 2.18, 11.05, 0.78, 24, C.white, { bold: true, italic: true, align: 'center' });
  const outs = [['PROTOTYPE', 'works'], ['CONDITIONS', 'change'], ['BASELINE', 'compare'], ['LIMITS', 'stay visible']];
  outs.forEach((o, i) => {
    const x = 0.75 + i * 3.13;
    card(s, x, 4.0, 2.78, 1.55, C.card, i === 2 ? C.amber : C.line);
    text(s, o[0], x + 0.15, 4.28, 2.48, 0.3, 13, i === 2 ? C.amber : C.teal, { bold: true, align: 'center' });
    text(s, o[1], x + 0.15, 4.72, 2.48, 0.4, 22, C.white, { bold: true, align: 'center' });
  });
  text(s, 'Evidence matters more than technological complexity.', 0.8, 6.35, 11.7, 0.45, 18, C.mute, { italic: true, align: 'center' });
  footer(s);
}

// 3 — Design Thinking
{
  const s = slide('Walk left to right. Empathize, Define and Ideate explain why the solution exists. Prototype and Test create evidence. Old narrative status labels do not decide completion.');
  label(s, 'Design Thinking');
  heading(s, 'People → problem → options → evidence', 0.85, 35);
  const stages = [
    ['1', 'EMPATHIZE', '8 people', C.amber], ['2', 'DEFINE', 'one problem', C.cyan],
    ['3', 'IDEATE', 'many options', C.purple], ['4', 'PROTOTYPE', 'one system', C.green],
    ['5', 'TEST', 'honest proof', C.red],
  ];
  stages.forEach((st, i) => {
    const x = 0.55 + i * 2.55;
    s.addShape(pptx.ShapeType.ellipse, { x: x + 0.73, y: 2.05, w: 0.9, h: 0.9, fill: { color: st[3] }, line: { color: st[3] } });
    text(s, st[0], x + 0.73, 2.05, 0.9, 0.9, 22, C.white, { bold: true, align: 'center' });
    if (i < 4) arrow(s, x + 2.18, 2.3, 0.4, C.line);
    text(s, st[1], x, 3.2, 2.35, 0.32, 13, st[3], { bold: true, align: 'center' });
    text(s, st[2], x, 3.68, 2.35, 0.38, 18, C.white, { align: 'center' });
  });
  card(s, 1.0, 5.15, 11.3, 1.05, C.navy2, C.teal);
  text(s, 'We did not start with an LLM. We started with who could be helped—or harmed.', 1.35, 5.42, 10.6, 0.5, 21, C.white, { bold: true, align: 'center' });
  text(s, 'Research-informed personas · not interview-validated [C02]', 0.8, 6.55, 11.7, 0.3, 12, C.mute, { align: 'center' });
  footer(s);
}

// 4 — Eight personas
{
  const s = slide('Point at the one-word needs. Do not read biographies. Full evidence-backed cards are in the separate persona companion deck.');
  label(s, 'Empathize');
  heading(s, 'One street. Eight human needs.', 0.8, 34);
  faces.forEach((f, i) => {
    const x = 0.3 + i * 1.62;
    photo(s, f[0], x, 1.75, 1.48, 3.7);
    s.addShape(pptx.ShapeType.rect, { x, y: 4.75, w: 1.48, h: 1.05, fill: { color: C.card }, line: { color: C.card } });
    text(s, f[2], x, 4.9, 1.48, 0.3, 14, C.white, { bold: true, align: 'center' });
    text(s, f[1], x, 5.35, 1.48, 0.26, 11, C.mute, { align: 'center' });
  });
  text(s, 'Amara · David · Chidi · Rosa · Marcus · Yuki · Maria · Omar', 0.55, 6.28, 12.2, 0.35, 16, C.teal, { align: 'center' });
  text(s, 'Full persona cards: CoFlow-5-Persona-Cards.pptx', 0.55, 6.7, 12.2, 0.28, 11, C.mute, { align: 'center' });
  footer(s);
}

// 5 — Amara focus
{
  const s = slide('Amara is the example persona. Her statement is a design synthesis, not an interview quote. Literature motivates the need; it is not our result. [C03][C04]');
  photo(s, 'p1-amara.png', 0, 0, 6.15, H);
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 5.55, w: 6.15, h: 1.95, fill: { color: C.navy, transparency: 8 }, line: { color: C.navy } });
  text(s, 'P1 · AMARA · 74', 0.4, 5.72, 5.3, 0.3, 12, C.teal, { bold: true, charSpacing: 1.4 });
  text(s, 'Illustration · not a real stakeholder', 0.4, 6.75, 5.3, 0.25, 11, C.mute);
  label(s, 'One persona, one consequence', 6.65, 1.1, 6);
  heading(s, 'The light assumes someone faster.', 1.55, 33, 6.1);
  text(s, 'NEED', 6.65, 3.25, 1.2, 0.28, 11, C.teal, { bold: true });
  text(s, 'Finish the crossing.', 7.95, 3.15, 4.7, 0.45, 22, C.white, { bold: true });
  text(s, 'FEAR', 6.65, 4.05, 1.2, 0.28, 11, C.red, { bold: true });
  text(s, 'Cars get green while she is still on it.', 7.95, 3.92, 4.7, 0.65, 20, C.white);
  text(s, 'Evidence: perceived wait ≈2× in one study [C03] · clearance guidance ≈1.07 m/s [C04]', 6.65, 5.25, 6.0, 0.8, 14, C.mute);
  text(s, 'Measure: mean / P95 / max wait + zero clearance truncations', 6.65, 6.25, 6.0, 0.45, 15, C.amber, { bold: true });
}

// 6 — Conflict
{
  const s = slide('Tell this story in 20 seconds. A person already crossing finishes. Then emergency priority is considered only if downstream space exists. A late bus needs evidence. Every decision records who paid. [C16]');
  const trio = [
    ['p1-amara.png', 'AMARA', 'already crossing'],
    ['p5-marcus.png', 'MARCUS', 'ambulance coming'],
    ['p3-chidi.png', 'CHIDI', 'late bus waiting'],
  ];
  trio.forEach((t, i) => {
    const x = 0.3 + i * 4.3;
    photo(s, t[0], x, 0, 4.15, 5.35);
    s.addShape(pptx.ShapeType.rect, { x, y: 4.55, w: 4.15, h: 0.8, fill: { color: C.navy, transparency: 10 }, line: { color: C.navy } });
    text(s, t[1], x + 0.15, 4.66, 3.85, 0.26, 12, C.teal, { bold: true, align: 'center' });
    text(s, t[2], x + 0.15, 4.95, 3.85, 0.26, 17, C.white, { bold: true, align: 'center' });
  });
  heading(s, 'Who should the light serve first?', 5.62, 32);
  text(s, 'Safety → emergency → pedestrian deadline → late transit → flow → sustainability', 0.65, 6.48, 12, 0.36, 16, C.teal, { bold: true, align: 'center' });
  footer(s, 'One street · competing needs · visible trade-offs');
}

// 7 — Define
{
  const s = slide('Contrast the rejected technical framing with the human-centred problem. Then read the How-might-we question once.');
  label(s, 'Define');
  heading(s, 'The problem is not average delay.', 0.85, 35);
  card(s, 0.7, 1.85, 5.8, 2.15, '311F2A', C.red);
  text(s, 'WRONG', 1.0, 2.1, 1.3, 0.3, 12, C.red, { bold: true });
  text(s, '“Build five AI agents and reduce mean car delay.”', 1.0, 2.62, 5.2, 0.85, 23, C.white, { bold: true });
  card(s, 6.85, 1.85, 5.8, 2.15, '15382F', C.green);
  text(s, 'HUMAN-CENTRED', 7.15, 2.1, 2.2, 0.3, 12, C.green, { bold: true });
  text(s, 'Serve people—and show the trade-off when their needs conflict.', 7.15, 2.58, 5.2, 0.9, 23, C.white, { bold: true });
  label(s, 'Refined HMW', 0.9, 4.65, 3);
  text(s, 'How might we improve traffic for every person—not only the average car—while staying auditable and safe when things fail?', 0.9, 5.08, 11.55, 1.05, 25, C.white, { bold: true, align: 'center' });
  footer(s);
}

// 8 — Ideate
{
  const s = slide('Explain the ideation logic: diverge, challenge assumptions, then compare. Numerical matrix scores are team judgements, not evidence.');
  label(s, 'Ideate');
  heading(s, 'Generate widely. Cut ruthlessly.', 0.85, 35);
  const methods = [
    ['BRAINWRITE', 'central · local · rule-based · learned'],
    ['WORST IDEA', 'LLM drives · every agent writes · every bus wins'],
    ['SCAMPER', 'reverse authority: specialists ask, one acts'],
  ];
  methods.forEach((m, i) => {
    const x = 0.7 + i * 4.18;
    card(s, x, 2.0, 3.85, 2.15, C.card, i === 1 ? C.red : C.line);
    text(s, `0${i + 1}`, x + 0.25, 2.25, 0.65, 0.45, 17, i === 1 ? C.red : C.teal, { bold: true });
    text(s, m[0], x + 0.25, 2.85, 3.35, 0.35, 18, C.white, { bold: true });
    text(s, m[1], x + 0.25, 3.35, 3.35, 0.55, 14, C.mute);
  });
  card(s, 0.9, 4.75, 11.55, 1.25, '15382F', C.green);
  text(s, 'CHOSEN', 1.2, 4.98, 1.4, 0.28, 12, C.green, { bold: true });
  text(s, 'Cooperative Max-Pressure + one writer + typed advisers + deterministic safety', 2.55, 4.92, 9.5, 0.5, 22, C.white, { bold: true });
  text(s, 'Rejected: LLM control · five writers · mandatory RL · best-episode reporting  [C11][C16]', 1.2, 5.58, 10.85, 0.3, 13, C.mute, { align: 'center' });
  footer(s);
}

// 9 — Architecture
{
  const s = slide('Only A1 has a path to the safety mask and executor. A2 to A5 advise. Synapse reads immutable evidence and has no actuation path. [C16]');
  label(s, 'Proposed solution · [C16]');
  heading(s, 'Five agents. One pair of hands.', 0.85, 35);
  const agents = [
    ['A2', 'Emergency', 'ASKS'], ['A3', 'Walk / bus', 'ASKS'], ['A4', 'Situation', 'ADVISES'],
    ['A5', 'Sustainability', 'ADVISES'], ['A1', 'Flow', 'WRITES'],
  ];
  agents.forEach((a, i) => {
    const x = 0.48 + i * 2.55;
    card(s, x, 2.0, 2.35, 2.2, i === 4 ? '184B44' : C.card, i === 4 ? C.teal : C.line);
    text(s, a[0], x, 2.28, 2.35, 0.42, 24, i === 4 ? C.teal : C.white, { bold: true, align: 'center' });
    text(s, a[1], x + 0.15, 2.9, 2.05, 0.4, 17, C.white, { bold: true, align: 'center' });
    text(s, a[2], x + 0.15, 3.55, 2.05, 0.28, 12, i === 4 ? C.teal : C.mute, { bold: true, align: 'center' });
  });
  arrow(s, 5.8, 4.65, 0.6, C.teal);
  text(s, 'typed, expiring messages', 3.3, 4.62, 2.35, 0.32, 13, C.mute, { align: 'right' });
  card(s, 6.55, 4.4, 2.65, 0.95, C.card, C.amber);
  text(s, 'SAFETY MASK', 6.75, 4.65, 2.25, 0.3, 16, C.amber, { bold: true, align: 'center' });
  arrow(s, 9.42, 4.65, 0.55, C.amber);
  card(s, 10.12, 4.4, 2.55, 0.95, '15382F', C.green);
  text(s, 'EXECUTOR → SUMO', 10.25, 4.65, 2.28, 0.3, 15, C.green, { bold: true, align: 'center' });
  text(s, 'Only A1 writes signals.', 0.7, 5.75, 5.0, 0.45, 24, C.white, { bold: true });
  text(s, 'Synapse never actuates.', 7.0, 5.75, 5.0, 0.45, 24, C.purple, { bold: true, align: 'right' });
  text(s, 'Recovery: Max-Pressure → actuated → fixed-time', 0.7, 6.45, 12, 0.35, 16, C.teal, { bold: true, align: 'center' });
  footer(s);
}

// 10 — Communication
{
  const s = slide('Follow one request. The board validates identity and expiry. A1 safety-checks and ranks. One immutable reply and decision event close the round. If the board is empty, local Max-Pressure continues.');
  label(s, 'Communication');
  heading(s, 'Ask → check → decide → explain', 0.85, 35);
  const steps = [
    ['1', 'ASK', 'A2 / A3 request'], ['2', 'CHECK', 'TTL · identity · capacity'],
    ['3', 'DECIDE', 'A1 + safety mask'], ['4', 'REPLY', 'yes/no + reason'],
  ];
  steps.forEach((st, i) => {
    const x = 0.65 + i * 3.14;
    s.addShape(pptx.ShapeType.ellipse, { x: x + 1.0, y: 2.0, w: 0.72, h: 0.72, fill: { color: i === 2 ? C.amber : C.teal }, line: { color: C.white } });
    text(s, st[0], x + 1.0, 2.0, 0.72, 0.72, 20, C.white, { bold: true, align: 'center' });
    if (i < 3) arrow(s, x + 2.62, 2.17, 0.38, C.line);
    text(s, st[1], x, 3.05, 2.75, 0.35, 17, C.white, { bold: true, align: 'center' });
    text(s, st[2], x, 3.55, 2.75, 0.5, 14, C.mute, { align: 'center' });
  });
  card(s, 1.0, 4.65, 11.3, 0.9, C.navy2, C.teal);
  text(s, 'run_id  ·  scenario_hash  ·  event_id  ·  message_id', 1.3, 4.92, 10.7, 0.35, 19, C.white, { bold: true, align: 'center' });
  text(s, 'Empty board? A1 still runs.  Synapse failure? Light actions stay unchanged.', 0.8, 6.0, 11.7, 0.45, 18, C.teal, { bold: true, align: 'center' });
  footer(s);
}

// 11 — Scenarios and data
{
  const s = slide('These are three evidence layers: baseline traffic outcomes, cooperation decisions, and resilience under failure. Each produces joined records instead of a screenshot-only demo.');
  label(s, 'Scenarios + data');
  heading(s, 'Three questions. Three evidence packs.', 0.85, 34);
  const groups = [
    ['01', 'BASELINE', 'fixed-time · actuated · Max-Pressure', 'trips · waits · tails', C.cyan],
    ['02', 'COOPERATION', 'crossing · emergency · late bus', 'messages · decisions · KPIs', C.teal],
    ['03', 'FAILURE', 'loss · stale · controller · Synapse', 'faults · recovery · action hash', C.red],
  ];
  groups.forEach((g, i) => {
    const x = 0.65 + i * 4.15;
    card(s, x, 1.95, 3.85, 3.35, C.card, g[4]);
    text(s, g[0], x + 0.25, 2.2, 0.75, 0.35, 15, g[4], { bold: true });
    text(s, g[1], x + 0.25, 2.78, 3.35, 0.4, 20, C.white, { bold: true });
    text(s, g[2], x + 0.25, 3.5, 3.35, 0.65, 16, C.white);
    text(s, g[3], x + 0.25, 4.52, 3.35, 0.42, 13, C.mute);
  });
  text(s, 'No hidden exclusions: unfinished trips, faults, nulls and externalities stay visible.', 0.8, 5.9, 11.7, 0.45, 18, C.amber, { bold: true, align: 'center' });
  text(s, 'Data spine: manifest → state/messages → decisions/trips/faults → KPIs', 0.8, 6.4, 11.7, 0.32, 14, C.mute, { align: 'center' });
  footer(s);
}

// 12 — Evidence status
{
  const s = slide('Rows 07 through 10c are gated evidence slices. On matched seed 37, fixed-time completed 71/84 trips, actuated 84/84, and cooperative Max-Pressure 70/84. P95 wait was 33, 16, and 25 seconds. This mixed result establishes no winner or superiority. A4/A5 value remains unestablished. [C17]');
  label(s, 'Evidence now · [C17]');
  heading(s, 'Proven behavior ≠ proven performance.', 0.85, 35);
  const stats = [
    ['09', '0 orphans', '115 records joined'],
    ['10', '1 / 2', 'A5 accepted / rejected advice'],
    ['10B', '70 / 84', 'Max-Pressure trips completed'],
  ];
  stats.forEach((st, i) => {
    const x = 0.7 + i * 4.15;
    card(s, x, 1.9, 3.85, 2.25, C.card, i === 2 ? C.green : C.line);
    text(s, `ROW ${st[0]}`, x + 0.2, 2.18, 3.45, 0.25, 11, C.teal, { bold: true, align: 'center' });
    text(s, st[1], x + 0.2, 2.72, 3.45, 0.55, 29, C.white, { bold: true, align: 'center' });
    text(s, st[2], x + 0.2, 3.45, 3.45, 0.32, 13, C.mute, { align: 'center' });
  });
  card(s, 0.95, 4.65, 11.45, 1.35, '322A1F', C.amber);
  text(s, 'WHAT IS STILL MISSING', 1.25, 4.9, 2.75, 0.25, 11, C.amber, { bold: true });
  text(s, 'multi-seed inference  ·  A4/A5 value ablations  ·  stakeholder validation  ·  Tunis', 1.25, 5.32, 10.85, 0.4, 16, C.white, { align: 'center' });
  text(s, 'Rows 07, 08 and 09 plus 10, 10b and 10c are gated.', 0.8, 6.35, 11.7, 0.34, 14, C.green, { bold: true, align: 'center' });
  footer(s);
}

// 13 — Tunis, sources, boundaries
{
  const s = slide('Tunis is a future data showcase, not deployment evidence. OpenStreetMap geometry and official scheduled TRANSTU datasets may be used; dataset format must be checked and road demand remains synthetic or calibrated. [C15]');
  label(s, 'Tunis + resources');
  heading(s, 'Local story. Controlled claims.', 0.85, 35);
  card(s, 0.7, 1.9, 5.5, 3.85, C.card, C.teal);
  text(s, 'TUNIS SHOWCASE', 1.05, 2.25, 4.8, 0.32, 12, C.teal, { bold: true });
  text(s, 'OpenStreetMap', 1.05, 2.9, 4.8, 0.42, 24, C.white, { bold: true });
  text(s, '+ official scheduled TRANSTU data', 1.05, 3.45, 4.8, 0.42, 19, C.white);
  text(s, 'Road demand: synthetic or calibrated—not observed.', 1.05, 4.35, 4.8, 0.75, 16, C.amber, { bold: true });
  text(s, '[C15]', 1.05, 5.25, 1.0, 0.25, 11, C.mute);
  card(s, 6.55, 1.9, 6.05, 3.85, C.card, C.line);
  text(s, 'SOURCE SPINE', 6.9, 2.25, 5.35, 0.32, 12, C.teal, { bold: true });
  const sources = [
    'Course + method  [C01][C02]',
    'People + operations  [C03]–[C10]',
    'Traffic research  [C11]–[C14]',
    'Project authority + evidence  [C16][C17]',
  ];
  sources.forEach((v, i) => text(s, `•  ${v}`, 6.95, 2.9 + i * 0.62, 5.15, 0.4, 16, i === 3 ? C.green : C.white));
  text(s, '32-row mixed-source evidence register · full URLs in presentation-claim-ledger.json', 0.8, 6.12, 11.7, 0.35, 14, C.mute, { align: 'center' });
  text(s, 'No lives-saved claim · no ambient air claim · no best-episode headline', 0.8, 6.58, 11.7, 0.3, 13, C.red, { bold: true, align: 'center' });
  footer(s);
}

// 14 — Close
{
  const s = slide('Close in one sentence: CoFlow-5 is not an LLM traffic controller. It is a testable decision architecture where people define the requirements, A1 alone acts, and evidence decides what we may claim.');
  faces.forEach((f, i) => photo(s, f[0], i * W / 8, 0, W / 8, H));
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: W, h: H, fill: { color: C.navy, transparency: 30 }, line: { color: C.navy } });
  heading(s, 'People. Evidence. One writer.', 2.25, 42);
  text(s, 'Not an LLM traffic controller.', 0.7, 3.55, 12, 0.48, 24, C.teal, { bold: true, align: 'center' });
  text(s, 'A testable decision architecture for urban traffic simulation.', 0.7, 4.25, 12, 0.45, 20, C.white, { align: 'center' });
  text(s, 'Questions?', 0.7, 6.15, 12, 0.55, 30, C.white, { bold: true, align: 'center' });
}

if (count !== 14) throw new Error(`Expected 14 slides, built ${count}`);
const output = path.join(__dirname, 'CoFlow-5-Synapse-TALK.pptx');
pptx.writeFile({ fileName: output })
  .then(() => console.log(`SUCCESS ${output} slides=${count}`))
  .catch((error) => { console.error(error); process.exit(1); });
