'use strict';

const path = require('path');
const pptxgen = require('pptxgenjs');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'CoFlow-5 Synapse · ESPRIT 4DS';
pptx.company = 'ESPRIT';
pptx.subject = 'Design Thinking and proposed reliable multi-agent traffic solution';
pptx.title = 'CoFlow-5 Synapse — Professor Presentation';
pptx.lang = 'en-US';
pptx.theme = {
  headFontFace: 'Aptos Display',
  bodyFontFace: 'Aptos',
  lang: 'en-US',
};
pptx.defineSlideMaster({
  title: 'CONTENT',
  background: { color: 'F4F8FB' },
  objects: [
    { rect: { x: 0, y: 0, w: 13.333, h: 0.12, fill: { color: '16A3A5' }, line: { color: '16A3A5' } } },
    { line: { x: 0.45, y: 7.08, w: 12.43, h: 0, line: { color: 'C8D7E3', width: 0.6 } } },
  ],
  slideNumber: { x: 12.42, y: 7.12, w: 0.42, h: 0.18, color: '587286', fontFace: 'Aptos', fontSize: 8, align: 'right', margin: 0 },
});

const C = {
  navy: '0B2239', navy2: '123552', blue: '176B87', cyan: '2E9BB5', teal: '168F8B',
  green: '2D936C', mint: 'DDF3EC', sky: 'DDEFF5', pale: 'EEF5F8', white: 'FFFFFF',
  ink: '162B3A', slate: '4E6878', muted: '708896', line: 'C8D7E3', amber: 'CF7B1B',
  amberLt: 'FFF0D8', red: 'B74444', redLt: 'FBE4E4', purple: '6C5AA7', purpleLt: 'ECE8F8',
};
const W = 13.333;
const H = 7.5;
let slideCount = 0;

function tx(slide, text, x, y, w, h, options = {}) {
  slide.addText(text, {
    x, y, w, h, fontFace: 'Aptos', fontSize: 14, color: C.ink, margin: 0.06,
    breakLine: false, valign: 'mid', fit: 'shrink', ...options,
  });
}

function rect(slide, x, y, w, h, fill = C.white, line = C.line, radius = 0.08) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h, rectRadius: radius,
    fill: { color: fill }, line: { color: line, width: 0.8 },
  });
}

function pill(slide, text, x, y, w, fill, color = C.white) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h: 0.3, rectRadius: 0.08, fill: { color: fill }, line: { color: fill },
  });
  tx(slide, text, x + 0.04, y + 0.015, w - 0.08, 0.27, {
    fontSize: 9, bold: true, color, align: 'center', charSpacing: 0.7,
  });
}

function titleSlide(title, subtitle, section, note) {
  const slide = pptx.addSlide('CONTENT');
  slideCount += 1;
  pill(slide, section.toUpperCase(), 0.48, 0.28, Math.max(1.45, section.length * 0.09), C.teal);
  tx(slide, title, 0.48, 0.72, 12.15, 0.45, { fontFace: 'Aptos Display', fontSize: 27, bold: true, color: C.navy });
  if (subtitle) tx(slide, subtitle, 0.5, 1.19, 12.1, 0.26, { fontSize: 11.5, color: C.slate });
  tx(slide, 'CoFlow-5 Synapse · Design Thinking + proposed solution', 0.5, 7.12, 6.3, 0.18, { fontSize: 8, color: C.muted });
  slide.addNotes(note);
  return slide;
}

function sectionBox(slide, title, body, x, y, w, h, fill = C.white, accent = C.teal, bodySize = 13) {
  rect(slide, x, y, w, h, fill, accent);
  slide.addShape(pptx.ShapeType.rect, { x, y, w: 0.08, h, fill: { color: accent }, line: { color: accent } });
  tx(slide, title, x + 0.18, y + 0.08, w - 0.32, 0.28, { fontSize: 13, bold: true, color: accent });
  tx(slide, body, x + 0.18, y + 0.4, w - 0.32, h - 0.48, { fontSize: bodySize, color: [C.navy, C.navy2].includes(fill) ? C.white : C.ink, valign: 'top', breakLine: true });
}

function bulletList(slide, items, x, y, w, h, options = {}) {
  const fontSize = options.fontSize || 14;
  const lineH = h / items.length;
  items.forEach((item, i) => {
    const text = typeof item === 'string' ? item : item.text;
    const color = typeof item === 'string' ? (options.color || C.ink) : (item.color || options.color || C.ink);
    tx(slide, `•  ${text}`, x, y + i * lineH, w, lineH - 0.02, { fontSize, color, bold: Boolean(item.bold), valign: 'top' });
  });
}

function arrow(slide, x, y, w, color = C.blue) {
  slide.addShape(pptx.ShapeType.chevron, { x, y, w, h: 0.34, fill: { color }, line: { color } });
}

function evidenceTag(ids) {
  return ids.map(id => `[${id}]`).join('');
}

