'use strict';

const fs = require('fs');
const path = require('path');
const pptxgen = require('pptxgenjs');

const pptx = new pptxgen();
pptx.defineLayout({ name: 'TALK', width: 13.333, height: 7.5 });
pptx.layout = 'TALK';
pptx.author = 'CoFlow-5 Synapse · ESPRIT 4DS';
pptx.title = 'CoFlow-5 Synapse — 11-slide talk';
pptx.subject = 'Short professor talk: people, one writer, honest evidence';

const C = {
  navy: '0B1C2C',
  ink: 'F4F7F8',
  mute: '9BB0BD',
  teal: '3DCFC4',
  amber: 'F0A04B',
  red: 'E06B6B',
  white: 'FFFFFF',
  card: '122838',
};
const W = 13.333;
const H = 7.5;
const PHOTO = (name) => path.join(__dirname, 'personas', name);

const faces = [
  { file: 'p1-amara.png', word: 'Time', name: 'Amara' },
  { file: 'p2-david.png', word: 'Predict', name: 'David' },
  { file: 'p3-chidi.png', word: 'Regular', name: 'Chidi' },
  { file: 'p4-rosa.png', word: 'Explain', name: 'Rosa' },
  { file: 'p5-marcus.png', word: 'Pass', name: 'Marcus' },
  { file: 'p6-yuki.png', word: 'Control', name: 'Yuki' },
  { file: 'p7-maria.png', word: 'Home', name: 'Maria' },
  { file: 'p8-omar.png', word: 'Trust', name: 'Omar' },
];

function notes(slide, text) {
  slide.addNotes(text);
}

function label(slide, text, x, y, w = 3) {
  slide.addText(text, {
    x, y, w, h: 0.28,
    fontFace: 'Calibri', fontSize: 11, bold: true, color: C.teal,
    charSpacing: 2, margin: 0,
  });
}

function heading(slide, text, x, y, w = 12, h = 0.9, size = 36) {
  slide.addText(text, {
    x, y, w, h,
    fontFace: 'Calibri', fontSize: size, bold: true, color: C.white, margin: 0,
  });
}

function body(slide, text, x, y, w, h, size = 18, color = C.mute) {
  slide.addText(text, {
    x, y, w, h,
    fontFace: 'Calibri', fontSize: size, color, margin: 0,
  });
}

// 1 Cover
{
  const s = pptx.addSlide();
  s.background = { color: C.navy };
  faces.forEach((f, i) => {
    s.addImage({
      path: PHOTO(f.file),
      x: i * (W / 8), y: 0, w: W / 8, h: H,
      sizing: { type: 'cover', w: W / 8, h: H },
    });
  });
  s.addShape(pptx.ShapeType.rect, {
    x: 0, y: 0, w: W, h: H,
    fill: { color: C.navy, transparency: 42 },
    line: { color: C.navy },
  });
  label(s, 'ESPRIT  ·  4DS  ·  11 SLIDES', 0.7, 1.7, 8);
  heading(s, 'The light should see a person.', 0.7, 2.15, 12, 1.1, 40);
  body(s, 'CoFlow-5 Synapse  ·  eight research-informed personas  ·  one signal writer', 0.7, 3.4, 11, 0.4, 18, C.teal);
  body(s, 'Illustrations, not interviews. [C02]', 0.7, 6.7, 8, 0.3, 13, C.mute);
  notes(s, 'Open on the faces. Say: traffic is not an average car. These portraits are illustrations. Personas are research-informed, not interview-validated. [C02]');
}

