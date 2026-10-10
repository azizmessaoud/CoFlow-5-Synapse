'use strict';

// CoFlow-5 Synapse — Empathize & Ideation validation, 15 slides.
// Build: node build-validation-15.js
// Visual system matched to the audited light deck: paper #F4F1EA, ink #16222C, teal #1F6B72, amber #E8A33D.

const path = require('path');
const fs = require('fs');
const pptxgen = require('pptxgenjs');

const pptx = new pptxgen();
pptx.defineLayout({ name: 'WIDE', width: 13.333, height: 7.5 });
pptx.layout = 'WIDE';
pptx.author = 'CoFlow-5 Synapse · ESPRIT 4DS';
pptx.title = 'CoFlow-5 Synapse — Empathize and Ideation validation';
pptx.subject = 'User research, evidence, personas, needs, problem statement, ideas, and the selected solution';
pptx.lang = 'en-US';

const C = {
  paper: 'F4F1EA',
  ink: '16222C',
  navy: '14202B',
  teal: '1F6B72',
  amber: 'E8A33D',
  white: 'FBFAF6',
  mute: '5E6A70',
  faint: '8A847C',
  line: 'E4DFD6',
  header: 'E2DFD9',
  rust: '9A4E28',
  soft: 'E7F2F2',
};

const PHOTO = (f) => path.join(__dirname, 'personas', f);

const people = [
  {
    name: 'Amara', age: '74', file: 'p1-amara.png',
    role: 'Retired pedestrian. Uses a cane.',
    statement: 'I need enough time to finish crossing, even when traffic is busy.',
    need: 'Enough time to finish, and a shorter wait.',
    pain: 'Cars get green while she is still crossing.',
    based: 'Pedestrians were 28% of 2023 deaths in the investment case. The 2024 strategy names older people and people with disabilities. Clearance guidance is about 1.07 m/s.',
  },
  {
    name: 'David', age: '41', file: 'p2-david.png',
    role: 'Delivery-van driver.',
    statement: 'I can plan around a longer trip if I know how long it will actually take.',
    need: 'The real duration, including the trip that does not finish.',
    pain: 'A better mean hides unfinished or extreme trips.',
    based: 'Occupants carry most of the health cost in that case. Appraisal guidance uses 0.4 as a reliability ratio. On seed 37, unfinished trips stayed in the count.',
  },
  {
    name: 'Chidi', age: '27', file: 'p3-chidi.png',
    role: 'Frequent bus passenger.',
    statement: 'Buses should arrive regularly, not three at once after a long wait.',
    need: 'Priority only for a late bus or a large gap.',
    pain: 'Three buses arrive together after one long gap.',
    based: 'TRANSTU reported 187.4 million paying passengers in 2018. That is not this year’s headway. Appraisal guidance values waiting time above time on the bus.',
  },
  {
    name: 'Rosa', age: '52', file: 'p4-rosa.png',
    role: 'Incident-report reader. She never changes the light.',
    statement: 'Show me why priority was granted or denied, and let me respond safely.',
    need: 'A reason code, and a record she can read later.',
    pain: 'A refusal with no history.',
    based: 'ONSR compiles the national crash record. SCATS documents monitoring and audit trails. That is an analogy, not a Tunis control room we visited.',
  },
  {
    name: 'Marcus', age: '34', file: 'p5-marcus.png',
    role: 'Urban ambulance crew. We did not ride with one.',
    statement: 'Get us through safely, and make sure traffic recovers after we pass.',
    need: 'A checked exit, then recovery. Delay to others is logged.',
    pain: 'A green light into a full exit only moves the queue.',
    based: 'Civil Protection answers these calls. Preemption can add delay elsewhere. A Taipei minute figure is cited as foreign. Not lives saved.',
  },
  {
    name: 'Omar', age: '55', file: 'p8-omar.png',
    role: 'Network duty officer.',
    statement: 'Tell me what is wrong, why you think so, and whether I can still trust the data.',
    need: 'The class, the confidence, and the freshness.',
    pain: 'A guessed cause, or a frozen screen that looks healthy.',
    based: 'The detector has classes. An anomaly does not name a cause. A 25–30% congestion share is a US citation, not a map of these junctions.',
  },
];

function text(s, v, x, y, w, h, size, color, extra = {}) {
  s.addText(v, {
    x, y, w, h,
    fontFace: extra.fontFace || 'Aptos',
    fontSize: size,
    color,
    margin: 0,
    valign: extra.valign || 'top',
    ...extra,
  });
}