const personas = [
  {
    id: 'P1', name: 'Amara', initials: 'AM', photo: 'p1-amara.png', age: '74', role: 'Retired pedestrian; uses a cane',
    situation: 'Crosses a busy central street for shops and transit', context: 'Tunis design context (assumption)',
    statement: 'I need enough time to finish crossing, even when traffic is busy.',
    frustrations: 'Long waits cause fatigue. A short clearance can leave her exposed when conflicting traffic is released.',
    personality: 'Careful, independent, neighbourhood-aware. These traits are design assumptions, not interview findings.',
    needs: 'Clear acknowledgement; wait-aware service; conservative clearance; no repeated deferral; no app requirement.',
    technology: 'Pedestrian push-button, audible/visual feedback and reliable presence detection. A smartphone is not required.',
    bio: 'Amara represents slower walkers who can be excluded when signal timing assumes an average walking speed.',
    rejects: 'A shortened crossing for an ambulance already in conflict; inaccessible apps; targets presented as achieved results.',
    evidence: `One NZ study found perceived mean wait about 2x observed mean wait. MUTCD uses about 1.07 m/s and asks for slower values where needed. ${evidenceTag(['C03','C04'])}`,
    evaluation: 'Mean, P95 and maximum pedestrian wait; waits above the declared threshold; zero clearance truncations.',
    color: C.purple,
  },
  {
    id: 'P2', name: 'David', initials: 'DV', photo: 'p2-david.png', age: '41', role: 'Delivery-van driver',
    situation: 'More than 60 time-sensitive stops in a workday', context: 'Tunis design context (assumption)',
    statement: 'I can plan around a longer trip if I know how long it will actually take.',
    frustrations: 'Unpredictable surges break delivery windows. A good average can hide severe late trips and unfinished routes.',
    personality: 'Organised, practical and schedule-focused. These traits are a design synthesis.',
    needs: 'Reliable journey tails, fewer unnecessary stops, visible incidents and network coordination beyond one junction.',
    technology: 'Work phone, GPS/navigation and delivery-round tools; no special traffic-control interface.',
    bio: 'David makes journey reliability visible: the system must report the bad tail, not only mean travel time.',
    rejects: 'A faster average with worse P95 trips; deleting unfinished or teleported trips from evaluation.',
    evidence: `DfT TAG uses 0.4 as an appraisal reliability ratio for car/non-freight LGV journey-time variability. ${evidenceTag(['C05'])}`,
    evaluation: 'Completed and unfinished trips, P95/max duration, stops per vehicle, standstill time and teleports.',
    color: C.blue,
  },
  {
    id: 'P3', name: 'Chidi', initials: 'CH', photo: 'p3-chidi.png', age: '27', role: 'Frequent bus passenger',
    situation: 'Uses a high-frequency corridor where regularity is the service', context: 'Tunis design context (assumption)',
    statement: 'Buses should arrive regularly—not three at once after a long wait.',
    frustrations: 'A long gap is followed by bunched buses. Signal delay compounds lateness and breaks connections.',
    personality: 'Routine-oriented and sensitive to uncertainty. This is a research-informed design assumption.',
    needs: 'Conditional priority for a late bus or large headway gap—not automatic priority for every bus.',
    technology: 'Passenger information or timetable application when available; otherwise direct observation at the stop.',
    bio: 'Chidi represents passengers for whom headway regularity and waiting matter more than one bus moving slightly faster.',
    rejects: 'Unconditional bus priority; cutting pedestrian clearance; measuring only bus travel time.',
    evidence: `DfT TAG applies a 2x value-of-time multiplier to public-transport waiting. Bunching evidence motivates headway measures. ${evidenceTag(['C05'])}`,
    evaluation: 'Lateness, headway variation, passenger waiting proxy and externality to other traffic.',
    color: C.cyan,
  },
  {
    id: 'P4', name: 'Rosa', initials: 'RO', photo: 'p4-rosa.png', age: '52', role: 'Bus depot controller',
    situation: 'Supervises bus operations and disruption', context: 'Tunis design context (assumption)',
    statement: 'Show me why priority was granted or denied, and let me respond safely.',
    frustrations: 'Scattered information and unexplained refusals make incidents difficult to manage and defend later.',
    personality: 'Responsible, calm under pressure and evidence-seeking. These are design assumptions.',
    needs: 'Positions, headways, priority status, confidence, reason codes, safe intervention and a time-stamped audit trail.',
    technology: 'Depot tools, vehicle-location screen, radio, spreadsheet and an operations dashboard.',
    bio: 'Rosa represents the operator who must understand why a bus request lost to safety, emergency or capacity constraints.',
    rejects: 'A black box, unsupported prediction promises and any override that bypasses the safety mask.',
    evidence: `SCATS documentation includes monitoring, manual intervention and audit trails, motivating explainable operations. ${evidenceTag(['C08'])}`,
    evaluation: 'Reason-code coverage, joined decision history and a simple operator task: explain one accepted and one rejected request.',
    color: C.amber,
  },
  {
    id: 'P5', name: 'Marcus', initials: 'MA', photo: 'p5-marcus.png', age: '34', role: 'Urban ambulance crew',
    situation: 'Responds through congested streets during peak periods', context: 'Tunis design context (assumption)',
    statement: 'Get us through safely, and make sure traffic recovers after we pass.',
    frustrations: 'A green is useless when the downstream link is full. Isolated priority can leave queues and disrupted buses behind.',
    personality: 'Urgent, precise and aware of other road users. This is a design synthesis.',
    needs: 'Authenticated route/ETA request, downstream-capacity check, safe pre-clearance and controlled post-passage recovery.',
    technology: 'Dispatch tablet, GPS, radio, lights and siren; no public consumer application.',
    bio: 'Marcus makes both benefit and civilian externality visible. Passage and recovery form one journey.',
    rejects: 'Truncating an occupied crossing, moving a queue one junction ahead or translating simulation seconds into casualties.',
    evidence: `One Taipei cohort associated each additional ALS-response minute with 7% lower adjusted odds of survival to discharge. Closely spaced preemptions can impose delay in a studied network. ${evidenceTag(['C06','C07'])}`,
    evaluation: 'Emergency travel effect, civilian delay externality, blocked-downstream rejection, safety violations and recovery completion.',
    color: C.red,
  },
  {
    id: 'P6', name: 'Yuki', initials: 'YU', photo: 'p6-yuki.png', age: '47', role: 'Traffic engineer / network operations',
    situation: 'Accountable for safe automated network performance', context: 'Tunis design context (assumption)',
    statement: 'Automation should support my decisions—not leave me responsible for a system I cannot control.',
    frustrations: 'Stale data can look normal. Unexpected decisions are hard to diagnose, and unsafe manual takeover is not acceptable.',
    personality: 'Careful, process-driven and accountable. These are design assumptions.',
    needs: 'Current mode, health, freshness, decisions, constraints, safe override and predictable recovery.',
    technology: 'Signal supervisor, logs, sensor-health tools and GIS/analysis software.',
    bio: 'Yuki represents the engineer who must diagnose failure and regain control without bypassing legal signal transitions.',
    rejects: 'Silent degradation, an LLM in the control loop and a manual command that can create conflicting greens.',
    evidence: `Operational systems document intervention and fallback concepts; they motivate—not validate—CoFlow-5's exact ladder. ${evidenceTag(['C08'])}`,
    evaluation: 'Legal actions, transition reasons, health evidence, fallback order, log completeness and recovery time.',
    color: C.teal,
  },
  {
    id: 'P7', name: 'Maria', initials: 'MI', photo: 'p7-maria.png', age: '38', role: 'Parent living near an arterial',
    situation: 'Walks her child along a school-adjacent street', context: 'Tunis design context (assumption)',
    statement: 'Cleaner traffic on the main road must not mean more exhaust outside our homes.',
    frustrations: 'A network average can hide queues moved to her street. Modelled emissions are not the air her family breathes.',
    personality: 'Protective, local and sceptical of averages. These traits are design assumptions.',
    needs: 'Link-level maps, school-sensitive checks, before/after comparison and explicit displacement limits.',
    technology: 'No specialist technology is assumed; she sees understandable maps and labels, not TraCI.',
    bio: 'Maria represents residents who bear local burdens even when a city-wide metric improves.',
    rejects: 'Calling HBEFA air quality, hiding a worse side street, or claiming a Tunis deployment from simulation.',
    evidence: `For 2005–2006, 6.4 million students (12.5% of the studied US population) attended schools within 250 m of a major road. ${evidenceTag(['C09'])}`,
    evaluation: 'Per-link stops and emission proxies near selected receptors; displacement map; no ambient-exposure claim.',
    color: C.green,
  },
  {
    id: 'P8', name: 'Omar', initials: 'OM', photo: 'p8-omar.png', age: '55', role: 'Network duty officer',
    situation: 'Monitors incidents and coordinates operational response', context: 'Tunis design context (assumption)',
    statement: 'Tell me what is wrong, why you think so, and whether I can still trust the data.',
    frustrations: 'False alarms destroy trust. A queue may mean an incident, demand or a dead sensor; a frozen screen can look healthy.',
    personality: 'Sceptical, methodical and operational. These are design assumptions.',
    needs: 'Severity, observations, uncertainty, freshness, data-health warnings and recovery tracked after clearance.',
    technology: 'Radio, camera/video wall, incident tools and an operator dashboard.',
    bio: 'Omar represents the person who must separate “nothing detected” from “insufficient reliable data.”',
    rejects: 'Alerts without evidence, a universal detection-delay number or an anomaly presented as a proven cause.',
    evidence: `FHWA estimates incidents account for about 25–30% of congestion in many US metropolitan contexts; this is not a Tunis measurement. ${evidenceTag(['C10'])}`,
    evaluation: 'Detection delay, false-alarm rate, missed incidents, stale-data handling and recovery by severity.',
    color: C.navy2,
  },
];

function personaPhoto(filename) {
  return path.join(__dirname, 'personas', filename);
}