// 2 Eight words
{
  const s = pptx.addSlide();
  s.background = { color: C.navy };
  label(s, 'EMPATHIZE', 0.55, 0.32);
  heading(s, 'One street. Eight needs.', 0.55, 0.62, 12, 0.6, 32);
  faces.forEach((f, i) => {
    const col = i % 8;
    const x = 0.35 + col * 1.62;
    s.addImage({
      path: PHOTO(f.file),
      x, y: 1.55, w: 1.48, h: 3.6,
      sizing: { type: 'cover', w: 1.48, h: 3.6 },
    });
    s.addShape(pptx.ShapeType.rect, {
      x, y: 4.55, w: 1.48, h: 1.35,
      fill: { color: C.card }, line: { color: C.card },
    });
    s.addText(f.word, {
      x, y: 4.62, w: 1.48, h: 0.7,
      fontFace: 'Calibri', fontSize: 16, bold: true, color: C.white, align: 'center', margin: 0,
    });
    s.addText(f.name, {
      x, y: 5.28, w: 1.48, h: 0.4,
      fontFace: 'Calibri', fontSize: 12, color: C.mute, align: 'center', margin: 0,
    });
  });
  body(s, 'Do not add extra names. This is the course roster.', 0.55, 6.95, 12, 0.28, 13, C.mute);
  notes(s, 'Point at the words, not the biographies. Amara=time, David=predict, Chidi=regular, Rosa=explain, Marcus=pass, Yuki=control, Maria=home, Omar=trust. Full cards live in the long deck if asked.');
}

// 3 Amara
{
  const s = pptx.addSlide();
  s.background = { color: C.navy };
  s.addImage({
    path: PHOTO('p1-amara.png'),
    x: 0, y: 0, w: 6.4, h: H,
    sizing: { type: 'cover', w: 6.4, h: H },
  });
  label(s, 'P1  ·  AMARA  ·  74', 6.85, 1.7, 6);
  heading(s, 'The light is built for someone faster.', 6.85, 2.15, 6, 1.5, 32);
  body(s, 'Need: finish the crossing.\nFear: cars get green while she is still on it.', 6.85, 3.9, 5.8, 1.1, 20, C.ink);
  body(s, 'Perceived wait can feel about 2× the clock. [C03]  Clearance often assumes ~1.07 m/s. [C04]', 6.85, 5.3, 5.8, 1.0, 15, C.mute);
  notes(s, 'This is a design statement, not a quote from an interview. Evidence motivates the need; it is not a CoFlow-5 result. [C03][C04]');
}

// 4 Collision
{
  const s = pptx.addSlide();
  s.background = { color: C.navy };
  const trio = [
    { file: 'p1-amara.png', who: 'Amara is crossing' },
    { file: 'p5-marcus.png', who: 'Marcus is coming' },
    { file: 'p3-chidi.png', who: 'Chidi is waiting' },
  ];
  trio.forEach((t, i) => {
    const x = 0.35 + i * 4.3;
    s.addImage({
      path: PHOTO(t.file),
      x, y: 0, w: 4.15, h: 5.15,
      sizing: { type: 'cover', w: 4.15, h: 5.15 },
    });
    s.addShape(pptx.ShapeType.rect, {
      x, y: 4.55, w: 4.15, h: 0.6,
      fill: { color: C.navy, transparency: 20 }, line: { color: C.navy },
    });
    s.addText(t.who, {
      x, y: 4.6, w: 4.15, h: 0.48,
      fontFace: 'Calibri', fontSize: 18, bold: true, color: C.white, align: 'center', margin: 0,
    });
  });
  heading(s, 'Who should the light serve first?', 0.55, 5.5, 12.2, 0.7, 34);
  body(s, 'If everyone “wins”, someone on the street loses.', 0.55, 6.3, 12, 0.4, 18, C.teal);
  notes(s, 'Tell the shared journey in 20 seconds. Safety first: person already crossing finishes. Then emergency if the exit is free. Then a late bus with evidence. Record who paid. [C16]');
}