function card(s, x, y, w, h, fill = C.white) {
  s.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h,
    rectRadius: 0.08,
    fill: { color: fill },
    line: { color: C.line, width: 1 },
  });
}

function paper(notes) {
  const s = pptx.addSlide();
  s.background = { color: C.paper };
  s.addNotes(notes);
  return s;
}

function dark(notes) {
  const s = pptx.addSlide();
  s.background = { color: C.navy };
  s.addNotes(notes);
  return s;
}

function kicker(s, label, color = C.teal) {
  text(s, label, 0.46, 0.28, 10.6, 0.28, 12, color, { bold: true, charSpacing: 1.15 });
}

function title(s, label, color = C.ink) {
  text(s, label, 0.44, 0.56, 12.4, 0.62, 28, color, { bold: true, fontFace: 'Aptos Display' });
}

function footer(s, n, note, color = C.faint) {
  if (note) text(s, note, 0.46, 7.08, 11.2, 0.28, 12, color);
  text(s, String(n).padStart(2, '0'), 12.15, 7.08, 0.72, 0.28, 12, color, { align: 'right' });
}

function photo(s, file, x, y, w, h) {
  const p = PHOTO(file);
  if (!fs.existsSync(p)) throw new Error('missing portrait ' + file);
  s.addImage({ path: p, x, y, w, h, sizing: { type: 'cover', w, h } });
}

function ruleTable(s, rows, x, y, w, h, colW, opts = {}) {
  const size = opts.size || 13;
  const shaped = rows.map((row, ri) => row.map((cell, ci) => {
    const rust = opts.rustCol === ci && ri > 0;
    return {
      text: String(cell),
      options: {
        fill: { color: ri === 0 ? C.header : C.white },
        color: rust ? C.rust : (ri === 0 ? '5C656A' : C.ink),
        bold: ri === 0 || ci === 0,
        align: 'left',
        valign: 'middle',
        fontFace: 'Aptos',
        fontSize: ri === 0 ? 11 : size,
        margin: [5, 8, 5, 8],
      },
    };
  }));
  s.addTable(shaped, {
    x, y, w, h, colW,
    border: [
      { pt: 0.6, color: 'E7E2D8' },
      { pt: 0.6, color: 'E7E2D8' },
      { pt: 0.6, color: 'E7E2D8' },
      { pt: 0.6, color: 'E7E2D8' },
    ],
    fontFace: 'Aptos',
    valign: 'middle',
  });
}

function halfPersona(s, p, x) {
  const y = 1.4;
  const w = 6.18;
  const h = 5.52;
  card(s, x, y, w, h);
  photo(s, p.file, x + 0.18, y + 0.2, 2.02, 2.69);
  s.addShape(pptx.ShapeType.rect, {
    x: x + 2.4, y: y + 0.28, w: 0.06, h: 0.62,
    fill: { color: C.teal }, line: { color: C.teal },
  });
  const tx = x + 2.58;
  const tw = w - 2.78;
  text(s, `${p.name}, ${p.age}`, tx, y + 0.22, tw, 0.36, 20, C.ink, { bold: true, fontFace: 'Aptos Display' });
  text(s, p.role, tx, y + 0.6, tw, 0.52, 13, C.mute);
  text(s, `“${p.statement}”`, tx, y + 1.18, tw, 1.45, 14, C.ink, { italic: true });

  const blocks = [
    ['NEED', p.need],
    ['PAIN', p.pain],
    ['BASED ON', p.based],
  ];
  blocks.forEach((b, i) => {
    const by = y + 3.08 + i * 0.78;
    text(s, b[0], x + 0.22, by, w - 0.44, 0.2, 11, C.teal, { bold: true, charSpacing: 0.6 });
    text(s, b[1], x + 0.22, by + 0.2, w - 0.44, 0.54, 13, C.ink);
  });
}