function personaSlide(persona, index) {
  const s = pptx.addSlide();
  slideCount += 1;
  s.background = { color: 'F4F8FB' };
  const photoW = 4.85;
  s.addImage({
    path: personaPhoto(persona.photo),
    x: 0, y: 0, w: photoW, h: H,
    sizing: { type: 'cover', w: photoW, h: H },
  });
  s.addShape(pptx.ShapeType.rect, {
    x: 0, y: 5.55, w: photoW, h: 1.95,
    fill: { color: C.navy }, line: { color: C.navy },
  });
  tx(s, `${persona.id}  ·  ${persona.age}`, 0.28, 5.68, 4.3, 0.28, {
    fontSize: 13, bold: true, color: '7FE0D7', charSpacing: 0.8,
  });
  tx(s, persona.name, 0.28, 5.96, 4.3, 0.48, {
    fontFace: 'Aptos Display', fontSize: 32, bold: true, color: C.white,
  });
  tx(s, persona.role, 0.28, 6.46, 4.3, 0.32, { fontSize: 14, color: 'B9DCE7' });
  tx(s, 'Illustration · not a real stakeholder', 0.28, 6.88, 4.3, 0.28, {
    fontSize: 11, italic: true, color: '7896A8',
  });

  const x = 5.15;
  pill(s, 'EMPATHIZE', x, 0.28, 1.55, C.teal);
  tx(s, `Persona ${index} — ${persona.name}`, x, 0.68, 7.8, 0.42, {
    fontFace: 'Aptos Display', fontSize: 24, bold: true, color: C.navy,
  });
  tx(s, `${persona.situation}. ${persona.context}.`, x, 1.12, 7.8, 0.36, {
    fontSize: 13, color: C.slate,
  });
  rect(s, x, 1.58, 7.8, 1.18, C.sky, persona.color);
  tx(s, 'DESIGN STATEMENT · NOT AN INTERVIEW QUOTE', x + 0.22, 1.68, 7.36, 0.22, {
    fontSize: 10, bold: true, color: persona.color, charSpacing: 0.6,
  });
  tx(s, `“${persona.statement}”`, x + 0.22, 1.92, 7.36, 0.68, {
    fontSize: 18, bold: true, italic: true, color: C.navy, valign: 'top',
  });
  sectionBox(s, 'Need', persona.needs, x, 2.92, 7.8, 1.02, C.mint, C.green, 14);
  sectionBox(s, 'Fear', persona.frustrations, x, 4.04, 3.78, 1.08, C.white, C.red, 13);
  sectionBox(s, 'Rejects', persona.rejects, x + 4.02, 4.04, 3.78, 1.08, C.redLt, C.red, 12.5);
  rect(s, x, 5.22, 7.8, 1.82, C.white, C.blue);
  tx(s, 'WHY · EVIDENCE · PROPOSED MEASURE', x + 0.22, 5.3, 7.36, 0.2, {
    fontSize: 10, bold: true, color: C.blue, charSpacing: 0.6,
  });
  tx(s, persona.bio, x + 0.22, 5.52, 7.36, 0.42, {
    fontSize: 13, color: C.ink, valign: 'top',
  });
  tx(s, persona.evidence, x + 0.22, 5.96, 7.36, 0.52, {
    fontSize: 12, color: C.slate, valign: 'top',
  });
  tx(s, `Target, not a result: ${persona.evaluation}`, x + 0.22, 6.5, 7.36, 0.42, {
    fontSize: 12, italic: true, color: C.amber, valign: 'top',
  });
  s.addNotes(
    `Introduce ${persona.name} as a research-informed design persona, not an interviewed person. ` +
    `Read the design statement, then one need, one fear, and one reject. ` +
    `Evidence: ${persona.evidence} Evaluation target, not a result: ${persona.evaluation} ` +
    `Personality (assumption): ${persona.personality} Technology: ${persona.technology}`,
  );
}

// 1 — Cover
{
  const s = pptx.addSlide(); slideCount += 1; s.background = { color: C.navy };
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: W, h: H, fill: { color: C.navy }, line: { color: C.navy } });
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 0.16, h: H, fill: { color: C.teal }, line: { color: C.teal } });
  pill(s, 'ESPRIT · 4DS · DATA SCIENCE', 0.7, 0.55, 2.75, C.teal);
  tx(s, 'CoFlow-5 Synapse', 0.7, 1.35, 11.8, 0.8, { fontFace: 'Aptos Display', fontSize: 42, bold: true, color: C.white });
  tx(s, 'Design Thinking → a reliable five-agent traffic solution', 0.72, 2.18, 11.3, 0.55, { fontSize: 24, color: 'B9DCE7' });
  tx(s, 'Eight research-informed personas · controlled SUMO scenarios · one signal writer · evidence before claims', 0.72, 2.85, 11.2, 0.55, { fontSize: 16, color: 'D8E8EF' });
  const labels = [['EMPATHIZE', 'people and journeys'], ['DEFINE', 'human-centred problem'], ['IDEATE', 'compare and cut ideas'], ['PROPOSE', 'five agents, one writer']];
  labels.forEach((item, i) => {
    rect(s, 0.72 + i * 3.02, 4.1, 2.75, 1.2, i === 3 ? '184D59' : C.navy2, i === 3 ? C.teal : '335D76');
    tx(s, item[0], 0.86 + i * 3.02, 4.3, 2.47, 0.26, { fontSize: 12, bold: true, color: i === 3 ? '7FE0D7' : '79C2D4' });
    tx(s, item[1], 0.86 + i * 3.02, 4.62, 2.47, 0.36, { fontSize: 13, color: C.white });
  });
  tx(s, 'Course HMW: How might we use data and intelligent agents to make urban traffic more efficient, adaptive and sustainable?', 0.72, 5.75, 11.85, 0.85, { fontSize: 17, italic: true, color: '9ADCE2', align: 'center' });
  tx(s, 'Professor presentation · 22 September 2026', 0.72, 6.92, 11.85, 0.22, { fontSize: 10, color: '7896A8', align: 'center' });
  s.addNotes('Open with the course question. Say that we began with people and evidence before choosing an algorithm. The presentation covers Design Thinking and the proposed solution, with current project status shown honestly.');
}

// 2 — Course challenge
{
  const s = titleSlide('The course challenge', 'The brief gives the problem and outcomes—not a predefined technical answer.', 'Course brief',
    'Read the challenge once. Explain that the course allows us to choose the data, agents, cooperation and evaluation method, but requires a prototype, scenarios, baseline comparison and evidence.');
  rect(s, 0.6, 1.75, 12.1, 1.35, C.navy, C.navy);
  tx(s, '“How might we use data and intelligent agents to make urban traffic more efficient, adaptive, and sustainable?”', 0.95, 1.98, 11.4, 0.85, { fontSize: 24, bold: true, italic: true, color: C.white, align: 'center' });
  const questions = [
    ['INFORMATION', 'What should an agent observe?'], ['DECISIONS', 'What may it decide?'],
    ['COOPERATION', 'Independent or cooperative?'], ['EVALUATION', 'How do we know it helps?'],
  ];
  questions.forEach((q, i) => sectionBox(s, q[0], q[1], 0.6 + i * 3.07, 3.45, 2.85, 1.18, i % 2 ? C.mint : C.sky, i % 2 ? C.green : C.blue, 14));
  sectionBox(s, 'Our answer', 'Cooperate through typed evidence. Only A1 acts. Compare against fixed-time and actuated control. Keep failures and limitations visible. [C01]', 0.6, 4.95, 12.1, 1.12, C.white, C.teal, 16);
}

// 3 — Expected outcomes
{
  const s = titleSlide('What the professor should be able to verify', 'Innovation matters, but evidence matters more than technological complexity.', 'Course outcomes',
    'Explain the four required outcomes. Stress that a smaller reproducible prototype is stronger than a complex demo with no baseline or evidence.');
  const outcomes = [
    ['1', 'Working prototype', 'A reproducible SUMO run with one legal signal writer.'],
    ['2', 'Different conditions', 'Demand, emergency, pedestrian, transit and failure scenarios.'],
    ['3', 'Baseline comparison', 'Fixed-time and actuated on matched scenario seeds.'],
    ['4', 'Strengths + limitations', 'Data, null results, externalities and missing evidence.'],
  ];
  outcomes.forEach((o, i) => {
    const x = 0.65 + i * 3.13;
    rect(s, x, 1.75, 2.88, 3.85, C.white, i % 2 ? C.green : C.blue);
    s.addShape(pptx.ShapeType.ellipse, { x: x + 0.93, y: 2.0, w: 1.0, h: 1.0, fill: { color: i % 2 ? C.green : C.blue }, line: { color: i % 2 ? C.green : C.blue } });
    tx(s, o[0], x + 0.93, 2.0, 1.0, 1.0, { fontSize: 26, bold: true, color: C.white, align: 'center' });
    tx(s, o[1], x + 0.2, 3.2, 2.48, 0.46, { fontSize: 18, bold: true, color: C.navy, align: 'center' });
    tx(s, o[2], x + 0.22, 3.78, 2.44, 1.05, { fontSize: 14, color: C.slate, align: 'center', valign: 'top' });
  });
  rect(s, 1.2, 5.95, 10.93, 0.64, C.amberLt, C.amber);
  tx(s, 'Evidence discipline: measured result ≠ proposed target ≠ literature finding ≠ design assumption.', 1.4, 6.08, 10.53, 0.34, { fontSize: 16, bold: true, color: C.amber, align: 'center' });
}

