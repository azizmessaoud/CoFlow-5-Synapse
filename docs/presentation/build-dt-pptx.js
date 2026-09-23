'use strict';

const path = require('path');
const pptxgen = require('pptxgenjs');

const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = 'CoFlow-5-Synapse · ESPRIT 4DS';
pres.title = 'CoFlow-5-Synapse — Design Thinking Project';
pres.subject = 'Intelligent Multi-Agent Traffic Management';

const C = {
  navy: '0B1628',
  navy2: '0D2341',
  blue: '1D4ED8',
  blueLt: 'DBEAFE',
  amber: 'D97706',
  amberLt: 'FEF3C7',
  green: '059669',
  greenLt: 'D1FAE5',
  red: 'DC2626',
  redLt: 'FEE2E2',
  purple: '7C3AED',
  purpleLt: 'EDE9FE',
  slate: '475569',
  ink: '1E293B',
  rule: 'E2E8F0',
  bg: 'F8FAFC',
  white: 'FFFFFF',
  muted: '94A3B8',
};

function addLabel(slide, text, x, y, w, color) {
  slide.addText(text, {
    x, y, w, h: 0.22,
    fontSize: 8, bold: true, color: color || C.slate,
    charSpacing: 1.5, fontFace: 'Calibri',
    isTextBox: true, margin: 0,
  });
}

function addHeading(slide, text, x, y, w) {
  slide.addText(text, {
    x, y, w, h: 0.46,
    fontSize: 22, bold: true, color: C.ink,
    fontFace: 'Calibri', isTextBox: true, margin: 0,
  });
}

function phaseTag(slide, label, color) {
  slide.addShape(pres.ShapeType.rect, {
    x: 0.5, y: 0.22, w: 2.35, h: 0.26,
    fill: { color },
  });
  slide.addText(label, {
    x: 0.5, y: 0.22, w: 2.35, h: 0.26,
    fontSize: 8, bold: true, color: C.white,
    align: 'center', valign: 'middle',
    charSpacing: 1, fontFace: 'Calibri',
    isTextBox: true, margin: 0,
  });
}

function sectionLine(slide) {
  slide.addShape(pres.ShapeType.line, {
    x: 0.5, y: 0.58, w: 9, h: 0,
    line: { color: C.rule, width: 1 },
  });
}

function honestyBar(slide, text) {
  slide.addShape(pres.ShapeType.roundRect, {
    x: 0.5, y: 5.18, w: 9, h: 0.32,
    fill: { color: C.amberLt },
    rectRadius: 0.04,
  });
  slide.addText(text, {
    x: 0.58, y: 5.18, w: 8.84, h: 0.32,
    fontSize: 9, color: C.amber, valign: 'middle',
    fontFace: 'Calibri', isTextBox: true, margin: 0,
  });
}