// 01 Title
{
  const s = dark('Presented to Fedi Baccar. Team from ADR-0002. Claim: the system evaluates a constrained incident response in simulation and keeps a record of each decision. It does not prevent accidents in Tunisia.');
  text(s, 'ESPRIT 4DS  ·  DESIGN THINKING VALIDATION', 0.55, 0.42, 9.2, 0.3, 13, C.amber, { bold: true, charSpacing: 1.2 });
  text(s, 'CoFlow-5 Synapse', 0.52, 1.85, 9.4, 0.85, 48, 'F4F1EA', { bold: true, fontFace: 'Aptos Display' });
  text(s, 'Empathize and Ideation for a simulated, auditable traffic-signal controller in incident response.', 0.55, 2.8, 8.6, 0.85, 18, 'C9D3D8');
  text(s, 'Presented to Fedi Baccar', 0.55, 5.15, 8.5, 0.32, 16, 'F4F1EA');
  text(s, 'Aziz Messaoud  ·  Eya Laourine  ·  Fares Ben Kacem', 0.55, 5.55, 8.8, 0.28, 14, 'C9D3D8');
  text(s, 'Mohamed Aymen Hamzaoui  ·  Oumayma Saddouri  ·  Ranim Ben Salem', 0.55, 5.88, 9.2, 0.28, 14, 'C9D3D8');
  text(s, 'September 2026', 0.55, 6.28, 4, 0.28, 14, C.amber);
  text(s, 'Research  →  Evidence  →  Personas  →  Needs  →  Problem  →  Ideas  →  Solution', 0.55, 6.9, 10.2, 0.28, 13, '8AA0AD');

  s.addShape(pptx.ShapeType.roundRect, {
    x: 11.15, y: 1.35, w: 1.28, h: 3.55,
    rectRadius: 0.62,
    fill: { color: '1C2E3C' },
    line: { color: '1C2E3C' },
  });
  s.addShape(pptx.ShapeType.ellipse, { x: 11.46, y: 1.62, w: 0.66, h: 0.66, fill: { color: '3E4E5A' }, line: { color: '3E4E5A' } });
  s.addShape(pptx.ShapeType.ellipse, { x: 11.46, y: 2.55, w: 0.66, h: 0.66, fill: { color: C.amber }, line: { color: C.amber } });
  s.addShape(pptx.ShapeType.ellipse, { x: 11.46, y: 3.48, w: 0.66, h: 0.66, fill: { color: '3E4E5A' }, line: { color: '3E4E5A' } });
  s.addShape(pptx.ShapeType.rect, { x: 11.64, y: 4.9, w: 0.3, h: 0.7, fill: { color: '1C2E3C' }, line: { color: '1C2E3C' } });
  footer(s, 1, '', '8AA0AD');
}

// 02 Problem context
{
  const s = paper('Why it matters: a signal change hits the person still crossing, the unfinished trip, the bus gap, and the people who must read a refusal, a full exit, or a stale sensor. No public adaptive-signal network in Tunis was found. This slide does not claim the project prevents deaths.');
  kicker(s, 'EMPATHIZE  ·  1  ·  PROBLEM CONTEXT');
  title(s, 'One signal decision hits several people at once');
  const items = [
    ['AMARA', 'A light changes while someone\nis still crossing.', 'Pedestrians were 28% of 2023 deaths in the WHO investment case quoting ONSR. The 2024 strategy names older people and people with disabilities.'],
    ['DAVID', 'A better average can hide a trip\nthat never finishes.', 'Vehicle occupants carry most of the health cost in the same investment case.'],
    ['CHIDI', 'Buses bunch. An early bus\nis then treated as urgent.', 'TRANSTU reported 187.4 million paying passengers in 2018. That is not this year’s headway.'],
    ['ROSA  ·  MARCUS  ·  OMAR', 'A refusal, a full exit, or a stale\nsensor can look like nothing.', 'The report reader, the crew, and the duty officer each need a record they can check.'],
  ];
  items.forEach((item, i) => {
    const x = 0.42 + (i % 2) * 6.46;
    const y = 1.48 + Math.floor(i / 2) * 2.68;
    card(s, x, y, 6.28, 2.52);
    text(s, '→   ' + item[0], x + 0.24, y + 0.18, 5.8, 0.28, 13, C.teal, { bold: true, charSpacing: 0.6 });
    text(s, item[1], x + 0.24, y + 0.52, 5.8, 0.78, 16, C.ink, { bold: true });
    text(s, item[2], x + 0.24, y + 1.38, 5.8, 0.95, 14, C.mute);
  });
  footer(s, 2, 'No public adaptive-signal network in Tunis was found.');
}