// 4 — Design Thinking
{
  const s = titleSlide('Design Thinking: the path from people to prototype', 'Stages 1–3 are complete as research-informed design work; current prototype evidence is tracked separately.', 'Method',
    'Walk left to right. Empathize, Define and Ideate explain why the architecture exists. Prototype and Test are governed by the harness and current evidence status, not by old slide labels.');
  const phases = [
    ['1', 'EMPATHIZE', 'Personas\nJourneys\nEvidence', C.amber],
    ['2', 'DEFINE', 'POV\nProblem\nHMW', C.blue],
    ['3', 'IDEATE', 'Diverge\nCompare\nChoose', C.purple],
    ['4', 'PROTOTYPE', 'SUMO\nAgents\nArtifacts', C.green],
    ['5', 'TEST', 'Baselines\nFaults\nLimits', C.red],
  ];
  phases.forEach((p, i) => {
    const x = 0.55 + i * 2.55;
    s.addShape(pptx.ShapeType.ellipse, { x: x + 0.72, y: 1.75, w: 0.9, h: 0.9, fill: { color: p[3] }, line: { color: p[3] } });
    tx(s, p[0], x + 0.72, 1.75, 0.9, 0.9, { fontSize: 23, bold: true, color: C.white, align: 'center' });
    tx(s, p[1], x, 2.85, 2.34, 0.34, { fontSize: 13, bold: true, color: p[3], align: 'center' });
    tx(s, p[2], x, 3.28, 2.34, 1.05, { fontSize: 14, color: C.slate, align: 'center', valign: 'top' });
    if (i < 4) arrow(s, x + 2.18, 2.02, 0.46, C.line);
  });
  sectionBox(s, 'Why this matters', 'We did not begin with “build five AI agents.” We began with who experiences the problem, what evidence supports the need, and what a safe system must never do. [C02]', 0.7, 4.75, 11.9, 1.05, C.sky, C.blue, 16);
  sectionBox(s, 'Current status rule', 'Old narrative status labels are not evidence. Contracts, artifacts and tests decide what is gated or verified.', 0.7, 5.98, 11.9, 0.72, C.white, C.teal, 14);
}

// 5 — Empathize method
{
  const s = titleSlide('How we Empathized without inventing interviews', 'Literature and system documentation informed needs; journey maps exposed pain and trade-offs.', 'Empathize',
    'Explain that we used three methods: consult evidence, map journeys and use SUMO as a stand-in environment. A team or professor walkthrough is proxy validation, not a stakeholder interview.');
  const methods = [
    ['CONSULT', 'Primary papers, official guidance and product documentation', 'DfT · FHWA · MUTCD · SCATS · SUMO'],
    ['OBSERVE', 'Eight staged User Journeys from approach to recovery', 'Pain, uncertainty, trade-offs and failure'],
    ['IMMERSE', 'SUMO as a controlled street environment', 'Useful for tests; not a substitute for field interviews'],
    ['CHALLENGE', 'Claim flags and a source-type audit', 'Prevent folklore numbers and exaggerated conclusions'],
  ];
  methods.forEach((m, i) => {
    const col = i % 2, row = Math.floor(i / 2), x = 0.65 + col * 6.15, y = 1.65 + row * 2.18;
    rect(s, x, y, 5.9, 1.85, i === 3 ? C.amberLt : (i % 2 ? C.mint : C.sky), i === 3 ? C.amber : (i % 2 ? C.green : C.blue));
    tx(s, m[0], x + 0.2, y + 0.15, 1.2, 0.28, { fontSize: 11, bold: true, color: i === 3 ? C.amber : (i % 2 ? C.green : C.blue) });
    tx(s, m[1], x + 0.2, y + 0.52, 5.5, 0.54, { fontSize: 17, bold: true, color: C.navy });
    tx(s, m[2], x + 0.2, y + 1.18, 5.5, 0.42, { fontSize: 12.5, color: C.slate });
  });
  rect(s, 0.85, 6.18, 11.62, 0.5, C.navy, C.navy);
  tx(s, 'Proxy validation = team/professor walkthrough of assumptions · not an interview with the persona', 1.05, 6.27, 11.22, 0.28, { fontSize: 14, bold: true, color: C.white, align: 'center' });
}

// 6 — Overview
{
  const s = titleSlide('Eight personas: traffic is more than the average car', 'Each persona contributes one need, one accountable component and one main evaluation question.', 'Empathize',
    'Introduce the eight personas quickly. Do not read every card. Tell the professor that the next eight slides show the complete persona canvases.');
  personas.forEach((p, i) => {
    const col = i % 4, row = Math.floor(i / 4), x = 0.5 + col * 3.18, y = 1.58 + row * 2.35;
    rect(s, x, y, 2.95, 2.05, C.white, p.color);
    s.addImage({
      path: personaPhoto(p.photo),
      x: x + 0.12, y: y + 0.12, w: 0.7, h: 0.7,
      rounding: true,
      sizing: { type: 'cover', w: 0.7, h: 0.7 },
    });
    tx(s, `${p.id} · ${p.name}`, x + 0.92, y + 0.14, 1.85, 0.3, { fontSize: 15, bold: true, color: p.color });
    tx(s, p.role, x + 0.92, y + 0.46, 1.85, 0.36, { fontSize: 10.5, color: C.slate });
    tx(s, p.statement, x + 0.18, y + 0.95, 2.59, 0.75, { fontSize: 12.5, italic: true, color: C.navy, align: 'center' });
    pill(s, 'PHOTO CARD NEXT', x + 0.8, y + 1.7, 1.45, p.color);
  });
  tx(s, 'Canonical roster: do not append the alternate six-name IMATM roster as extra people.', 0.6, 6.35, 12.1, 0.34, { fontSize: 12, color: C.red, bold: true, align: 'center' });
}

personas.forEach((persona, index) => personaSlide(persona, index + 1));

// 15 — Shared journey
{
  const s = titleSlide('Shared journey: one street, competing needs', 'An ambulance approaches Maria’s school street while Amara is crossing and Chidi’s late bus arrives.', 'User Journey',
    'Tell this as a story. The point is not to make one persona win every time. The point is to preserve safety, record who pays, and recover after priority.');
  const steps = [
    ['1', 'Request arrives', 'Marcus / Yuki', 'Authenticate route, ETA and urgency'],
    ['2', 'Crossing occupied', 'Amara / Marcus', 'Finish active clearance before conflicting movement'],
    ['3', 'Capacity checked', 'Marcus / David', 'Reject a green into blocked downstream space'],
    ['4', 'Bus request judged', 'Chidi / Rosa', 'Late-only request; record accept/reject reason'],
    ['5', 'Queues watched', 'Maria / David', 'Observe displaced stops and local proxy burden'],
    ['6', 'Failure + recovery', 'Yuki / Omar', 'Degrade visibly; then recover in known stages'],
  ];
  steps.forEach((st, i) => {
    const x = 0.55 + i * 2.08;
    s.addShape(pptx.ShapeType.ellipse, { x: x + 0.57, y: 1.6, w: 0.78, h: 0.78, fill: { color: i < 2 ? C.red : i < 4 ? C.blue : C.green }, line: { color: C.white, width: 1 } });
    tx(s, st[0], x + 0.57, 1.6, 0.78, 0.78, { fontSize: 20, bold: true, color: C.white, align: 'center' });
    if (i < 5) arrow(s, x + 1.48, 1.82, 0.38, C.line);
    tx(s, st[1], x, 2.58, 1.92, 0.38, { fontSize: 14, bold: true, color: C.navy, align: 'center' });
    tx(s, st[2], x, 3.02, 1.92, 0.35, { fontSize: 10.5, bold: true, color: C.teal, align: 'center' });
    tx(s, st[3], x, 3.5, 1.92, 1.05, { fontSize: 12, color: C.slate, align: 'center', valign: 'top' });
  });
  sectionBox(s, 'Design principle', 'Cooperation with explicit safeguards: no specialist may hide the cost imposed on another person.', 0.75, 5.2, 11.82, 0.9, C.navy, C.teal, 18);
  tx(s, 'This is a human-centred scenario story. Implemented deterministic fixtures are shown later.', 0.75, 6.32, 11.82, 0.34, { fontSize: 12.5, italic: true, color: C.slate, align: 'center' });
}