// ════════════════════════════════════════
// SLIDE 1 — COVER
// ════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };

  s.addText('ESPRIT  ·  4DS  ·  DATA SCIENCE ENGINEERING  ·  SEPTEMBER 2026', {
    x: 0.6, y: 0.5, w: 8.8, h: 0.22,
    fontSize: 8, color: '93C5FD', bold: true,
    charSpacing: 1.4, fontFace: 'Calibri', isTextBox: true, margin: 0,
  });

  s.addText('CoFlow-5-Synapse', {
    x: 0.6, y: 0.85, w: 8.8, h: 0.7,
    fontSize: 36, bold: true, color: C.white,
    fontFace: 'Calibri', isTextBox: true, margin: 0,
  });

  s.addText('Intelligent Multi-Agent Traffic Management', {
    x: 0.6, y: 1.55, w: 8.8, h: 0.38,
    fontSize: 18, color: 'CBD5E1',
    fontFace: 'Calibri', isTextBox: true, margin: 0,
  });

  s.addText('A cooperative five-agent SUMO system. Only A1 writes lights. Synapse explains and never actuates.', {
    x: 0.6, y: 1.98, w: 8.8, h: 0.32,
    fontSize: 12, color: '93C5FD',
    fontFace: 'Calibri', isTextBox: true, margin: 0,
  });

  s.addShape(pres.ShapeType.line, {
    x: 0.6, y: 2.42, w: 8.8, h: 0,
    line: { color: '1E3A5F', width: 1 },
  });

  const metas = [
    ['METHODOLOGY', 'Design Thinking × Multi-Agent Systems'],
    ['REQUIRED CONTROLLER', 'Cooperative Max-Pressure'],
    ['STATUS', 'Stages 1–3 done · Prototype planned'],
  ];
  metas.forEach(([label, val], i) => {
    const x = 0.6 + i * 3.1;
    s.addText(label, {
      x, y: 2.58, w: 2.9, h: 0.18,
      fontSize: 7, color: '64748B', bold: true, charSpacing: 1,
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
    s.addText(val, {
      x, y: 2.8, w: 2.9, h: 0.4,
      fontSize: 12, color: 'E2E8F0',
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
  });

  s.addShape(pres.ShapeType.rect, {
    x: 0, y: 4.35, w: 10, h: 1.275,
    fill: { color: C.navy2 },
  });
  s.addText('Course How-might-we', {
    x: 0.6, y: 4.48, w: 8.8, h: 0.2,
    fontSize: 8, bold: true, color: '64748B', charSpacing: 1,
    fontFace: 'Calibri', isTextBox: true, margin: 0,
  });
  s.addText('"How might we use data and intelligent agents to make urban traffic more efficient, adaptive, and sustainable?"', {
    x: 0.6, y: 4.7, w: 8.8, h: 0.7,
    fontSize: 14, color: '93C5FD', italic: true,
    fontFace: 'Calibri', isTextBox: true, margin: 0,
  });

  s.addNotes('Cover. Empathize, Define and Ideate are complete. A controlled prototype and partial technical test evidence are gated through Row 10c. Do not claim stakeholder validation, deployment impact, multi-seed inference or controller superiority.');
}

// ════════════════════════════════════════
// SLIDE 2 — DESIGN THINKING OVERVIEW
// ════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };

  addLabel(s, 'OUR PROCESS', 0.5, 0.22, 4);
  sectionLine(s);
  addHeading(s, 'Design Thinking — five stages, in order', 0.5, 0.66, 9);

  const phases = [
    { num: '1', label: 'EMPATHIZE', sub: '8 personas\nJourneys + evidence', color: C.amber, status: 'DONE' },
    { num: '2', label: 'DEFINE', sub: 'Human-centred\nproblem + HMW', color: C.blue, status: 'DONE' },
    { num: '3', label: 'IDEATE', sub: 'Many ideas,\none architecture', color: C.purple, status: 'DONE' },
    { num: '4', label: 'PROTOTYPE', sub: 'SUMO + A1–A5\n+ evidence bundle', color: C.green, status: 'PLANNED' },
    { num: '5', label: 'TEST', sub: 'Baselines, ablations,\nhonest limits', color: C.red, status: 'PLANNED' },
  ];

  phases.forEach((p, i) => {
    const x = 0.45 + i * 1.9;
    s.addShape(pres.ShapeType.ellipse, {
      x: x + 0.4, y: 1.4, w: 0.82, h: 0.82,
      fill: { color: p.color },
    });
    s.addText(p.num, {
      x: x + 0.4, y: 1.4, w: 0.82, h: 0.82,
      fontSize: 20, bold: true, color: C.white,
      align: 'center', valign: 'middle',
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
    if (i < 4) {
      s.addShape(pres.ShapeType.line, {
        x: x + 1.22, y: 1.8, w: 0.68, h: 0,
        line: { color: C.rule, width: 1.5 },
      });
    }
    s.addText(p.label, {
      x, y: 2.38, w: 1.7, h: 0.24,
      fontSize: 10, bold: true, color: p.color, align: 'center',
      charSpacing: 0.6, fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
    s.addText(p.sub, {
      x, y: 2.64, w: 1.7, h: 0.55,
      fontSize: 11, color: C.slate, align: 'center',
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
    const done = p.status === 'DONE';
    s.addShape(pres.ShapeType.roundRect, {
      x: x + 0.35, y: 3.28, w: 1.0, h: 0.22,
      fill: { color: done ? C.greenLt : C.amberLt },
      rectRadius: 0.04,
    });
    s.addText(p.status, {
      x: x + 0.35, y: 3.28, w: 1.0, h: 0.22,
      fontSize: 8, bold: true, color: done ? C.green : C.amber,
      align: 'center', valign: 'middle',
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
  });

  s.addText('The course grades innovation, reasoning, and evidence more than technological complexity. We therefore finished Empathize → Define → Ideate before writing SUMO code, and we will not present Prototype or Test as complete.', {
    x: 0.5, y: 3.7, w: 9, h: 0.7,
    fontSize: 13, color: C.ink,
    fontFace: 'Calibri', isTextBox: true, margin: 0,
  });

  s.addText('Framework: Interaction Design Foundation (Empathize → Define → Ideate → Prototype → Test).', {
    x: 0.5, y: 4.45, w: 9, h: 0.28,
    fontSize: 11, color: C.slate, italic: true,
    fontFace: 'Calibri', isTextBox: true, margin: 0,
  });

  honestyBar(s, 'Personas are research-informed design artifacts, not interview-validated profiles. Expert interviews were planned and not completed.');

  s.addNotes('Slide 2. Stages 1–3 complete. Prototype and Test remain planned. No fabricated interviews.');
}

// ════════════════════════════════════════
// SLIDE 3 — EIGHT PERSONAS
// ════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };

  phaseTag(s, 'PHASE 1 · EMPATHIZE', C.amber);
  sectionLine(s);
  addHeading(s, 'Eight User Personas — not only drivers', 0.5, 0.64, 9);

  const personas = [
    { id: 'P1', name: 'Amara, 74', role: 'Pedestrian (cane)', pain: 'Standard clearance assumes a faster walker', need: 'Enough time to finish crossing', color: C.purple, colorLt: C.purpleLt },
    { id: 'P2', name: 'David, 41', role: 'Delivery driver', pain: 'Mean delay hides late tails', need: 'Predictable journeys, not only shorter ones', color: C.amber, colorLt: C.amberLt },
    { id: 'P3', name: 'Chidi, 27', role: 'Bus rider', pain: 'Bunching, then three buses at once', need: 'Regular arrivals, not a faster late bus', color: C.blue, colorLt: C.blueLt },
    { id: 'P4', name: 'Rosa, 52', role: 'Depot controller', pain: 'Unexplained priority refusals', need: 'See why, then intervene safely', color: C.green, colorLt: C.greenLt },
    { id: 'P5', name: 'Marcus, 34', role: 'Paramedic', pain: 'Green that dumps a queue one junction ahead', need: 'Passage and recovery as one journey', color: C.red, colorLt: C.redLt },
    { id: 'P6', name: 'Yuki, 47', role: 'Traffic engineer', pain: 'Adaptive control degrades silently', need: 'Diagnose, override, disable', color: C.navy, colorLt: 'E2E8F0' },
    { id: 'P7', name: 'Omar, 55', role: 'Duty officer', pain: 'A frozen dashboard can look normal', need: 'What is wrong, why, and how much to trust it', color: C.blue, colorLt: C.blueLt },
  ];

  personas.forEach((p, i) => {
    const col = i % 4;
    const row = Math.floor(i / 4);
    const x = 0.4 + col * 2.38;
    const y = 1.18 + row * 1.92;

    s.addShape(pres.ShapeType.roundRect, {
      x, y, w: 2.26, h: 1.8,
      fill: { color: C.white },
      line: { color: C.rule, width: 0.75 },
      rectRadius: 0.07,
    });
    s.addShape(pres.ShapeType.rect, {
      x, y, w: 2.26, h: 0.36,
      fill: { color: p.colorLt },
    });
    s.addText(p.id + '  ' + p.name, {
      x: x + 0.08, y: y + 0.04, w: 2.1, h: 0.28,
      fontSize: 11, bold: true, color: p.color,
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
    s.addText(p.role, {
      x: x + 0.08, y: y + 0.4, w: 2.1, h: 0.2,
      fontSize: 9, bold: true, color: C.slate,
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
    s.addText('PAIN  ' + p.pain, {
      x: x + 0.08, y: y + 0.64, w: 2.1, h: 0.48,
      fontSize: 10, color: C.ink,
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
    s.addText('NEED  ' + p.need, {
      x: x + 0.08, y: y + 1.16, w: 2.1, h: 0.52,
      fontSize: 10, color: C.green,
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
  });

  honestyBar(s, 'These seven names are the course roster (parent/Maria removed — professor: not evident). Do not stack extra IMATM names.');

  s.addNotes('Eight research-informed personas from the Empathize pack. Not interviews.');
}

// ════════════════════════════════════════
// SLIDE 4 — JOURNEYS
// ════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };

  phaseTag(s, 'PHASE 1 · EMPATHIZE', C.amber);
  sectionLine(s);
  addHeading(s, 'Journeys — pain today vs planned prototype response', 0.5, 0.64, 9);

  const cols = ['STEP', 'TODAY (PAIN)', 'PLANNED CoFlow-5 RESPONSE'];
  const colW = [1.7, 3.55, 3.75];
  const colX = [0.5, 2.2, 5.75];

  cols.forEach((c, i) => {
    s.addText(c, {
      x: colX[i], y: 1.16, w: colW[i], h: 0.2,
      fontSize: 8, bold: true, color: C.slate, charSpacing: 0.7,
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
  });

  function journeyBlock(title, fill, titleColor, rows, y0) {
    s.addShape(pres.ShapeType.rect, {
      x: 0.5, y: y0, w: 9, h: 0.24,
      fill: { color: fill },
    });
    s.addText(title, {
      x: 0.58, y: y0, w: 8.84, h: 0.24,
      fontSize: 10, bold: true, color: titleColor,
      fontFace: 'Calibri', valign: 'middle', isTextBox: true, margin: 0,
    });
    rows.forEach((r, i) => {
      const y = y0 + 0.24 + i * 0.42;
      const bg = i % 2 === 0 ? C.white : C.bg;
      s.addShape(pres.ShapeType.rect, { x: 0.5, y, w: 9, h: 0.42, fill: { color: bg } });
      s.addText(r[0], { x: colX[0], y, w: colW[0], h: 0.42, fontSize: 11, color: C.ink, valign: 'middle', fontFace: 'Calibri', isTextBox: true, margin: [0, 0, 0, 4] });
      s.addText(r[1], { x: colX[1], y, w: colW[1], h: 0.42, fontSize: 11, color: C.red, valign: 'middle', fontFace: 'Calibri', isTextBox: true, margin: [0, 0, 0, 4] });
      s.addText(r[2], { x: colX[2], y, w: colW[2], h: 0.42, fontSize: 11, color: C.green, valign: 'middle', fontFace: 'Calibri', isTextBox: true, margin: [0, 0, 0, 4] });
    });
  }

  journeyBlock(
    'P2 David — delivery driver (predictability, not mean delay)',
    C.amberLt, C.amber,
    [
      ['Plans the day', 'Variable travel time breaks stop windows', 'Run evidence records seeds, scenario hash, unfinished trips'],
      ['Hits a surge', 'Mean “improvement” can hide worse tails', 'Report P95 delay and teleports, not a best episode'],
      ['Finishes route', 'Small delays compound into missed deliveries', 'Compare Max-Pressure vs fixed-time and actuated on matched seeds'],
    ],
    1.38,
  );

  journeyBlock(
    'P5 Marcus — paramedic (passage AND recovery; no lives-saved claim)',
    C.redLt, C.red,
    [
      ['Approaches queue', 'A local green does not clear the exit', 'A2 asks A1 for corridor priority; A1 may refuse with a reason'],
      ['On the crossing', 'Abrupt preemption endangers walkers', 'In-crossing pedestrian outranks emergency; safety mask is mandatory'],
      ['Leaves the area', 'Queues and buses stay broken', 'Recovery is Max-Pressure → actuated → fixed-time; civilian delay is logged'],
    ],
    3.12,
  );

  honestyBar(s, 'Literature (PLOS One 2022: about −7% ALS survival per minute of delay) motivates Marcus’s need. It is not a CoFlow-5 result. Simulation time is never “lives saved.”');

  s.addNotes('Journeys are pain maps plus planned responses. Prototype not built. Do not quote 26→9 min or 31% emergency gains.');
}

// ════════════════════════════════════════
// SLIDE 5 — DEFINE
// ════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };

  phaseTag(s, 'PHASE 2 · DEFINE', C.blue);
  sectionLine(s);
  addHeading(s, 'The problem is not “cut average car delay”', 0.5, 0.64, 9);

  s.addShape(pres.ShapeType.roundRect, {
    x: 0.5, y: 1.18, w: 9, h: 1.55,
    fill: { color: C.blue },
    rectRadius: 0.08,
  });
  s.addText('HUMAN-CENTRED PROBLEM', {
    x: 0.7, y: 1.28, w: 8.6, h: 0.2,
    fontSize: 8, bold: true, color: '93C5FD', charSpacing: 1,
    fontFace: 'Calibri', isTextBox: true, margin: 0,
  });
  s.addText('Street users — pedestrians, drivers, bus riders, emergency crews, and the people who run the network — need signal control that treats their distinct needs as first-class objectives with visible trade-offs, because today each need is handled by a separate mechanism that optimizes vehicle throughput, hides who pays for whom, and degrades silently when conditions or communications fail.', {
    x: 0.7, y: 1.52, w: 8.6, h: 1.1,
    fontSize: 13, color: C.white,
    fontFace: 'Calibri', isTextBox: true, margin: 0,
  });

  const hdrs = ['WHO', 'CORE NEED', 'TODAY’S FAILURE', 'DESIGN OPPORTUNITY'];
  const rW = [1.35, 2.15, 2.7, 2.8];
  const rX = [0.5, 1.85, 4.0, 6.7];
  hdrs.forEach((h, i) => {
    s.addShape(pres.ShapeType.rect, { x: rX[i], y: 2.88, w: rW[i], h: 0.26, fill: { color: 'F1F5F9' } });
    s.addText(h, {
      x: rX[i], y: 2.88, w: rW[i], h: 0.26,
      fontSize: 8, bold: true, color: C.slate, align: 'center', valign: 'middle',
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
  });

  const rows = [
    ['Amara', 'Finish the crossing', 'Clearance fitted to average walkers', 'A3 clearance + one-writer safety mask'],
    ['David / Chidi', 'Predictable trips; regular buses', 'Mean delay; every bus treated like a car', 'Tails + lateness-gated transit requests'],
    ['Marcus', 'Passage and recovery', 'Isolated green; cost to others hidden', 'A2 request + logged civilian delay'],
    ['Yuki / Omar', 'Override and trusted alerts', 'Silent degradation; frozen dashboards', 'Watchdog ladder + reason-coded log'],
    ['Rosa / Omar', 'Explainable priority; trustworthy alerts', 'Unexplained refusals; silent dashboard', 'Reason codes + severity/FAR'],
  ];
  rows.forEach((r, ri) => {
    const y = 3.14 + ri * 0.38;
    const bg = ri % 2 === 0 ? C.white : C.bg;
    rX.forEach((x, ci) => {
      s.addShape(pres.ShapeType.rect, { x, y, w: rW[ci], h: 0.38, fill: { color: bg } });
      s.addText(r[ci], {
        x: x + 0.06, y, w: rW[ci] - 0.1, h: 0.38,
        fontSize: 10, color: ci === 3 ? C.blue : C.ink, valign: 'middle',
        fontFace: 'Calibri', isTextBox: true, margin: 0,
      });
    });
  });

  s.addNotes('Define. Refined HMW: serve every person on the network, not only the average car.');
}

// ════════════════════════════════════════
// SLIDE 6 — IDEATE
// ════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };

  phaseTag(s, 'PHASE 3 · IDEATE', C.purple);
  sectionLine(s);
  addHeading(s, 'Ideas we compared — then cut', 0.5, 0.64, 9);

  const ideas = [
    { title: 'Fixed-time lights', desc: 'Pre-programmed cycles. Honest city baseline.', verdict: 'BASELINE', vc: C.slate, vbg: C.bg },
    { title: 'Actuated control', desc: 'Detectors extend green. Second required baseline.', verdict: 'BASELINE', vc: C.amber, vbg: C.amberLt },
    { title: 'LLM as controller', desc: 'Chat agents set the lights. Wrong latency and failure mode.', verdict: 'REJECTED', vc: C.red, vbg: C.redLt },
    { title: 'Independent RL per junction', desc: 'Each light learns alone. Creates neighbour bottlenecks.', verdict: 'REJECTED', vc: C.red, vbg: C.redLt },
    { title: 'Cooperative Max-Pressure', desc: 'A1 writes lights from local pressure + legal advisory requests.', verdict: 'CHOSEN', vc: C.green, vbg: C.greenLt },
    { title: 'Shared-policy DQN / MARL', desc: 'Learned efficiency after the cooperative core is frozen.', verdict: 'OPTIONAL', vc: C.purple, vbg: C.purpleLt },
  ];

  ideas.forEach((idea, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = 0.5 + col * 3.05;
    const y = 1.18 + row * 1.72;
    const chosen = idea.verdict === 'CHOSEN';

    s.addShape(pres.ShapeType.roundRect, {
      x, y, w: 2.9, h: 1.58,
      fill: { color: chosen ? C.greenLt : C.white },
      line: { color: chosen ? C.green : C.rule, width: chosen ? 1.5 : 0.75 },
      rectRadius: 0.08,
    });
    s.addText(idea.title, {
      x: x + 0.12, y: y + 0.1, w: 2.66, h: 0.3,
      fontSize: 13, bold: true, color: C.ink,
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
    s.addText(idea.desc, {
      x: x + 0.12, y: y + 0.42, w: 2.66, h: 0.68,
      fontSize: 11, color: C.slate,
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
    s.addShape(pres.ShapeType.roundRect, {
      x: x + 0.12, y: y + 1.18, w: 1.15, h: 0.24,
      fill: { color: idea.vbg }, rectRadius: 0.04,
    });
    s.addText(idea.verdict, {
      x: x + 0.12, y: y + 1.18, w: 1.15, h: 0.24,
      fontSize: 9, bold: true, color: idea.vc, align: 'center', valign: 'middle',
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
  });

  s.addText('Why this cut: a single learned agent can “win” one junction and starve the next. Cooperation with one writer is the Ideate result. RL is not required for the course prototype.', {
    x: 0.5, y: 4.7, w: 9, h: 0.4,
    fontSize: 12, color: C.ink, italic: true,
    fontFace: 'Calibri', isTextBox: true, margin: 0,
  });

  s.addNotes('Chosen: cooperative Max-Pressure A1. Rejected: LLM controller, independent RL. Optional: DQN row 15.');
}

// ════════════════════════════════════════
// SLIDE 7 — PROTOTYPE ARCHITECTURE
// ════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };

  phaseTag(s, 'PHASE 4 · PROTOTYPE  ·  PLANNED', C.green);
  sectionLine(s);
  addHeading(s, 'Five agents. One writer. Synapse off the loop.', 0.5, 0.64, 9);

  s.addShape(pres.ShapeType.roundRect, {
    x: 0.5, y: 1.16, w: 6.15, h: 0.7,
    fill: { color: C.amberLt },
    line: { color: C.amber, width: 1 },
    rectRadius: 0.08,
  });
  s.addText('A1 FLOW  —  sole signal writer', {
    x: 0.62, y: 1.2, w: 5.9, h: 0.3,
    fontSize: 14, bold: true, color: C.amber, align: 'center',
    fontFace: 'Calibri', isTextBox: true, margin: 0,
  });
  s.addText('Cooperative Max-Pressure + safety mask  →  SUMO / TraCI', {
    x: 0.62, y: 1.5, w: 5.9, h: 0.28,
    fontSize: 12, color: C.ink, align: 'center',
    fontFace: 'Calibri', isTextBox: true, margin: 0,
  });

  s.addShape(pres.ShapeType.roundRect, {
    x: 6.85, y: 1.16, w: 2.65, h: 0.7,
    fill: { color: C.purpleLt },
    line: { color: C.purple, width: 1 },
    rectRadius: 0.08,
  });
  s.addText('SYNAPSE  (explainer)', {
    x: 6.92, y: 1.22, w: 2.5, h: 0.28,
    fontSize: 11, bold: true, color: C.purple, align: 'center',
    fontFace: 'Calibri', isTextBox: true, margin: 0,
  });
  s.addText('Reads the log. Never TraCI.', {
    x: 6.92, y: 1.5, w: 2.5, h: 0.26,
    fontSize: 11, color: C.ink, align: 'center',
    fontFace: 'Calibri', isTextBox: true, margin: 0,
  });

  const agents = [
    { id: 'A2', name: 'Emergency', job: 'Asks for corridor priority. Cannot write lights.', color: C.red, colorLt: C.redLt },
    { id: 'A3', name: 'Multimodal', job: 'Crossing state + late-bus requests only.', color: C.blue, colorLt: C.blueLt },
    { id: 'A4', name: 'Situation', job: 'Forecasts and incident residuals. Alerts, no actuation.', color: C.purple, colorLt: C.purpleLt },
    { id: 'A5', name: 'Sustainability', job: 'Eco weights from emission proxies. Advice only.', color: C.green, colorLt: C.greenLt },
  ];

  agents.forEach((a, i) => {
    const x = 0.5 + i * 2.38;
    s.addShape(pres.ShapeType.roundRect, {
      x, y: 2.08, w: 2.26, h: 1.7,
      fill: { color: C.white },
      line: { color: a.color, width: 0.9 },
      rectRadius: 0.08,
    });
    s.addShape(pres.ShapeType.rect, {
      x, y: 2.08, w: 2.26, h: 0.52,
      fill: { color: a.colorLt },
    });
    s.addText(a.id, {
      x, y: 2.1, w: 2.26, h: 0.24,
      fontSize: 12, bold: true, color: a.color, align: 'center',
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
    s.addText(a.name, {
      x, y: 2.34, w: 2.26, h: 0.22,
      fontSize: 12, bold: true, color: a.color, align: 'center',
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
    s.addText(a.job, {
      x: x + 0.1, y: 2.7, w: 2.06, h: 0.95,
      fontSize: 12, color: C.ink,
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
  });

  s.addShape(pres.ShapeType.roundRect, {
    x: 0.5, y: 3.94, w: 9, h: 1.12,
    fill: { color: C.bg },
    rectRadius: 0.06,
  });
  s.addText('Arbitration order (A1, not Synapse): person already crossing  →  emergency  →  pedestrian deadline  →  late bus  →  general flow  →  eco.', {
    x: 0.65, y: 4.02, w: 8.7, h: 0.4,
    fontSize: 13, color: C.ink,
    fontFace: 'Calibri', isTextBox: true, margin: 0,
  });
  s.addText('Recovery if A1/control fails: cooperative Max-Pressure → actuated → fixed-time. Optional DQN, if ever enabled, fails into Max-Pressure first.', {
    x: 0.65, y: 4.44, w: 8.7, h: 0.48,
    fontSize: 13, color: C.ink,
    fontFace: 'Calibri', isTextBox: true, margin: 0,
  });

  s.addNotes('Do not draw Synapse as A5 coordinator that issues PHASE_COMMAND. A1 is the only writer.');
}

// ════════════════════════════════════════
// SLIDE 8 — COMMUNICATION
// ════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };

  phaseTag(s, 'PHASE 4 · PROTOTYPE  ·  PLANNED', C.green);
  sectionLine(s);
  addHeading(s, 'Typed messages. A1 continues if the board is empty.', 0.5, 0.64, 9);

  const hdrs = ['MESSAGE', 'FROM', 'TO', 'TRIGGER', 'RULE'];
  const colW = [2.05, 1.45, 1.55, 2.15, 2.1];
  const colX = [0.4, 2.45, 3.9, 5.45, 7.6];

  s.addShape(pres.ShapeType.rect, { x: 0.4, y: 1.18, w: 9.2, h: 0.3, fill: { color: C.navy } });
  hdrs.forEach((h, i) => {
    s.addText(h, {
      x: colX[i] + 0.04, y: 1.18, w: colW[i], h: 0.3,
      fontSize: 8, bold: true, color: '93C5FD', valign: 'middle',
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
  });

  const msgs = [
    ['run_id + scenario_hash', 'Every record', 'Evidence bundle', 'Every run', 'Join key; no orphan rows'],
    ['STATE / observation', 'SUMO adapter', 'A1–A5 (read)', 'Each sim step', 'No specialist writes lights'],
    ['PRIORITY_REQUEST', 'A2 Emergency', 'A1 via board', 'Ambulance on route', 'Expires; A1 accept/reject'],
    ['CROSSING / TRANSIT', 'A3 Multimodal', 'A1 via board', 'Active crossing / late bus', 'Early bus cannot preempt'],
    ['FORECAST / ALERT', 'A4 Situation', 'Board / A1', 'Horizon + residual', 'Stale forecast is ignored'],
    ['ECO_ADVICE', 'A5 Sustainability', 'Board / A1', 'Hot-spot proxy', 'Never overrides safety'],
    ['DECISION event_id', 'A1 Flow', 'Log / Synapse read', 'Every accept or reject', 'Immutable; reason code'],
    ['EXPLANATION', 'Synapse', 'Operator (Yuki/Rosa)', 'After the fact', 'Cannot change the action'],
  ];

  msgs.forEach((r, ri) => {
    const y = 1.48 + ri * 0.4;
    const bg = ri % 2 === 0 ? C.white : C.bg;
    s.addShape(pres.ShapeType.rect, { x: 0.4, y, w: 9.2, h: 0.4, fill: { color: bg } });
    r.forEach((cell, ci) => {
      s.addText(cell, {
        x: colX[ci] + 0.04, y, w: colW[ci] - 0.06, h: 0.4,
        fontSize: ci === 0 ? 10 : 10,
        bold: ci === 0,
        color: ci === 0 ? C.blue : C.ink,
        valign: 'middle',
        fontFace: 'Calibri', isTextBox: true, margin: 0,
      });
    });
  });

  s.addNotes('Join keys: run_id, scenario_hash, event_id, message_id. Synapse never publishes PHASE_COMMAND.');
}

// ════════════════════════════════════════
// SLIDE 9 — TEST PLAN
// ════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };

  phaseTag(s, 'PHASE 5 · TEST  ·  PLANNED', C.red);
  sectionLine(s);
  addHeading(s, 'Five experiment cells we will run — not results', 0.5, 0.64, 9);

  const exps = [
    { id: 'E1', title: 'Rush-hour grid', q: 'Does cooperative Max-Pressure beat matched fixed-time and actuated on mean and tail delay?', color: C.blue },
    { id: 'E2', title: 'Emergency request', q: 'Does A2 reduce emergency travel without truncating an in-crossing pedestrian, and is civilian delay reported?', color: C.red },
    { id: 'E3', title: 'Message / controller fault', q: 'If messages drop or A1 fails, does the ladder Max-Pressure → actuated → fixed-time stay legal?', color: C.amber },
    { id: 'E4', title: 'Off-peak / empty board', q: 'Does A1 keep running on local pressure when A2–A5 are silent?', color: C.green },
    { id: 'E5', title: 'Bus vs pedestrian', q: 'Does an early bus lose to an active crossing, and is the refusal reason logged?', color: C.purple },
  ];

  exps.forEach((e, i) => {
    const y = 1.18 + i * 0.72;
    s.addShape(pres.ShapeType.roundRect, {
      x: 0.5, y, w: 9, h: 0.64,
      fill: { color: C.white },
      line: { color: e.color, width: 0.8 },
      rectRadius: 0.06,
    });
    s.addShape(pres.ShapeType.roundRect, {
      x: 0.62, y: y + 0.12, w: 0.52, h: 0.4,
      fill: { color: C.bg }, rectRadius: 0.04,
    });
    s.addText(e.id, {
      x: 0.62, y: y + 0.12, w: 0.52, h: 0.4,
      fontSize: 12, bold: true, color: e.color,
      align: 'center', valign: 'middle',
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
    s.addText(e.title, {
      x: 1.28, y: y + 0.06, w: 7.95, h: 0.24,
      fontSize: 13, bold: true, color: C.ink,
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
    s.addText(e.q, {
      x: 1.28, y: y + 0.3, w: 7.95, h: 0.26,
      fontSize: 12, color: C.slate,
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
  });

  s.addNotes('Test is planned. Do not fill this slide with 57% / 45% / 79% simulation headlines.');
}

// ════════════════════════════════════════
// SLIDE 10 — EVALUATION DESIGN
// ════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };

  phaseTag(s, 'PHASE 5 · TEST  ·  PLANNED', C.red);
  sectionLine(s);
  addHeading(s, 'How we will judge success (empty until SUMO runs)', 0.5, 0.64, 9);

  const hdrs = ['METRIC', 'PERSONA', 'COMPARE AGAINST', 'HONESTY RULE'];
  const colW = [2.3, 1.7, 2.5, 2.5];
  const colX = [0.5, 2.8, 4.5, 7.0];

  s.addShape(pres.ShapeType.rect, { x: 0.5, y: 1.18, w: 9, h: 0.32, fill: { color: C.navy } });
  hdrs.forEach((h, i) => {
    s.addText(h, {
      x: colX[i] + 0.06, y: 1.18, w: colW[i], h: 0.32,
      fontSize: 8, bold: true, color: '93C5FD', valign: 'middle',
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
  });

  const rows = [
    ['Mean + tail delay, unfinished trips', 'David', 'Fixed-time and actuated', 'No best-episode headline'],
    ['Emergency travel + civilian delay', 'Marcus', 'No-preemption cell', 'Never convert seconds to lives'],
    ['Bus regularity / lateness', 'Chidi / Rosa', 'Every-bus vs late-only requests', 'Early bus cannot buy priority'],
    ['Ped wait, clearance truncations', 'Amara', 'Standard clearance', 'Zero illegal executed actions'],
    ['Idle / HBEFA emission proxy', 'Optional A5 KPI', 'Matched seeds', 'Proxy, not measured air quality'],
    ['Recovery + Synapse-killed actions', 'Yuki / Omar', 'Fault-injection cell', 'Killing Synapse must not change lights'],
  ];

  rows.forEach((r, ri) => {
    const y = 1.5 + ri * 0.52;
    const bg = ri % 2 === 0 ? C.white : C.bg;
    s.addShape(pres.ShapeType.rect, { x: 0.5, y, w: 9, h: 0.52, fill: { color: bg } });
    r.forEach((cell, ci) => {
      s.addText(cell, {
        x: colX[ci] + 0.06, y, w: colW[ci] - 0.08, h: 0.52,
        fontSize: 12, color: ci === 3 ? C.amber : C.ink, valign: 'middle',
        fontFace: 'Calibri', isTextBox: true, margin: 0,
      });
    });
  });

  honestyBar(s, 'Any table of “↓57% wait / ↑45% throughput / 79% bus on-time” is invented. Do not present it as evidence.');

  s.addNotes('Evaluation design only. Results cells stay blank until the harness produces a run evidence bundle.');
}

// ════════════════════════════════════════
// SLIDE 11 — CLAIM FLAGS
// ════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };

  phaseTag(s, 'EVIDENCE DISCIPLINE', C.amber);
  sectionLine(s);
  addHeading(s, 'What we may say vs what we must not', 0.5, 0.64, 9);

  const ok = [
    { t: 'Literature motivates the need', d: 'Perceived wait ≈ 2× actual; wait valued ≈ 2× in-vehicle; ALS delay literature; reliability ratio 0.4. These are citations, not our KPIs.' },
    { t: 'Architecture is a decision', d: 'One writer, Max-Pressure required, Synapse non-actuating, recovery ladder. That is Ideate + ADR-0001, not a measured gain.' },
    { t: 'Prototype will be SUMO evidence', d: 'Paired seeds, ablations, failure injection, DuckDB joins on run_id / scenario_hash / event_id / message_id.' },
  ];
  const no = [
    { t: 'No lives saved', d: 'Simulated emergency seconds must not become predicted survival.' },
    { t: 'No measured air quality', d: 'HBEFA/SUMO figures are emission proxies.' },
    { t: 'No interview quotes', d: 'Personas are research-informed. Interviews were not completed.' },
    { t: 'No RL-required story', d: 'DQN is optional row 15. It cannot block the course prototype.' },
  ];

  ok.forEach((item, i) => {
    const y = 1.18 + i * 0.78;
    s.addShape(pres.ShapeType.roundRect, {
      x: 0.5, y, w: 4.4, h: 0.7,
      fill: { color: C.greenLt },
      rectRadius: 0.06,
    });
    s.addText(item.t, {
      x: 0.62, y: y + 0.06, w: 4.16, h: 0.22,
      fontSize: 12, bold: true, color: C.green,
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
    s.addText(item.d, {
      x: 0.62, y: y + 0.28, w: 4.16, h: 0.36,
      fontSize: 11, color: C.ink,
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
  });

  no.forEach((item, i) => {
    const y = 1.18 + i * 0.88;
    s.addShape(pres.ShapeType.roundRect, {
      x: 5.1, y, w: 4.4, h: 0.8,
      fill: { color: C.redLt },
      rectRadius: 0.06,
    });
    s.addText(item.t, {
      x: 5.22, y: y + 0.08, w: 4.16, h: 0.22,
      fontSize: 12, bold: true, color: C.red,
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
    s.addText(item.d, {
      x: 5.22, y: y + 0.32, w: 4.16, h: 0.4,
      fontSize: 11, color: C.ink,
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
  });

  s.addNotes('Claim flags from the Empathize pack. Required on any professor-facing slide.');
}

// ════════════════════════════════════════
// SLIDE 12 — LIMITATIONS
// ════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };

  phaseTag(s, 'PHASE 5 · TEST  ·  PLANNED', C.red);
  sectionLine(s);
  addHeading(s, 'Known limits — we will keep them visible', 0.5, 0.64, 9);

  const limits = [
    { title: 'Prototype is not built yet', desc: 'This deck is Stages 1–3 plus the planned SUMO architecture. There is no gated smoke test and no experiment table.' },
    { title: 'Simulation is not a city', desc: 'SUMO is a stand-in street. Sensor noise, V2I ambulance detection, and weather are out of the first slice.' },
    { title: 'Tunis demand will be labelled synthetic', desc: 'OSM + TRANSTU GTFS is a showcase after the 4×4 science grid is frozen. It cannot validate deployment.' },
    { title: 'RL is a risk, not a requirement', desc: 'Early reward-shaping failures are expected if DQN is tried later. The course prototype must still work without it.' },
    { title: 'Scale is unproven', desc: 'We start with a small controlled grid. Synapse and UI read precomputed evidence; they are not a 50-junction controller.' },
  ];

  limits.forEach((l, i) => {
    const y = 1.16 + i * 0.74;
    s.addShape(pres.ShapeType.roundRect, {
      x: 0.5, y, w: 9, h: 0.66,
      fill: { color: i % 2 === 0 ? C.white : C.bg },
      line: { color: C.rule, width: 0.75 },
      rectRadius: 0.06,
    });
    s.addText(String(i + 1), {
      x: 0.62, y, w: 0.36, h: 0.66,
      fontSize: 16, bold: true, color: C.amber, valign: 'middle',
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
    s.addText(l.title, {
      x: 1.1, y: y + 0.06, w: 8.2, h: 0.24,
      fontSize: 13, bold: true, color: C.ink,
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
    s.addText(l.desc, {
      x: 1.1, y: y + 0.3, w: 8.2, h: 0.28,
      fontSize: 12, color: C.slate,
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
  });

  s.addNotes('Limitations. Do not claim 5-intersection corridor cleared in 8 seconds — that experiment has not been run.');
}

// ════════════════════════════════════════
// SLIDE 13 — CONCLUSION
// ════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };

  s.addText('CONCLUSION', {
    x: 0.6, y: 0.38, w: 8.8, h: 0.2,
    fontSize: 8, bold: true, color: '93C5FD', charSpacing: 1.5,
    fontFace: 'Calibri', isTextBox: true, margin: 0,
  });
  s.addText('What we designed. What we will prove. What we will not claim.', {
    x: 0.6, y: 0.64, w: 8.8, h: 0.5,
    fontSize: 22, bold: true, color: C.white,
    fontFace: 'Calibri', isTextBox: true, margin: 0,
  });

  s.addShape(pres.ShapeType.line, {
    x: 0.6, y: 1.22, w: 8.8, h: 0,
    line: { color: '1E3A5F', width: 1 },
  });

  const cols = [
    {
      title: 'Designed (Stages 1–3)',
      color: C.blueLt,
      points: [
        'Eight personas, not the average car',
        'Five agents; only A1 writes lights',
        'Max-Pressure required; DQN optional',
        'Synapse explains; never TraCI',
        'Recovery: MP → actuated → fixed-time',
      ],
    },
    {
      title: 'Will prove in SUMO',
      color: C.greenLt,
      points: [
        'Native Windows smoke test first',
        'Evidence bundle with join keys',
        'Paired baselines and ablations',
        'Fault injection + Synapse-kill test',
        'Null results kept, not deleted',
      ],
    },
    {
      title: 'Will not claim',
      color: C.amberLt,
      points: [
        'Lives saved from simulation',
        'Measured city air quality',
        'Interview-validated quotes',
        'Best-episode as the headline',
        'A working product already shipped',
      ],
    },
  ];

  cols.forEach((c, i) => {
    const x = 0.45 + i * 3.15;
    s.addShape(pres.ShapeType.roundRect, {
      x, y: 1.42, w: 3.0, h: 3.15,
      fill: { color: C.navy2 },
      rectRadius: 0.1,
    });
    s.addText(c.title, {
      x: x + 0.14, y: 1.54, w: 2.72, h: 0.36,
      fontSize: 13, bold: true, color: c.color,
      fontFace: 'Calibri', isTextBox: true, margin: 0,
    });
    c.points.forEach((p, pi) => {
      s.addText('·  ' + p, {
        x: x + 0.14, y: 1.98 + pi * 0.48, w: 2.72, h: 0.46,
        fontSize: 12, color: 'CBD5E1',
        fontFace: 'Calibri', isTextBox: true, margin: 0,
      });
    });
  });

  s.addText('CoFlow-5-Synapse  ·  ESPRIT 4DS  ·  Design Thinking Project  ·  September 2026', {
    x: 0.6, y: 4.75, w: 8.8, h: 0.28,
    fontSize: 11, color: C.muted, align: 'center',
    fontFace: 'Calibri', isTextBox: true, margin: 0,
  });
  s.addText('Refined HMW: serve every person on the network — walker, rider, driver, paramedic, operator, resident — not only the average car.', {
    x: 0.6, y: 5.08, w: 8.8, h: 0.36,
    fontSize: 11, color: '93C5FD', italic: true, align: 'center',
    fontFace: 'Calibri', isTextBox: true, margin: 0,
  });

  s.addNotes('Closing. Design Thinking drove the architecture. Prototype/Test are the next lab work, starting at harness row 01.');
}

const outPath = path.join(__dirname, 'CoFlow-5-Synapse-DT-4DS.pptx');
pres.writeFile({ fileName: outPath })
  .then(() => {
    console.log('SUCCESS ' + outPath);
  })
  .catch((err) => {
    console.error(err);
    process.exit(1);
  });