// 03 Target users
{
  const s = paper('Six groups named by a source. Ages and jobs on the persona cards are design readings, not interviews. Motorcyclists were 32% of 2023 deaths in the investment case. They are affected. This arc does not give them a persona.');
  kicker(s, 'EMPATHIZE  ·  2  ·  TARGET USERS');
  title(s, 'Six groups. Each one is named by a source.');
  ruleTable(s, [
    ['Who is affected', 'What the source says', 'Persona'],
    ['Pedestrians, including older people and people with disabilities', '28% of 2023 deaths. Named in the 2024 strategy.', 'Amara'],
    ['Occupants of motor vehicles', 'Most of the health cost in the same case.', 'David'],
    ['TRANSTU passengers in Greater Tunis', '187.4 million paying passengers in 2018.', 'Chidi'],
    ['Readers of the crash and incident record', 'ONSR compiles the national record. One reader.', 'Rosa'],
    ['Road emergency crews', 'Civil Protection answers the calls. We did not ride along.', 'Marcus'],
    ['The person who must trust the alert', 'A residual is not a cause.', 'Omar'],
  ], 0.42, 1.46, 12.5, 5.4, [5.15, 5.35, 2.0], { size: 13 });
  footer(s, 3, 'Motorcyclists were 32% of those deaths. They are affected. They are not a persona here.');
}

// 04 Evidence
{
  const s = paper('Sources: WHO country profile; WHO/UNIATF investment case quoting ONSR; La Presse briefing of ONSR, 17 Jan 2025; TRANSTU activity report 2018; harness/work/10c-evidence-page seed 37. Interviews, questionnaires, and ride-alongs were not collected. Tunis governorate 2024, same La Presse article: 953 crashes, 136 deaths. Not one intersection. Seed 37: fixed-time 71/84, mean wait 13.17 s, P95 33 s; actuated 84/84, 10.35 s, P95 16 s; cooperative Max-Pressure 70/84, 14.21 s, P95 25 s. Classroom watch is seed 53, not this row.');
  kicker(s, 'EMPATHIZE  ·  3  ·  USER RESEARCH AND EVIDENCE');
  title(s, 'What we used, and what we did not collect.');

  const methods = [
    ['Interviews', 'Not collected', 'Nothing. No quote.'],
    ['Questionnaires', 'Not collected', 'Nothing. No percentage from us.'],
    ['Observation', 'Not done', 'Nothing about a crew or one crossing.'],
    ['Existing data', 'Used', 'WHO, the investment case, La Presse, TRANSTU 2018.'],
    ['Literature', 'Used', 'Clearance, reliability, an audit-trail analogy.'],
    ['Simulation', 'One seed', 'Mixed. No winner. Not a Tunis result.'],
  ];
  methods.forEach((m, i) => {
    const y = 1.46 + i * 0.88;
    card(s, 0.42, y, 6.35, 0.8);
    text(s, m[0], 0.6, y + 0.1, 2.3, 0.28, 14, C.ink, { bold: true });
    text(s, m[1], 2.9, y + 0.1, 3.6, 0.28, 13, m[1] === 'Used' || m[1] === 'One seed' ? C.teal : C.rust, { bold: true });
    text(s, m[2], 0.6, y + 0.4, 5.95, 0.3, 13, C.mute);
  });

  card(s, 6.95, 1.46, 5.95, 1.7, C.navy);
  text(s, '5,796', 7.15, 1.58, 5.55, 0.78, 40, C.amber, { bold: true, fontFace: 'Aptos Display' });
  text(s, 'crashes in 2023, in both accounts', 7.18, 2.4, 5.5, 0.28, 14, 'F4F1EA', { bold: true });
  text(s, 'The crash total matches. The death total does not.', 7.18, 2.7, 5.5, 0.28, 13, 'C9D3D8');

  card(s, 6.95, 3.28, 2.9, 1.55);
  text(s, '2,273', 7.1, 3.4, 2.6, 0.58, 28, C.ink, { bold: true, fontFace: 'Aptos Display' });
  text(s, 'deaths, and 7,909 injuries. Investment case, quoting ONSR.', 7.1, 4.05, 2.6, 0.62, 12, C.mute);

  card(s, 10.0, 3.28, 2.9, 1.55);
  text(s, '1,216', 10.15, 3.4, 2.6, 0.58, 28, C.ink, { bold: true, fontFace: 'Aptos Display' });
  text(s, 'deaths. La Presse briefing of ONSR, 17 Jan 2025.', 10.15, 4.05, 2.6, 0.62, 12, C.mute);

  s.addShape(pptx.ShapeType.rect, { x: 6.95, y: 5.02, w: 0.07, h: 0.72, fill: { color: C.teal }, line: { color: C.teal } });
  text(s, 'We show both. We do not average them.', 7.18, 5.0, 5.6, 0.32, 15, C.ink, { bold: true });
  text(s, 'A single number would hide a gap of 1,057 deaths.', 7.18, 5.34, 5.6, 0.32, 13, C.mute);

  card(s, 6.95, 5.9, 5.95, 1.02);
  text(s, 'SEED 37  ·  ONE MATCHED RUN', 7.12, 6.0, 5.6, 0.22, 11, C.teal, { bold: true, charSpacing: 0.5 });
  text(s, 'Fixed 71/84   ·   Actuated 84/84   ·   Max-Pressure 70/84', 7.12, 6.24, 5.6, 0.26, 13, C.ink, { bold: true });
  text(s, 'Unfinished trips stayed in. Mixed. No winner.', 7.12, 6.52, 5.6, 0.26, 13, C.mute);
  footer(s, 4, 'Primary research is the gap we name first.');
}