// 16 — Evidence register
{
  const s = titleSlide('Evidence register: what supports a need—and what does not', 'Use the source type before using the number.', 'Evidence discipline',
    'Explain the correction from older deck language. We use a 32-row mixed-source evidence register, not a claim that every row is primary evidence.');
  rect(s, 0.6, 1.55, 12.1, 0.72, C.navy, C.navy);
  tx(s, '32-row mixed-source evidence register, audited by source type', 0.85, 1.68, 11.6, 0.4, { fontSize: 21, bold: true, color: C.white, align: 'center' });
  const types = [
    ['PRIMARY / OFFICIAL', 'Original study, agency guidance or owning documentation', C.green, C.mint],
    ['SECONDARY / VENDOR', 'Useful context; narrower wording and visible source limits', C.blue, C.sky],
    ['TEAM JUDGEMENT', 'Priority, weights and architecture scores—not measurements', C.purple, C.purpleLt],
    ['PROPOSED TARGET', 'A threshold to test—not a result or universal standard', C.amber, C.amberLt],
  ];
  types.forEach((t, i) => sectionBox(s, t[0], t[1], 0.6 + (i % 2) * 6.15, 2.65 + Math.floor(i / 2) * 1.35, 5.9, 1.08, t[3], t[2], 14));
  sectionBox(s, 'Claim flags', 'No casualty interpretation · no ambient air-quality claim · no invented interviews · no best-episode headline · no Tunis deployment claim', 0.6, 5.55, 12.1, 0.86, C.redLt, C.red, 16);
  tx(s, 'Method and persona status [C02] · full safe wording lives in presentation-claim-ledger.json', 0.65, 6.55, 12.0, 0.3, { fontSize: 11, color: C.slate, align: 'center' });
}

// 17 — Define
{
  const s = titleSlide('Define: the problem is not “reduce average car delay”', 'Averages can hide starvation, displacement, fragility and unexplained trade-offs.', 'Define',
    'Contrast the wrong technical framing with the human-centred framing. The system exists to make distinct needs first-class and trade-offs visible.');
  sectionBox(s, 'Wrong framing', '“Build five AI agents and reduce mean vehicle delay.”\n\nThat is a builder wish. It says nothing about who is harmed, safety, failure or evidence.', 0.65, 1.65, 5.8, 2.0, C.redLt, C.red, 17);
  sectionBox(s, 'Human-centred framing', 'Street users and operators need signal control that treats distinct needs as first-class objectives with visible trade-offs—because throughput-only control hides who pays and can degrade silently.', 6.85, 1.65, 5.82, 2.0, C.mint, C.green, 17);
  const hidden = [
    ['MEAN DELAY', 'can hide unfinished and extreme trips'], ['FAST BUS', 'does not guarantee regular headways'],
    ['GREEN FOR EV', 'does not create downstream space'], ['NETWORK CO₂', 'can hide a worse school-adjacent street'],
  ];
  hidden.forEach((h, i) => sectionBox(s, h[0], h[1], 0.65 + i * 3.04, 4.15, 2.82, 1.25, i % 2 ? C.sky : C.white, i % 2 ? C.blue : C.teal, 13.5));
  rect(s, 1.05, 5.85, 11.23, 0.68, C.navy, C.navy);
  tx(s, 'Design goal: measurable, constrained, explainable decisions that remain safe when data, messages or models fail.', 1.25, 5.98, 10.83, 0.38, { fontSize: 16, bold: true, color: C.white, align: 'center' });
}

// 18 — POV + HMW
{
  const s = titleSlide('POV statements become “How might we” questions', 'User + need + insight → a question broad enough for multiple solutions.', 'Define',
    'Show that each persona need becomes a design question. Read only the integrated question and one example, such as Amara or Marcus.');
  const povs = [
    ['Amara', 'finish safely', 'How might we reduce waiting without shortening required clearance?'],
    ['David', 'predictable trips', 'How might we improve tails, not only the mean?'],
    ['Chidi', 'regular service', 'How might lights help headways without prioritising every bus?'],
    ['Rosa', 'understand decisions', 'How might every accept/reject be explainable and reviewable?'],
    ['Marcus', 'passage + recovery', 'How might we create useful space and record civilian cost?'],
    ['Yuki', 'safe command', 'How might we diagnose, override and recover predictably?'],
    ['Maria', 'no displacement', 'How might we show where modelled burdens move?'],
    ['Omar', 'trustworthy alerts', 'How might we separate incident, congestion and bad data?'],
  ];
  povs.forEach((p, i) => {
    const col = i % 2, row = Math.floor(i / 2), x = 0.58 + col * 6.18, y = 1.5 + row * 0.9;
    rect(s, x, y, 5.95, 0.76, row % 2 ? C.white : C.pale, C.line);
    tx(s, p[0], x + 0.12, y + 0.08, 0.82, 0.24, { fontSize: 12, bold: true, color: C.teal });
    tx(s, p[1], x + 0.98, y + 0.08, 1.22, 0.24, { fontSize: 11, bold: true, color: C.slate });
    tx(s, p[2], x + 0.12, y + 0.34, 5.68, 0.34, { fontSize: 11.5, color: C.ink });
  });
  rect(s, 0.8, 5.35, 11.73, 1.08, C.navy, C.navy);
  tx(s, 'INTEGRATED HMW', 1.05, 5.5, 1.45, 0.22, { fontSize: 10, bold: true, color: '76D4CF' });
  tx(s, 'How might we improve urban traffic for every person—not only the average car—while making trade-offs auditable and failure safe?', 1.05, 5.78, 11.2, 0.46, { fontSize: 18, bold: true, color: C.white, align: 'center' });
}

// 19 — Brainstorm
{
  const s = titleSlide('Ideate: diverge before choosing', 'We generated alternatives across flow, emergency, multimodal, sustainability, situation and communication.', 'Ideate',
    'Explain that ideation was not reverse-engineered from the chosen architecture. We considered central, independent, hierarchical, rule-based, learned and language-model approaches.');
  const groups = [
    ['FLOW', 'Fixed-time · actuated · Max-Pressure · independent RL · graph coordination · corridor offsets'],
    ['EMERGENCY', 'Local preemption · corridor pre-clearance · route-aware requests · recovery mode'],
    ['MULTIMODAL', 'Every-bus priority · lateness-gated priority · pedestrian deadline · bus holding'],
    ['SITUATION', 'Persistence · tree model · LightGBM · residual anomaly detection · oracle ablation'],
    ['SUSTAINABILITY', 'Stop/idle proxy · modelled CO₂ · link displacement maps · eco advice'],
    ['COMMUNICATION', 'Perfect comms · typed board · TTL · drop/delay emulator · LLM orchestrator'],
  ];
  groups.forEach((g, i) => sectionBox(s, g[0], g[1], 0.58 + (i % 3) * 4.18, 1.55 + Math.floor(i / 3) * 1.55, 3.94, 1.25, i % 2 ? C.mint : C.sky, i % 2 ? C.green : C.blue, 12.5));
  sectionBox(s, 'Research context—not our results', `RESCO, T-REX, CoLLMLight and communication-reliability work helped us ask harder questions about stability, incidents, timing and failures. ${evidenceTag(['C11','C12','C13','C14'])}`, 0.58, 4.92, 12.3, 1.15, C.white, C.purple, 14);
  tx(s, 'Divergence rule: generate first; judge later.', 0.75, 6.33, 11.85, 0.34, { fontSize: 16, bold: true, color: C.teal, align: 'center' });
}