// 5 Answer
{
  const s = pptx.addSlide();
  s.background = { color: C.navy };
  label(s, 'THE RULE', 0.7, 0.7);
  heading(s, 'Five agents. One pair of hands.', 0.7, 1.1, 12, 0.8, 36);
  const agents = [
    ['A2 Emergency', 'asks'],
    ['A3 Walk / bus', 'asks'],
    ['A4 Situation', 'asks'],
    ['A5 Eco advice', 'asks'],
    ['A1 Flow', 'writes the lights'],
  ];
  agents.forEach((a, i) => {
    const x = 0.55 + i * 2.5;
    s.addShape(pptx.ShapeType.roundRect, {
      x, y: 2.4, w: 2.35, h: 2.4,
      fill: { color: i === 4 ? '184D4A' : C.card },
      line: { color: i === 4 ? C.teal : '1E3A4C' },
      rectRadius: 0.1,
    });
    s.addText(a[0], {
      x: x + 0.1, y: 2.7, w: 2.15, h: 0.9,
      fontFace: 'Calibri', fontSize: 18, bold: true, color: C.white, align: 'center', margin: 0,
    });
    s.addText(a[1], {
      x: x + 0.1, y: 3.7, w: 2.15, h: 0.6,
      fontFace: 'Calibri', fontSize: 16, color: i === 4 ? C.teal : C.mute, align: 'center', margin: 0,
    });
  });
  body(s, 'Synapse explains the log. It never presses a light.  Recovery: Max-Pressure → actuated → fixed-time. [C16]', 0.7, 5.2, 12, 0.9, 18, C.mute);
  notes(s, 'A1 is cooperative Max-Pressure. DQN is optional and cannot replace the ladder. Synapse never reaches TraCI. [C16]');
}

// 6 How they talk
{
  const s = pptx.addSlide();
  s.background = { color: C.navy };
  label(s, 'COMMUNICATION', 0.7, 0.7);
  heading(s, 'They post. A1 answers. Then it is over.', 0.7, 1.15, 12, 0.8, 34);
  const steps = [
    ['1', 'Ask', 'A typed, expiring request.'],
    ['2', 'Decide', 'One reason-coded yes or no.'],
    ['3', 'Act', 'Only A1 may move a signal.'],
  ];
  steps.forEach((st, i) => {
    const x = 0.7 + i * 4.15;
    s.addShape(pptx.ShapeType.roundRect, {
      x, y: 2.4, w: 3.9, h: 3.2,
      fill: { color: C.card }, line: { color: '1E3A4C' }, rectRadius: 0.12,
    });
    s.addText(st[0], {
      x, y: 2.65, w: 3.9, h: 0.7,
      fontFace: 'Calibri', fontSize: 28, bold: true, color: C.teal, align: 'center', margin: 0,
    });
    s.addText(st[1], {
      x: x + 0.2, y: 3.4, w: 3.5, h: 0.6,
      fontFace: 'Calibri', fontSize: 26, bold: true, color: C.white, align: 'center', margin: 0,
    });
    s.addText(st[2], {
      x: x + 0.3, y: 4.2, w: 3.3, h: 0.9,
      fontFace: 'Calibri', fontSize: 16, color: C.mute, align: 'center', margin: 0,
    });
  });
  notes(s, 'Empty board: A1 still runs. Killing Synapse cannot change the action sequence. Join keys: run_id, scenario_hash, event_id, message_id.');
}