// 05 Findings
{
  const s = paper('Each finding limits the claim. Finding 3 is seed 37 only. Finding 4: no public adaptive network found, and 2018 ridership is not today’s headway. Cause classes from the same La Presse briefing, not a model of our junction: inattention about 42% of crashes, speeding about 14% of crashes and about 30% of deaths, unsafe pedestrian crossing about 8% of crashes.');
  kicker(s, 'EMPATHIZE  ·  4  ·  KEY FINDINGS');
  title(s, 'Five findings we can defend.');
  const findings = [
    ['The people harmed are named in the counts.', 'Pedestrians, occupants, and public-transport passengers. The 2024 strategy also names older people and people with disabilities.'],
    ['2023 has two death totals beside one crash total.', '2,273 and 1,216, with the same 5,796 crashes. A single death number would hide that.'],
    ['A mean can improve while trips stay unfinished.', 'On seed 37, actuated finished more trips. Cooperative Max-Pressure did not win.'],
    ['We do not have a live Tunis signal network, or today’s bus gap.', 'No public adaptive-signal network was found. A 2018 passenger total is not a headway.'],
    ['An alert can go beyond the evidence.', 'Naming a cause, or showing a stale sensor as healthy, would do that.'],
  ];
  findings.forEach((f, i) => {
    const y = 1.46 + i * 1.08;
    card(s, 0.42, y, 12.5, 0.98);
    text(s, String(i + 1), 0.62, y + 0.22, 0.45, 0.5, 22, C.teal, { bold: true, fontFace: 'Aptos Display' });
    text(s, f[0], 1.25, y + 0.14, 11.4, 0.34, 16, C.ink, { bold: true });
    text(s, f[1], 1.25, y + 0.5, 11.4, 0.36, 14, C.mute);
  });
  footer(s, 5, 'These are limits on what the solution may say.');
}

// 06–08 Personas
const pairs = [
  [0, 1, 'EMPATHIZE  ·  5  ·  PERSONAS  ·  AMARA AND DAVID', 'The crossing, and the trip that may not finish.'],
  [2, 3, 'EMPATHIZE  ·  5  ·  PERSONAS  ·  CHIDI AND ROSA', 'The bus gap, and the reader of the refusal.'],
  [4, 5, 'EMPATHIZE  ·  5  ·  PERSONAS  ·  MARCUS AND OMAR', 'The crew at a full exit, and the officer who must trust the data.'],
];
pairs.forEach((pair, idx) => {
  const s = paper('Design readings, not interviews. Statements are syntheses, not quotes. Portraits are illustrations. ' + people[pair[0]].based + ' ' + people[pair[1]].based);
  kicker(s, pair[2]);
  title(s, pair[3]);
  halfPersona(s, people[pair[0]], 0.4);
  halfPersona(s, people[pair[1]], 6.74);
  footer(s, 6 + idx, 'Design readings, not interviews. Photos are illustrations.');
});