// 20 — Worst ideas
{
  const s = titleSlide('Worst Possible Idea: invert a bad design into a safeguard', 'Deliberately unsafe ideas made hidden assumptions visible.', 'Ideate',
    'Use the first two examples to explain the technique: describe a deliberately bad idea, identify why it fails, then turn that failure into a requirement.');
  const rows = [
    ['LLM sets lights', 'Latency and failure are wrong for safety-critical actuation', 'Synapse explains; never actuates'],
    ['All agents write', 'Conflicting commands and unclear accountability', 'One signal writer: A1'],
    ['Always preempt EV', 'Blocked exits and hidden civilian cost', 'Capacity check + separate externality'],
    ['Every bus gets green', 'Early buses consume recovery time', 'Lateness/headway evidence required'],
    ['Trust perfect data', 'Stale or missing messages look healthy', 'TTL, visible disposition and local fallback'],
    ['Show best episode', 'Selects an extreme and hides instability', 'Matched evidence + null/negative results'],
  ];
  tx(s, 'BAD IDEA', 0.65, 1.5, 2.65, 0.3, { fontSize: 10, bold: true, color: C.red });
  tx(s, 'WHY IT FAILS', 3.35, 1.5, 4.15, 0.3, { fontSize: 10, bold: true, color: C.amber });
  tx(s, 'SAFEGUARD CREATED', 7.75, 1.5, 4.85, 0.3, { fontSize: 10, bold: true, color: C.green });
  rows.forEach((r, i) => {
    const y = 1.88 + i * 0.72;
    rect(s, 0.58, y, 12.16, 0.62, i % 2 ? C.white : C.pale, C.line);
    tx(s, r[0], 0.75, y + 0.08, 2.45, 0.42, { fontSize: 13, bold: true, color: C.red });
    tx(s, r[1], 3.35, y + 0.08, 4.05, 0.42, { fontSize: 12.5, color: C.ink });
    tx(s, r[2], 7.75, y + 0.08, 4.7, 0.42, { fontSize: 13, bold: true, color: C.green });
  });
}

// 21 — SCAMPER
{
  const s = titleSlide('SCAMPER: rethink a conventional traffic controller', 'Seven prompts generated concrete features without assuming one AI model.', 'Ideate',
    'SCAMPER is an ideation checklist. Give two examples: substitute assumed demand with observed queues; reverse the authority so specialists ask and one controller acts.');
  const items = [
    ['S', 'Substitute', 'Assumed demand → observed queues and downstream capacity'],
    ['C', 'Combine', 'Local flow + typed emergency, pedestrian and transit evidence'],
    ['A', 'Adapt', 'Max-Pressure and deterministic recovery from adaptive control'],
    ['M', 'Modify', 'Count people, tails and externalities—not only vehicles'],
    ['P', 'Put to use', 'The same observations support forecasts and incident residuals'],
    ['E', 'Eliminate', 'Perfect communication and unlimited priority assumptions'],
    ['R', 'Reverse', 'Specialists ask; one authority acts; active crossing outranks EV'],
  ];
  items.forEach((it, i) => {
    const col = i < 4 ? 0 : 1, row = i < 4 ? i : i - 4, x = col === 0 ? 0.65 : 6.72, y = 1.5 + row * 1.15;
    s.addShape(pptx.ShapeType.ellipse, { x, y, w: 0.58, h: 0.58, fill: { color: i % 2 ? C.blue : C.teal }, line: { color: C.white } });
    tx(s, it[0], x, y, 0.58, 0.58, { fontSize: 18, bold: true, color: C.white, align: 'center' });
    tx(s, it[1], x + 0.78, y - 0.02, 1.28, 0.28, { fontSize: 13, bold: true, color: C.navy });
    tx(s, it[2], x + 0.78, y + 0.31, 5.05, 0.5, { fontSize: 12.5, color: C.slate, valign: 'top' });
  });
  sectionBox(s, 'Result', 'SCAMPER did not “prove” the architecture. It generated testable design features that still had to be compared and constrained.', 6.72, 5.2, 5.95, 1.0, C.amberLt, C.amber, 14);
}

// 22 — Comparison
{
  const s = titleSlide('Converge: compare architecture options', 'Scores and weights are team judgements—not empirical evidence.', 'Ideate',
    'Explain that evidence informed the criteria, but the numerical scores are our decision aid. The chosen option wins mainly because safety and auditability are structural.');
  const headers = ['OPTION', 'SAFETY', 'AUDIT', 'EVIDENCE RISK', 'COMPUTE', 'DECISION'];
  const widths = [3.05, 1.45, 1.45, 2.0, 1.45, 2.25];
  let x = 0.6;
  headers.forEach((h, i) => { rect(s, x, 1.52, widths[i], 0.5, C.navy, C.navy, 0); tx(s, h, x + 0.04, 1.6, widths[i] - 0.08, 0.3, { fontSize: 10, bold: true, color: C.white, align: 'center' }); x += widths[i]; });
  const rows = [
    ['Central learned brain', '2/5', '2/5', 'High', 'High', 'Reject'],
    ['Independent junctions', '3/5', '3/5', 'Medium', 'Low', 'Reject'],
    ['Hierarchical MARL', '4/5', '3/5', 'High', 'High', 'Park'],
    ['One actuator + advisers', '5/5', '5/5', 'Lower', 'Medium', 'Choose'],
  ];
  rows.forEach((r, ri) => {
    let xx = 0.6, y = 2.1 + ri * 0.82;
    r.forEach((cell, i) => {
      const chosen = ri === 3;
      rect(s, xx, y, widths[i], 0.68, chosen ? C.mint : (ri % 2 ? C.white : C.pale), chosen ? C.green : C.line, 0);
      tx(s, cell, xx + 0.05, y + 0.08, widths[i] - 0.1, 0.48, { fontSize: i === 0 ? 13 : 12.5, bold: chosen || i === 0, color: chosen ? C.green : C.ink, align: i ? 'center' : 'left' });
      xx += widths[i];
    });
  });
  sectionBox(s, 'Why chosen', 'One writer makes authority testable. Deterministic safety remains outside learning. Specialists can be removed by ablation. Explanations cannot affect actuation.', 0.75, 5.65, 11.85, 0.82, C.sky, C.blue, 15);
  tx(s, 'Illustrative scores only · change the scores and discuss sensitivity before treating the matrix as a decision.', 0.8, 6.55, 11.75, 0.25, { fontSize: 11, italic: true, color: C.amber, align: 'center' });
}

// 23 — Architecture
{
  const s = titleSlide('Chosen solution: five agents, one set of hands on the lights', 'The Control plane is deterministic at the safety boundary; Synapse remains outside actuation.', 'Proposed solution',
    'Follow the arrows from specialist evidence to A1, then safety mask, executor and SUMO. Point out that Synapse only receives immutable evidence and has no arrow to the executor.');
  const agents = [
    ['A2', 'Emergency', 'route · ETA · urgency'], ['A3', 'Multimodal', 'crossing · late transit'],
    ['A4', 'Situation', 'forecast · anomaly'], ['A5', 'Sustainability', 'emission-proxy advice'],
  ];
  agents.forEach((a, i) => {
    const x = 0.5 + i * 2.28;
    sectionBox(s, `${a[0]} · ${a[1]}`, a[2], x, 1.55, 2.05, 0.95, i % 2 ? C.sky : C.mint, i % 2 ? C.blue : C.green, 11.5);
    arrow(s, x + 0.75, 2.57, 0.55, C.line);
  });
  sectionBox(s, 'Typed message board', 'immutable · expiring · reason-coded', 0.5, 3.05, 8.9, 0.72, C.pale, C.teal, 13);
  arrow(s, 4.55, 3.88, 0.62, C.teal);
  sectionBox(s, 'A1 FLOW', 'cooperative Max-Pressure + deterministic arbitration', 3.05, 4.42, 3.75, 0.9, C.amberLt, C.amber, 15);
  arrow(s, 6.98, 4.7, 0.55, C.amber);
  sectionBox(s, 'Safety mask', 'legal phase · clearance · capacity', 7.7, 4.42, 2.25, 0.9, C.redLt, C.red, 12);
  arrow(s, 10.1, 4.7, 0.48, C.red);
  sectionBox(s, 'Executor → SUMO', 'Only A1 writes signals', 10.7, 4.42, 2.1, 0.9, C.mint, C.green, 13);
  sectionBox(s, 'Immutable evidence', 'manifest · messages · decisions · trips · faults', 0.5, 5.82, 5.15, 0.72, C.sky, C.blue, 12.5);
  arrow(s, 5.82, 6.02, 0.5, C.blue);
  sectionBox(s, 'SYNAPSE NEVER ACTUATES', 'reads immutable evidence only', 6.48, 5.82, 3.65, 0.72, C.purpleLt, C.purple, 12);
  tx(s, `Accepted boundary ${evidenceTag(['C16'])}`, 10.4, 5.92, 2.3, 0.35, { fontSize: 11, bold: true, color: C.purple, align: 'center' });
  tx(s, 'Recovery: Max-Pressure → actuated → fixed-time · optional DQN may only precede Max-Pressure', 0.65, 6.72, 12.0, 0.28, { fontSize: 12, bold: true, color: C.navy, align: 'center' });
}