// 7 Design Thinking
{
  const s = pptx.addSlide();
  s.background = { color: C.navy };
  label(s, 'METHOD', 0.7, 0.7);
  heading(s, 'We started with people. Not with an LLM.', 0.7, 1.15, 12, 0.7, 32);
  const stages = [
    ['1 Empathize', '8 personas + journeys', 'Done'],
    ['2 Define', 'Problem is not mean delay', 'Done'],
    ['3 Ideate', 'Cut the unsafe ideas', 'Done'],
    ['4 Prototype', 'SUMO, one writer', 'Now'],
    ['5 Test', 'Baseline + faults', 'Now'],
  ];
  stages.forEach((st, i) => {
    const x = 0.5 + i * 2.55;
    s.addShape(pptx.ShapeType.roundRect, {
      x, y: 2.3, w: 2.4, h: 3.4,
      fill: { color: i < 3 ? C.card : '184D4A' },
      line: { color: i < 3 ? '1E3A4C' : C.teal },
      rectRadius: 0.1,
    });
    s.addText(st[0], {
      x: x + 0.12, y: 2.55, w: 2.16, h: 0.9,
      fontFace: 'Calibri', fontSize: 18, bold: true, color: C.white, align: 'center', margin: 0,
    });
    s.addText(st[1], {
      x: x + 0.12, y: 3.55, w: 2.16, h: 1.0,
      fontFace: 'Calibri', fontSize: 15, color: C.mute, align: 'center', margin: 0,
    });
    s.addText(st[2], {
      x: x + 0.12, y: 4.8, w: 2.16, h: 0.5,
      fontFace: 'Calibri', fontSize: 16, bold: true, color: C.teal, align: 'center', margin: 0,
    });
  });
  notes(s, 'Framework: Interaction Design Foundation. Prototype/Test are not finished as a course claim. [C02]');
}

// 8 Honesty
{
  const s = pptx.addSlide();
  s.background = { color: C.navy };
  label(s, 'CLAIM FLAGS', 0.7, 0.7);
  heading(s, 'Three things we will not say.', 0.7, 1.15, 12, 0.7, 34);
  const flags = [
    ['No lives saved', 'Ambulance seconds in SUMO are not casualties.'],
    ['No measured air', 'HBEFA is an emission proxy, not the air on Maria’s street.'],
    ['No best episode', 'We keep unfinished trips, faults, and nulls. [C11]'],
  ];
  flags.forEach((f, i) => {
    const y = 2.2 + i * 1.35;
    s.addShape(pptx.ShapeType.roundRect, {
      x: 0.7, y, w: 11.9, h: 1.2,
      fill: { color: C.card }, line: { color: C.red }, rectRadius: 0.08,
    });
    s.addText(f[0], {
      x: 1.0, y: y + 0.15, w: 11.3, h: 0.4,
      fontFace: 'Calibri', fontSize: 22, bold: true, color: C.white, margin: 0,
    });
    s.addText(f[1], {
      x: 1.0, y: y + 0.6, w: 11.3, h: 0.4,
      fontFace: 'Calibri', fontSize: 16, color: C.mute, margin: 0,
    });
  });
  notes(s, 'If asked about ALS literature: one Taipei cohort associated each extra ALS minute with 7% lower adjusted odds of survival to discharge. That motivates Marcus. It is not our result. [C06]');
}

// 9 Course
{
  const s = pptx.addSlide();
  s.background = { color: C.navy };
  label(s, 'COURSE  ·  [C01]', 0.7, 0.7);
  heading(s, 'Evidence beats complexity.', 0.7, 1.15, 12, 0.7, 36);
  const outs = [
    ['01', 'A working prototype'],
    ['02', 'Different conditions'],
    ['03', 'A real baseline'],
    ['04', 'Strengths and limits'],
  ];
  outs.forEach((o, i) => {
    const x = 0.7 + (i % 2) * 6.2;
    const y = 2.2 + Math.floor(i / 2) * 2.1;
    s.addShape(pptx.ShapeType.roundRect, {
      x, y, w: 5.9, h: 1.9,
      fill: { color: C.card }, line: { color: '1E3A4C' }, rectRadius: 0.1,
    });
    s.addText(o[0], {
      x: x + 0.3, y: y + 0.3, w: 5.3, h: 0.45,
      fontFace: 'Calibri', fontSize: 16, bold: true, color: C.teal, margin: 0,
    });
    s.addText(o[1], {
      x: x + 0.3, y: y + 0.85, w: 5.3, h: 0.6,
      fontFace: 'Calibri', fontSize: 26, bold: true, color: C.white, margin: 0,
    });
  });
  notes(s, 'The brief asks for prototype, conditions, baseline comparison, and data-driven strengths and limitations. Innovation matters; evidence matters more. [C01] Baselines: fixed-time and actuated on matched seeds.');
}