// 09 Needs
{
  const s = paper('Needs, pains, and expectations taken from the six cards. Not from an interview.');
  kicker(s, 'EMPATHIZE  ·  6  ·  NEEDS AND PAIN POINTS');
  title(s, 'Six needs. Six pains. Six expectations.');
  ruleTable(s, [
    ['Who', 'Need', 'Pain', 'Expectation'],
    ['Amara', 'Enough time to finish', 'Green while she is still crossing', 'Conflicting green stays held'],
    ['David', 'The real duration, bad trip included', 'A better mean hides the unfinished trip', 'Unfinished trips stay on the page'],
    ['Chidi', 'A regular gap', 'Three buses after one long wait', 'An early bus gets nothing'],
    ['Rosa', 'A reason she can read later', 'A refusal with no history', 'A citation, or an abstention'],
    ['Marcus', 'A path through, then recovery', 'Green into a full exit', 'Exit checked. Others’ delay logged.'],
    ['Omar', 'A class he can trust', 'A frozen screen, or a guessed cause', 'Freshness shown. Stale stays stale.'],
  ], 0.42, 1.48, 12.5, 5.35, [1.7, 3.7, 3.7, 3.4], { size: 13 });
  footer(s, 9, 'Each row comes from that persona and the evidence on the previous slides.');
}

// 10 Problem + HMW
{
  const s = paper('The problem statement is refined from the needs table. It is not “reduce deaths in Tunisia.” The six How Might We questions were written from that table. They were not collected in a workshop with users.');
  kicker(s, 'IDEATION  ·  7  ·  PROBLEM STATEMENT AND HOW MIGHT WE');
  title(s, 'One problem. Six questions.');
  card(s, 0.42, 1.4, 12.5, 1.85);
  text(s, 'PROBLEM STATEMENT', 0.64, 1.52, 12, 0.24, 12, C.teal, { bold: true, charSpacing: 0.7 });
  text(s, 'How might a simulated signal serve the person still crossing, the unfinished trip, the bus gap, the reader of the refusal, the crew at a full exit, and the officer who must not be told a residual is a cause — while only one component writes the light, and every decision keeps a source?', 0.64, 1.82, 12.05, 1.25, 16, C.ink);
  text(s, 'Not the problem: “reduce deaths in Tunisia.”  Out of scope: lives saved, measured air, a Tunis deployment, a winner from one seed.', 0.46, 3.36, 12.4, 0.32, 13, C.rust);

  const hmws = [
    ['Amara', 'hold the conflicting green until the crossing finishes, and count every cut?'],
    ['David', 'show unfinished trips beside the mean, so the average cannot hide the tail?'],
    ['Chidi', 'give green only after an unusual gap, and give an early bus nothing?'],
    ['Rosa', 'explain one grant or one denial with a reason code, or abstain?'],
    ['Marcus', 'check the exit before green, then recover, without cutting the crossing?'],
    ['Omar', 'publish the class, the confidence, and the freshness, and refuse to name the cause?'],
  ];
  hmws.forEach((h, i) => {
    const x = 0.42 + (i % 2) * 6.46;
    const y = 3.82 + Math.floor(i / 2) * 1.02;
    card(s, x, y, 6.28, 0.92);
    text(s, h[0].toUpperCase(), x + 0.2, y + 0.1, 5.9, 0.22, 12, C.teal, { bold: true, charSpacing: 0.5 });
    text(s, 'How might we ' + h[1], x + 0.2, y + 0.36, 5.9, 0.46, 13, C.ink);
  });
  footer(s, 10, 'Questions written from the needs table. Not from a workshop.');
}

// 11 Ideas + method
{
  const s = paper('Method: one idea per persona need, written beside the source, then kept or refused. Not SCAMPER. Not mind mapping. Not a workshop with users. Six kept. Nine refused: six beside a persona, plus three that failed for everyone. Refused ideas stay on the record.');
  kicker(s, 'IDEATION  ·  8  ·  IDEAS, AND HOW THEY WERE GENERATED');
  title(s, 'Six kept. Nine refused.');
  card(s, 0.42, 1.38, 12.5, 0.78, 'F3EBE3');
  text(s, 'HOW', 0.62, 1.48, 0.7, 0.22, 12, C.teal, { bold: true, charSpacing: 0.6 });
  text(s, 'One idea per need, written next to its source, then kept or refused with a reason. Not SCAMPER. Not a workshop.', 0.62, 1.72, 12.05, 0.32, 14, C.ink);
  ruleTable(s, [
    ['Who', 'Kept', 'Refused', 'Why refused'],
    ['Amara', 'Hold the green. Count truncations.', 'A camera that guesses her ability.', 'Invents data about her'],
    ['David', 'Keep unfinished trips in the count.', 'A scraped map treated as his trip.', 'Not his trip. No source.'],
    ['Chidi', 'Priority only after a real gap.', 'Green for every bus.', 'Rewards the early bus'],
    ['Rosa', 'One cited explanation, or abstain.', 'A chatbot that negotiates the phase.', 'A second writer on the light'],
    ['Marcus', 'Request, exit check, then recovery.', 'Always-green corridor, or “lives saved.”', 'Cuts the crossing, or overclaims'],
    ['Omar', 'Class, confidence, freshness.', 'A news scrape that declares a crash.', 'Guesses a cause'],
    ['All', '—', 'Map or news as a crash. Heatmap with no denominator. A sentence that writes the light.', 'No source, or a second writer'],
  ], 0.42, 2.3, 12.5, 4.6, [1.45, 3.7, 4.35, 3.0], { size: 12, rustCol: 3 });
  footer(s, 11, 'The refused column is part of the evidence.');
}