// 24 — Communication
{
  const s = titleSlide('How the agents communicate', 'They do not call each other in a tangled chain; they publish typed evidence and A1 answers requests.', 'Proposed solution',
    'Follow an emergency request: A2 publishes a finite expiring message, the board validates it, A1 reads matching run/scenario evidence, checks safety and capacity, then records one decision and one reply.');
  const flow = [
    ['1', 'SPECIALIST', 'Build finite evidence\nA2/A3/A4/A5'],
    ['2', 'ENVELOPE', 'IDs · time · expiry\npriority · provenance'],
    ['3', 'BOARD', 'Validate · deduplicate\nignore stale/invalid'],
    ['4', 'A1', 'Filter · safety check\nrank deterministically'],
    ['5', 'REPLY + EVENT', 'Accept/reject reason\nimmutable join'],
  ];
  flow.forEach((f, i) => {
    const x = 0.48 + i * 2.58;
    s.addShape(pptx.ShapeType.ellipse, { x: x + 0.75, y: 1.5, w: 0.68, h: 0.68, fill: { color: i === 3 ? C.amber : C.teal }, line: { color: C.white } });
    tx(s, f[0], x + 0.75, 1.5, 0.68, 0.68, { fontSize: 17, bold: true, color: C.white, align: 'center' });
    if (i < 4) arrow(s, x + 2.18, 1.68, 0.34, C.line);
    tx(s, f[1], x, 2.42, 2.2, 0.3, { fontSize: 12, bold: true, color: i === 3 ? C.amber : C.teal, align: 'center' });
    tx(s, f[2], x, 2.84, 2.2, 0.72, { fontSize: 12.5, color: C.slate, align: 'center', valign: 'top' });
  });
  sectionBox(s, 'Envelope identity', 'run_id · scenario_hash · message_id · correlation_id · source · topic · simulation time · expires_at · priority · confidence · schema · payload · provenance', 0.6, 3.95, 12.1, 0.9, C.sky, C.blue, 13.5);
  const tiers = ['active crossing', 'emergency', 'pedestrian deadline', 'conditional late transit', 'general flow', 'sustainability'];
  tiers.forEach((tier, i) => pill(s, `${i + 1} · ${tier}`, 0.6 + i * 2.02, 5.15, 1.83, i < 2 ? C.red : i < 4 ? C.blue : C.green));
  sectionBox(s, 'Failure rule', 'If the board is empty or unavailable, A1 continues legal local Max-Pressure control.', 0.9, 5.75, 11.53, 0.72, C.mint, C.green, 15);
}

// 25 — Scenarios + Tunis
{
  const s = titleSlide('Simulation scenarios: from controlled science to a Tunis showcase', 'Human-centred stories, deterministic fixtures and broader experiments have different evidence strength.', 'Prototype + Test',
    'Separate what is designed, what is already a deterministic fixture and what remains a future showcase. Do not imply the Tunis network or demand has been validated.');
  const scenarioGroups = [
    ['CONTROLLED BASELINES', 'Fixed-time · actuated · cooperative Max-Pressure\nMatched scenario hashes and seeds', C.blue, C.sky],
    ['COOPERATION FIXTURES', 'Active crossing vs emergency · two emergencies · blocked downstream · pedestrian deadline · early/late bus', C.teal, C.mint],
    ['FAILURE FIXTURES', 'Absence · loss · delay · duplicate · expiry · malformed · contradiction · silence · controller recovery · Synapse isolation', C.red, C.redLt],
  ];
  scenarioGroups.forEach((g, i) => sectionBox(s, g[0], g[1], 0.55 + i * 4.25, 1.5, 4.0, 1.55, g[3], g[2], 13.5));
  sectionBox(s, 'Future Tunis showcase', `OpenStreetMap geometry + official scheduled TRANSTU datasets. Dataset format must be verified. Road demand stays explicitly synthetic or calibrated until an observed source is verified. ${evidenceTag(['C15'])}`, 0.65, 3.45, 12.0, 1.15, C.navy, C.teal, 16);
  const labels = [
    ['DESIGNED', 'persona story'], ['IMPLEMENTED', 'code/fixture exists'], ['GATED', 'contract tests pass'], ['VERIFIED', 'independent evidence review'],
  ];
  labels.forEach((l, i) => {
    const x = 0.72 + i * 3.08;
    rect(s, x, 5.05, 2.78, 1.1, i === 3 ? C.mint : C.white, i === 3 ? C.green : C.line);
    tx(s, l[0], x + 0.12, 5.2, 2.54, 0.28, { fontSize: 11, bold: true, color: i === 3 ? C.green : C.blue, align: 'center' });
    tx(s, l[1], x + 0.12, 5.58, 2.54, 0.28, { fontSize: 12.5, color: C.slate, align: 'center' });
  });
  tx(s, 'Never use these four words as synonyms.', 0.7, 6.42, 11.9, 0.3, { fontSize: 13, bold: true, color: C.amber, align: 'center' });
}

// 26 — Data collection
{
  const s = titleSlide('Data collection: input → record → metric → claim', 'Every conclusion must resolve to an immutable run and its evidence files.', 'Data Science',
    'Explain the four layers. Inputs are observations. Records preserve what happened. Metrics summarise outcomes. Claims must cite the run and keep unavailable values empty.');
  const layers = [
    ['INPUTS', 'phase · elapsed time · queues · downstream capacity · route/ETA · crossing state · wait · lateness/headway'],
    ['RECORDS', 'run manifest · state · messages · decisions · trips · faults · transitions · KPIs'],
    ['METRICS', 'safety · completion · mean/P95/max tails · emergency + civilian effects · pedestrian wait · transit regularity · robustness'],
    ['CLAIMS', 'requirement · directional · exploratory · null/negative retained · unavailable is not imputed'],
  ];
  layers.forEach((l, i) => {
    const y = 1.45 + i * 1.1;
    pill(s, l[0], 0.62, y + 0.18, 1.35, i === 3 ? C.amber : C.teal);
    rect(s, 2.15, y, 10.5, 0.82, i % 2 ? C.white : C.pale, C.line);
    tx(s, l[1], 2.4, y + 0.14, 10.0, 0.52, { fontSize: 14, color: C.ink });
  });
  rect(s, 0.75, 5.95, 11.83, 0.72, C.navy, C.navy);
  tx(s, 'JOIN SPINE  ·  run_id  +  scenario_hash  +  event_id  +  message_id', 0.95, 6.08, 11.43, 0.4, { fontSize: 19, bold: true, color: C.white, align: 'center' });
  tx(s, 'Sustainability remains a modelled emission-proxy category; no residential-link ambient observations exist yet.', 0.75, 6.76, 11.83, 0.24, { fontSize: 11.5, color: C.red, align: 'center' });
}