// 10 Status
{
  const s = pptx.addSlide();
  s.background = { color: C.navy };
  label(s, 'NOW  ·  [C17]', 0.7, 0.7);
  heading(s, 'What is proven. What is not.', 0.7, 1.15, 12, 0.7, 34);
  const rows = [
    ['Verified', 'Rows 07 and 08. Emergency, multimodal, recovery.', C.teal],
    ['Gated', 'Rows 02–09 on TraCI. Tests and files, not chat.', C.amber],
    ['Blocked', 'Row 01 libsumo. Windows blocked the DLL.', C.red],
    ['Not verified', 'Row 09 evaluation headline. Do not claim it.', C.mute],
  ];
  rows.forEach((r, i) => {
    const y = 2.15 + i * 1.1;
    s.addShape(pptx.ShapeType.roundRect, {
      x: 0.7, y, w: 11.9, h: 0.98,
      fill: { color: C.card }, line: { color: '1E3A4C' }, rectRadius: 0.08,
    });
    s.addText(r[0], {
      x: 1.0, y: y + 0.26, w: 2.6, h: 0.46,
      fontFace: 'Calibri', fontSize: 20, bold: true, color: r[2], margin: 0,
    });
    s.addText(r[1], {
      x: 3.8, y: y + 0.26, w: 8.4, h: 0.46,
      fontFace: 'Calibri', fontSize: 20, color: C.white, margin: 0,
    });
  });
  notes(s, 'Rows 07 and 08 are verified deterministic slices. Row 09 is gated and not verified in this session. Row 01 remains blocked by Windows Code Integrity on libsumo. [C17] Tunis road demand, if shown later, is synthetic or calibrated. [C15]');
}

// 11 Close
{
  const s = pptx.addSlide();
  s.background = { color: C.navy };
  faces.forEach((f, i) => {
    s.addImage({
      path: PHOTO(f.file),
      x: i * (W / 8), y: 0, w: W / 8, h: H,
      sizing: { type: 'cover', w: W / 8, h: H },
    });
  });
  s.addShape(pptx.ShapeType.rect, {
    x: 0, y: 0, w: W, h: H,
    fill: { color: C.navy, transparency: 38 },
    line: { color: C.navy },
  });
  heading(s, 'People. Evidence. One writer.', 0.7, 2.4, 12, 1.0, 40);
  body(s, 'Questions?', 0.7, 3.6, 12, 0.5, 28, C.teal);
  body(s, '32-row mixed-source evidence register  ·  cooperative Max-Pressure  ·  Synapse never actuates', 0.7, 6.5, 12, 0.4, 14, C.mute);
  notes(s, 'Close. Invite questions. If asked for sources, open the long deck or presentation-claim-ledger.json. Only A1 writes signals. [C16]');
}

const output = path.join(__dirname, 'CoFlow-5-Synapse-TALK.pptx');

pptx.writeFile({ fileName: output }).then(async () => {
  await addFadeTransitions(output);
  console.log(`SUCCESS ${output} slides=11 fade=on`);
}).catch((error) => {
  console.error(error);
  process.exit(1);
});

async function addFadeTransitions(file) {
  const JSZip = require('jszip');
  const data = fs.readFileSync(file);
  const zip = await JSZip.loadAsync(data);
  const names = Object.keys(zip.files).filter((name) => /^ppt\/slides\/slide\d+\.xml$/.test(name));
  const fade = '<p:transition spd="slow" advTm="0"><p:fade/></p:transition>';
  for (const name of names) {
    let xml = await zip.file(name).async('string');
    if (xml.includes('<p:transition')) continue;
    if (xml.includes('</p:cSld>')) {
      xml = xml.replace('</p:cSld>', `</p:cSld>${fade}`);
    }
    zip.file(name, xml);
  }
  const out = await zip.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' });
  fs.writeFileSync(file, out);
}