// 12 Selection
{
  const s = paper('Five filters. An idea that failed any one of them was dropped. Six passed. Nine failed and stay on the previous slide.');
  kicker(s, 'IDEATION  ·  9  ·  SELECTION OF IDEAS');
  title(s, 'Five filters. Fail one, and the idea is out.');
  const filters = [
    ['Names a person', 'A solution with no affected person is dropped.'],
    ['Points at evidence', 'Published data, literature, or a labelled simulation row.'],
    ['Invents nothing', 'No interview quote, no survey percentage, no Tunis digit we do not have.'],
    ['One writer', 'Specialists may request. Only A1, through the safety mask, sets the phase.'],
    ['Leaves a record', 'Rosa can read a grant, a denial, or an abstention.'],
  ];
  filters.forEach((f, i) => {
    const y = 1.46 + i * 0.95;
    card(s, 0.42, y, 12.5, 0.86);
    text(s, String(i + 1).padStart(2, '0'), 0.62, y + 0.18, 0.7, 0.48, 22, C.teal, { bold: true, fontFace: 'Aptos Display' });
    text(s, f[0], 1.5, y + 0.12, 10.8, 0.3, 16, C.ink, { bold: true });
    text(s, f[1], 1.5, y + 0.46, 10.8, 0.28, 14, C.mute);
  });
  footer(s, 12, 'Applied to all 15 ideas: 6 passed, 9 failed.');
}

// 13 Selected solution
{
  const s = dark('Selected concept: advisers request, A1 alone writes through the safety mask and the signal executor, Synapse explains with a citation or abstains and never reaches TraCI. Recovery after emergency priority: Max-Pressure, then actuated, then fixed-time. This evaluates incident response in simulation. It does not prevent accidents in Tunisia.');
  kicker(s, 'IDEATION  ·  10  ·  FINAL SELECTED IDEA', C.amber);
  text(s, 'Advisers request.', 0.5, 1.35, 12.2, 0.7, 36, 'F4F1EA', { bold: true, fontFace: 'Aptos Display' });
  text(s, 'One writer decides.', 0.5, 2.1, 12.2, 0.7, 36, C.amber, { bold: true, fontFace: 'Aptos Display' });
  text(s, 'The record stays.', 0.5, 2.85, 12.2, 0.7, 36, 'F4F1EA', { bold: true, fontFace: 'Aptos Display' });

  const cols = [
    ['A2  ·  A3  ·  A4  ·  A5', 'Specialists that can only ask.', '8AA0AD'],
    ['A1', 'The only writer, through the safety mask and the signal executor.', C.amber],
    ['SYNAPSE', 'Explains the log with a citation, or abstains. Never reaches TraCI.', '8AA0AD'],
  ];
  cols.forEach((c, i) => {
    const x = 0.5 + i * 4.2;
    s.addShape(pptx.ShapeType.rect, {
      x, y: 4.05, w: 3.7, h: 0.045,
      fill: { color: i === 1 ? C.amber : '8AA0AD' },
      line: { color: i === 1 ? C.amber : '8AA0AD' },
    });
    text(s, c[0], x, 4.22, 3.85, 0.3, 14, i === 1 ? C.amber : 'F4F1EA', { bold: true, charSpacing: 0.4 });
    text(s, c[1], x, 4.56, 3.85, 0.7, 15, 'C9D3D8');
  });
  text(s, 'After priority, recovery is Max-Pressure, then actuated, then fixed-time.', 0.5, 5.7, 12.2, 0.32, 15, 'F4F1EA');
  text(s, 'Evaluates incident response in simulation. It does not prevent accidents in Tunisia.', 0.5, 6.55, 11.2, 0.3, 14, '8AA0AD');
  footer(s, 13, '', '8AA0AD');
}