// 27 — Status and limitations
{
  const s = titleSlide('Current evidence status and honest limits', 'The presentation distinguishes verified invariants from unverified performance claims.', 'Status',
    'Read the green statements, then the amber gaps. Rows 07 and 08 prove cooperation and failure behavior in deterministic evidence slices. They do not prove city-scale traffic improvement.');
  sectionBox(s, 'VERIFIED NOW', `Rows 07 and 08 are verified.\n\n• 7 specialist requests → one decision + one reply each\n• 0 specialist signal writes; 0 clearance truncations\n• 8 fault classes → 8 legal local decisions\n• Synapse states → identical action hashes\n\n${evidenceTag(['C17'])}`, 0.65, 1.5, 5.9, 3.65, C.mint, C.green, 14.2);
  sectionBox(s, 'NOT ESTABLISHED YET', '• Multi-seed controller superiority\n• A4/A5 on/off value\n• Stakeholder-validated persona outcomes\n• Tunis network performance\n• Multi-seed confidence intervals', 6.8, 1.5, 5.9, 3.65, C.amberLt, C.amber, 14.2);
  sectionBox(s, 'Known platform boundary', 'Native Windows TraCI works. libsumo remains blocked by Windows application control; no libsumo throughput number is claimed.', 0.65, 5.45, 12.05, 0.88, C.white, C.red, 14.5);
  tx(s, 'Deterministic acceptance fixtures ≠ network-scale deployment estimates.', 0.8, 6.55, 11.75, 0.3, { fontSize: 14, bold: true, color: C.navy, align: 'center' });
}

// 28 — Sources
{
  const s = titleSlide('Resources: where the presentation comes from', 'Full URLs and safe wording are stored in presentation-claim-ledger.json.', 'Sources',
    'Show that the presentation is traceable. The course brief defines the assignment; research motivates needs; ADRs define architecture; gates define current evidence.');
  const groups = [
    ['COURSE + METHOD', 'SUMO_forStudents.docx · course transcription · Design Thinking record', '[C01][C02]'],
    ['PEOPLE + OPERATIONS', 'Vallyon · MUTCD · DfT TAG · PLOS ONE · Nelson/Bullock · SCATS · Kingsley · FHWA', '[C03]–[C10]'],
    ['TRAFFIC RESEARCH', 'RESCO · T-REX · CoLLMLight · Finkelberg · official Eclipse SUMO documentation', '[C11]–[C14]'],
    ['TUNIS DATA', 'OpenStreetMap · Tunisia Ministry of Transport open-data portal · scheduled TRANSTU datasets', '[C15]'],
    ['PROJECT AUTHORITY', 'ADR-0001 · requirements/design · row contracts, artifacts and tests', '[C16][C17]'],
  ];
  groups.forEach((g, i) => {
    const y = 1.42 + i * 0.95;
    pill(s, g[0], 0.6, y + 0.18, 2.2, i === 4 ? C.amber : C.teal);
    rect(s, 3.0, y, 8.55, 0.78, i % 2 ? C.white : C.pale, C.line);
    tx(s, g[1], 3.2, y + 0.12, 8.15, 0.52, { fontSize: 13.5, color: C.ink });
    tx(s, g[2], 11.7, y + 0.15, 0.95, 0.44, { fontSize: 11.5, bold: true, color: C.blue, align: 'center' });
  });
  sectionBox(s, 'Citation rule', 'Literature explains why a need matters. Only CoFlow-5 artifacts and tests can establish what CoFlow-5 did.', 0.75, 6.2, 11.85, 0.62, C.navy, C.teal, 14);
}

// 29 — Corrections appendix
{
  const s = titleSlide('Appendix: corrections applied to older material', 'The new deck does not silently copy stale reports or generated slides.', 'Audit appendix',
    'This slide helps answer “what changed?” Explain that the evidence audit narrowed claims and the accepted ADR replaced historical architecture options.');
  const corrections = [
    ['OLD / UNSAFE', 'CURRENT / SAFE'],
    ['Older deck overstated every evidence row', '32-row mixed-source register, audited by source type'],
    ['Older deck used the wrong school-proximity percentage', '6.4M / 12.5% of the studied US population (2005–2006)'],
    ['“7% survival lost per minute”', '7% lower adjusted odds per additional ALS-response minute in one cohort'],
    ['Shared-policy DQN as core A1', 'Cooperative Max-Pressure required; DQN optional'],
    ['Policy-led recovery ladder', 'Max-Pressure → actuated → fixed-time'],
    ['Prototype/Test labelled only planned', 'Use current gates and verification certificates'],
    ['Tunis GTFS/live demand assumed', 'Verify dataset format; road demand synthetic or calibrated'],
  ];
  corrections.forEach((r, ri) => {
    const y = 1.42 + ri * 0.66;
    const header = ri === 0;
    rect(s, 0.58, y, 5.9, 0.54, header ? C.red : (ri % 2 ? C.redLt : C.white), header ? C.red : C.line, 0);
    rect(s, 6.72, y, 6.03, 0.54, header ? C.green : (ri % 2 ? C.mint : C.white), header ? C.green : C.line, 0);
    tx(s, r[0], 0.75, y + 0.07, 5.55, 0.38, { fontSize: header ? 11 : 12.5, bold: header, color: header ? C.white : C.red, align: header ? 'center' : 'left' });
    tx(s, r[1], 6.9, y + 0.07, 5.67, 0.38, { fontSize: header ? 11 : 12.5, bold: header, color: header ? C.white : C.green, align: header ? 'center' : 'left' });
  });
  tx(s, 'These corrections protect the professor from attractive but unsupported claims.', 0.7, 6.72, 11.93, 0.26, { fontSize: 13, bold: true, color: C.navy, align: 'center' });
}

// 30 — Close
{
  const s = pptx.addSlide(); slideCount += 1; s.background = { color: C.navy };
  pill(s, 'CLOSE', 0.7, 0.55, 1.1, C.teal);
  tx(s, 'People → evidence → problem → ideas → safe architecture', 0.7, 1.3, 11.9, 0.75, { fontFace: 'Aptos Display', fontSize: 34, bold: true, color: C.white, align: 'center' });
  const points = [
    ['8 PERSONAS', 'Traffic is not only cars'], ['5 AGENTS', 'Specialists advise'],
    ['1 WRITER', 'A1 alone may actuate'], ['3 FALLBACK MODES', 'Max-Pressure → actuated → fixed-time'],
  ];
  points.forEach((p, i) => {
    const x = 0.72 + i * 3.05;
    rect(s, x, 2.45, 2.78, 1.45, C.navy2, '335D76');
    tx(s, p[0], x + 0.12, 2.68, 2.54, 0.36, { fontSize: 16, bold: true, color: '70D5CF', align: 'center' });
    tx(s, p[1], x + 0.12, 3.15, 2.54, 0.42, { fontSize: 13.5, color: C.white, align: 'center' });
  });
  rect(s, 1.1, 4.45, 11.13, 1.18, '173E57', C.teal);
  tx(s, 'Our contribution is not an LLM traffic controller. It is a testable decision architecture with explicit authority, safety, evidence and failure behavior.', 1.4, 4.72, 10.53, 0.62, { fontSize: 21, bold: true, color: C.white, align: 'center' });
  tx(s, 'Next research question: do the proposed specialist benefits survive matched experiments without hiding costs?', 0.9, 6.15, 11.53, 0.42, { fontSize: 16, italic: true, color: '9ADCE2', align: 'center' });
  tx(s, 'Questions?', 0.9, 6.78, 11.53, 0.4, { fontSize: 20, bold: true, color: C.white, align: 'center' });
  s.addNotes('Close with the distinction: this is not an LLM traffic controller. It is a reliable decision architecture whose value must be established through matched evidence. Invite questions and use the resources slide to answer where each claim came from.');
}

if (slideCount !== 30) {
  throw new Error(`Expected 30 slides, built ${slideCount}`);
}

const output = path.join(__dirname, process.env.PPTX_OUT || 'CoFlow-5-Synapse-DT-4DS.pptx');
pptx.writeFile({ fileName: output })
  .then(() => console.log(`SUCCESS ${output} slides=${slideCount}`))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