// 14 The link
{
  const s = paper('The chain the validation asks to see, one row per persona: evidence, pain, the idea we kept, and the behaviour in the selected concept.');
  kicker(s, 'THE LINK  ·  RESEARCH TO SOLUTION');
  title(s, 'Evidence, then the person, then the behaviour.');
  ruleTable(s, [
    ['Persona', 'Evidence', 'Pain', 'Kept idea', 'In the solution'],
    ['Amara', '28% of deaths. Clearance ≈ 1.07 m/s.', 'Green while still crossing', 'Hold the green. Count cuts.', 'A3 asks. A1 holds the green.'],
    ['David', 'Seed 37: 71 / 84 / 70 finished.', 'Mean hides the unfinished trip', 'Keep unfinished trips', 'Unfinished trips stay beside the mean.'],
    ['Chidi', 'TRANSTU 2018. Waiting valued more.', 'Three buses after a long gap', 'Priority only after a real gap', 'A3 asks for a late bus or a gap only.'],
    ['Rosa', 'ONSR record. Audit-trail analogy.', 'A refusal with no history', 'One cited reason, or abstain', 'A reason code on every decision.'],
    ['Marcus', 'Preemption can add network delay.', 'Green into a full exit', 'Request, check, recover', 'A2 asks. A1 checks the exit, then recovers.'],
    ['Omar', 'An anomaly does not name a cause.', 'A guessed cause, or a frozen screen', 'Class, confidence, freshness', 'A4 publishes. Stale leaves A1 on local control.'],
  ], 0.32, 1.42, 12.7, 5.45, [1.35, 3.15, 2.7, 2.55, 2.95], { size: 11 });
  footer(s, 14, 'User research → evidence → personas → needs → problem → ideas → selected solution.');
}

// 15 Close
{
  const s = paper('Say the chain once more. Claim only the simulation record. Name what is still missing: interviews, and more than one seed.');
  kicker(s, 'CLOSE');
  title(s, 'What we claim, and what we leave open.');
  text(s, 'Research  →  Evidence  →  Personas  →  Needs  →  Problem  →  Ideas  →  Solution', 0.46, 1.32, 12.3, 0.3, 14, C.teal, { bold: true });

  card(s, 0.42, 1.8, 6.2, 3.15, C.navy);
  text(s, 'WE CLAIM', 0.66, 2.0, 5.7, 0.28, 13, C.amber, { bold: true, charSpacing: 0.8 });
  text(s, 'The system evaluates a constrained incident response in simulation, and keeps a record of each decision.', 0.66, 2.45, 5.7, 1.5, 20, 'F4F1EA');

  card(s, 6.8, 1.8, 6.1, 3.15);
  text(s, 'WE DO NOT CLAIM', 7.02, 2.0, 5.7, 0.28, 13, C.rust, { bold: true, charSpacing: 0.8 });
  const nos = ['Prevents accidents in Tunisia', 'Lives saved', 'Measured air quality', 'A Tunis deployment', 'A winner from one seed'];
  nos.forEach((n, i) => {
    text(s, '×    ' + n, 7.02, 2.48 + i * 0.42, 5.6, 0.36, 16, C.ink);
  });

  card(s, 0.42, 5.12, 12.48, 1.15);
  text(s, 'STILL OPEN', 0.64, 5.26, 12, 0.24, 12, C.teal, { bold: true, charSpacing: 0.6 });
  text(s, 'No interviews, questionnaires, or ride-alongs. Personas are design readings. One matched seed. A synthetic grid, not a measured Tunis junction.', 0.64, 5.56, 12.05, 0.52, 15, C.ink);
  footer(s, 15, 'Questions.');
}

const outDir = __dirname;
const outName = 'CoFlow-5-Empathize-Ideation-15.pptx';
const output = path.join(outDir, outName);
pptx.writeFile({ fileName: output }).then(() => {
  console.log('SUCCESS ' + output);
}).catch((err) => {
  console.error(err);
  process.exit(1);
});
