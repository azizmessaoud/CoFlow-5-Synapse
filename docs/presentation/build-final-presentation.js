'use strict';

// CoFlow-5 — Final professor presentation (10-stage arc, six personas)
// Build:  npm install pptxgenjs   →   node build-final-presentation.js
// Needs:  ./personas/p1-amara.png p2-david.png p3-chidi.png p4-rosa.png p5-marcus.png p8-omar.png
// (missing images become labelled placeholder cards — the build does not crash)

const path = require('path');
const fs = require('fs');
const pptxgen = require('pptxgenjs');
const pptx = new pptxgen();
pptx.defineLayout({ name: 'CARDS', width: 13.333, height: 7.5 });
pptx.layout = 'CARDS';
pptx.author = 'CoFlow-5 Synapse · ESPRIT 4DS';
pptx.title = 'CoFlow-5 — Empathize and Ideation validation';
pptx.subject = 'User research, evidence, personas, needs, problem statement, ideas, and the selected solution';
pptx.lang = 'en-US';
pptx.theme = { headFontFace: 'Aptos Display', bodyFontFace: 'Aptos', lang: 'en-US' };

const C = { navy:'081B2B', navy2:'102C3E', card:'123246', white:'FFFFFF', mute:'9CB3BF', teal:'35C8BC', amber:'F2A44C', red:'E56E72', green:'54C38A', blue:'45B8D1', purple:'A892E8', line:'285064' };
const W=13.333, H=7.5;
const PHOTO=(f)=>path.join(__dirname,'personas',f);
const people=[
  {
    name:'Amara', file:'p1-amara.png', age:'74', role:'Retired pedestrian; uses a cane', situation:'Crosses a busy central street for shops and transit',
    statement:'I need enough time to finish crossing, even when traffic is busy.',
    personality:'Careful and independent; design assumption.', bio:'Represents slower walkers excluded by average-speed timing.',
    need:'Acknowledgement, shorter waiting and enough clearance to finish.', fear:'Cars receive green while she is still crossing.',
    uses:'Push-button, audible/visual feedback; no phone required.', rejects:'Shortened clearance, inaccessible apps, invented success claims.',
    evidence:'Perceived wait ≈2× in one NZ study [C03]. MUTCD clearance guidance ≈1.07 m/s and slower where needed [C04].',
    measure:'Mean / P95 / max wait + zero clearance truncations.', color:C.purple,
    affected:'Amara, while she is still in the crossing',
    problem:'Clearance assumes a faster walk than hers.',
    idea:'Hold the conflicting green until she finishes, and count truncations.',
    solution:'A3 asks. A1 holds the conflicting green. Truncations are counted.',
    prevention:'Conflicting traffic stays red while the crossing is occupied. The fixture counted zero truncations. That is not crashes prevented.',
  },
  {
    name:'David', file:'p2-david.png', age:'41', role:'Delivery-van driver', situation:'More than 60 time-sensitive stops per workday',
    statement:'I can plan around a longer trip if I know how long it will actually take.',
    personality:'Organised and schedule-focused; design assumption.', bio:'Represents reliability and the severe tail—not only the average.',
    need:'Predictable journeys, fewer stops and visible incidents.', fear:'A better mean hides unfinished or extreme trips.',
    uses:'Work phone, GPS/navigation and delivery-round tools.', rejects:'Best-case headlines and deleted unfinished trips.',
    evidence:'DfT TAG uses 0.4 as an appraisal reliability ratio for journey-time variability [C05].',
    measure:'Completed/unfinished trips, P95/max duration, stops and standstill.', color:C.blue,
    affected:'David, on the trip that does not finish',
    problem:'A better average hides the late or unfinished trip.',
    idea:'Show unfinished trips and the tail beside the mean.',
    solution:'The evidence page keeps unfinished trips in the count, next to the mean.',
    prevention:'A jammed scenario cannot look safe just because the average improved.',
  },
  {
    name:'Chidi', file:'p3-chidi.png', age:'27', role:'Frequent bus passenger', situation:'Uses a high-frequency corridor where regularity is the service',
    statement:'Buses should arrive regularly—not three at once after a long wait.',
    personality:'Routine-oriented and uncertainty-sensitive; design assumption.', bio:'Represents passengers harmed by bunching and unpredictable gaps.',
    need:'Priority only for a late bus or a large headway gap.', fear:'Three buses arrive together after one long gap.',
    uses:'Passenger-information app when available; otherwise the stop.', rejects:'Every-bus priority and pedestrian clearance sacrificed for transit.',
    evidence:'DfT TAG applies a 2× value-of-time multiplier to public-transport waiting [C05].',
    measure:'Lateness, headway variation, passenger-wait proxy and car externality.', color:C.blue,
    affected:'Chidi, waiting through a long gap between buses',
    problem:'Buses bunch, then the early bus is treated as urgent.',
    idea:'Ask for green only after an unusual gap. An early bus gets nothing.',
    solution:'A3 asks only for a late bus or a large gap. Pedestrian clearance stays ahead of the bus.',
    prevention:'An early bus does not steal the crossing from the person still in it.',
  },
  {
    name:'Rosa', file:'p4-rosa.png', age:'52', role:'Incident-report reader', situation:'Reads disruption and the crash record. She does not change the light',
    statement:'Show me why priority was granted or denied, and let me respond safely.',
    personality:'Calm, responsible and evidence-seeking; design assumption.', bio:'She reads the record and the reason code. She does not write the signal.',
    need:'Positions, headways, confidence, reason codes and a joined audit trail.', fear:'A black box refuses priority and leaves no history.',
    uses:'Depot tools, vehicle-location screen, radio and dashboard.', rejects:'Unsupported predictions or override outside the safety mask.',
    evidence:'SCATS documentation describes monitoring, manual intervention and audit trails [C08].',
    measure:'Reason-code coverage and operator explanation of one yes and one no.', color:C.amber,
    affected:'Rosa, reading a refusal that has no reason',
    problem:'A refusal with no reason cannot be checked after the shift.',
    idea:'Explain one grant or denial with the reason code and a citation, or abstain.',
    solution:'S2 returns one cited explanation, or an abstention. Rosa does not write the signal.',
    prevention:'The reason is kept, so a bad pattern can be found after the shift.',
  },
  {
    name:'Marcus', file:'p5-marcus.png', age:'34', role:'Urban ambulance crew', situation:'Responds through congested streets during peak periods',
    statement:'Get us through safely, and make sure traffic recovers after we pass.',
    personality:'Urgent, precise and aware of other road users; design assumption.', bio:'Represents passage plus recovery and the civilian cost of priority.',
    need:'Trusted route/ETA request, downstream check and controlled recovery.', fear:'A green into a full link simply moves the queue.',
    uses:'Dispatch tablet, GPS, radio, lights and siren.', rejects:'Cutting an occupied crossing or translating simulation into casualties.',
    evidence:'One Taipei cohort associated each extra ALS minute with 7% lower adjusted odds [C06]. Preemption can impose network delay [C07].',
    measure:'Emergency time, civilian delay, downstream rejection and recovery. Not lives saved.', color:C.red,
    affected:'Marcus, and the people his priority delays',
    problem:'A green light into a full exit only moves the queue.',
    idea:'Authenticated request, an exit check, then recovery.',
    solution:'A2 sends route and expiry. A1 checks the exit, then recovers Max-Pressure, actuated, fixed-time.',
    prevention:'He is not sent into a blocked exit, and Amara’s crossing is not cut. Civilian delay is logged. Not lives saved.',
  },
  {
    name:'Omar', file:'p8-omar.png', age:'55', role:'Network duty officer', situation:'Monitors incidents and coordinates operational response',
    statement:'Tell me what is wrong, why you think so, and whether I can still trust the data.',
    personality:'Sceptical, methodical and operational; design assumption.', bio:'Represents the difference between “nothing detected” and “cannot see.”',
    need:'Severity, observations, uncertainty, freshness and data-health warnings.', fear:'False alarms or a frozen screen hide the real condition.',
    uses:'Radio, camera wall, incident tools and dashboard.', rejects:'Alerts without evidence or anomaly presented as proven cause.',
    evidence:'FHWA estimates incidents account for about 25–30% of congestion in many US metropolitan contexts—not Tunis [C10].',
    measure:'Detection delay, false alarms, misses, stale data and recovery.', color:C.navy2,
    affected:'Omar, when a queue might be a crash, demand, or a dead sensor',
    problem:'A residual can be a crash, extra demand, or a sensor that has gone quiet.',
    idea:'Publish the class, the residual, and whether the sample is fresh.',
    solution:'A4 publishes the class and the freshness. It does not name the cause. Stale data leaves A1 on local control.',
    prevention:'A stale sensor is not called a healthy road, so a false all-clear is not the alert.',
  },
];

function text(s,v,x,y,w,h,size=15,color=C.white,extra={}){s.addText(v,{x,y,w,h,fontFace:'Aptos',fontSize:size,color,margin:0,fit:'shrink',valign:'mid',...extra});}
function box(s,x,y,w,h,fill=C.card,line=C.line){s.addShape(pptx.ShapeType.roundRect,{x,y,w,h,rectRadius:0.08,fill:{color:fill},line:{color:line,width:0.8}});}
function field(s,title,value,x,y,w,h,color=C.teal){box(s,x,y,w,h,C.card,color);text(s,title,x+0.18,y+0.1,w-0.36,0.23,10,color,{bold:true,charSpacing:1});text(s,value,x+0.18,y+0.38,w-0.36,h-0.5,13,C.white,{valign:'top'});}
function photo(s,file,x,y,w,h){
  const p=PHOTO(file);
  if(fs.existsSync(p)){s.addImage({path:p,x,y,w,h,sizing:{type:'cover',w,h}});}
  else{ // placeholder so the deck still builds before the persona portraits exist
    s.addShape(pptx.ShapeType.rect,{x,y,w,h,fill:{color:C.navy2},line:{color:C.line}});
    text(s,file.replace('.png','').toUpperCase(),x,y+h/2-0.2,w,0.5,16,C.mute,{align:'center'});
  }
}
function stage(kicker,title,note){
  const s=pptx.addSlide();s.background={color:C.navy};
  text(s,kicker,0.45,0.32,12.4,0.28,13,C.teal,{bold:true,charSpacing:1.1});
  text(s,title,0.45,0.68,12.4,0.85,28,C.white,{bold:true,fontFace:'Aptos Display',valign:'top'});
  s.addNotes(note);
  return s;
}
function darkTable(s,rows,y,colW,h){
  const shaped=rows.map((row,ri)=>row.map((cell)=>({
    text:String(cell),
    options:{fill:{color:ri===0?C.navy2:C.card},color:ri===0?C.teal:C.white,bold:ri===0,align:'left',valign:'middle',fontFace:'Aptos',fontSize:ri===0?11:12,margin:[5,6,5,6]},
  })));
  s.addTable(shaped,{x:0.4,y,w:12.5,h,colW,border:[{pt:0.4,color:C.line},{pt:0.4,color:C.line},{pt:0.4,color:C.line},{pt:0.4,color:C.line}],valign:'middle'});
}

// — Validation title. The chain the professor asked to see. —
{
  const s=stage('Empathize and Ideation · validation','Research, then evidence, then the person, then the idea.','Fedi Baccar asked for a visible link: user research, evidence, personas, needs, problem statement, ideas, selected solution. Interviews and questionnaires were not collected.');
  const chain=['1 Research','2 Evidence','3 Personas','4 Needs','5 Problem','6 Ideas','7 Selected solution'];
  chain.forEach((label,i)=>{
    box(s,0.45,1.75+i*0.72,12.4,0.62,C.card,C.teal);
    text(s,label,0.7,1.75+i*0.72,11.9,0.62,18,C.white,{bold:true});
  });
}

// — Empathize: problem context —
{
  const s=stage('Empathize · Problem context','A signal decision hits several people at once.','Why it matters: published Tunisian crash counts, and no public adaptive-signal network was found. This is not a claim that the project prevents deaths.');
  darkTable(s,[
    ['What is happening','Why it matters here'],
    ['A light changes while someone is still crossing.','Pedestrians were 28% of 2023 deaths in the WHO investment case that quotes ONSR. The 2024 strategy names older people and people with disabilities.'],
    ['A better average can hide a trip that never finishes.','Vehicle occupants carry most of the health cost in that same case.'],
    ['Buses bunch, then an early bus is treated as urgent.','TRANSTU reported 187.4 million paying passengers in 2018. That is not this year’s headway.'],
    ['A refusal, a full exit, or a stale sensor can look like nothing.','The reader, the crew, and the duty officer each need a record they can check.'],
  ],1.7,[4.4,8.1],4.6);
  text(s,'2023 deaths are published as both 2,273 and 1,216, with the same 5,796 crashes. Show both. Do not average them.',0.45,6.55,12.4,0.4,13,C.amber);
}

// — Empathize: target users —
{
  const s=stage('Empathize · Target users','Six groups named by published sources.','These are the people affected. Ages and jobs on the cards are design readings, not interviews.');
  darkTable(s,[
    ['Who is affected','What the source names','Persona'],
    ['Pedestrians, and older people and people with disabilities','28% of 2023 deaths in the investment case. Named in the 2024 strategy.','Amara'],
    ['Occupants of motor vehicles','Most of the health cost in that case.','David'],
    ['TRANSTU passengers in Greater Tunis','187.4 million paying passengers in 2018.','Chidi'],
    ['The reader of the crash record','ONSR compiles the national record. One reader, not a second controller.','Rosa'],
    ['Road emergency crews','Civil Protection answers those calls. We did not ride with them.','Marcus'],
    ['The person who must trust the alert','A residual is not a cause.','Omar'],
  ],1.7,[4.3,5.6,2.6],5.3);
}

// — Empathize: user research / evidence —
{
  const s=stage('Empathize · User research','What was collected, and what was not.','Interviews, questionnaires, and ride-alongs are not in the repository. Existing data and literature are. Inventing a sample would break the validation.');
  darkTable(s,[
    ['Method','Status','What it supports'],
    ['Interviews','Not collected','Nothing. No quote.'],
    ['Questionnaires','Not collected','Nothing. No percentage from us.'],
    ['Observation / ride-along','Not done','Nothing about a Tunis crew or a specific crossing.'],
    ['Existing data','Used','WHO profile, WHO/UNIATF investment case quoting ONSR, La Presse briefing 17 Jan 2025, INS republished counts, TRANSTU 2018 report.'],
    ['Literature','Used','Clearance guidance, appraisal guidance on wait and reliability, an audit-trail product analogy, a Taipei minute figure labelled as not Tunis.'],
    ['Our simulation','One matched seed','71, 84, and 70 of 84 trips. Mixed. No winner. Not a Tunis result.'],
  ],1.7,[2.4,2.3,7.8],5.3);
}

// — Empathize: key findings —
{
  const s=stage('Empathize · Key findings','Five insights. Each one limits what we may say.','The findings come from the sources on the previous slide. They are not interview themes.');
  const lines=[
    'The people harmed are named in official counts: pedestrians, occupants, and public-transport passengers. The 2024 strategy also names older people and people with disabilities.',
    'Two death totals exist for 2023, 2,273 and 1,216, beside the same 5,796 crashes. A single death number would hide that.',
    'A mean can improve while trips stay unfinished. On seed 37, actuated finished more trips. Max-Pressure did not win.',
    'No public adaptive-signal network in Tunis was found. A 2018 passenger total is not today’s bus gap.',
    'An alert that names a cause, or a stale sensor shown as healthy, would go beyond the evidence.',
  ];
  lines.forEach((line,i)=>{
    box(s,0.45,1.7+i*1.05,12.4,0.92,C.card,C.line);
    text(s,`${i+1}   ${line}`,0.65,1.7+i*1.05,12.0,0.92,14,C.white);
  });
}

// — Empathize: personas justified —
{
  const s=stage('Empathize · Personas','Each card is a reading of one group in the evidence.','Not interviewed people. The next six slides are the cards. The research column is why that card exists.');
  darkTable(s,[
    ['Persona','User type','Justified by'],
    ['Amara, 74','Slower pedestrian','Pedestrian share of deaths, plus the 2024 strategy, plus slower-clearance guidance.'],
    ['David, 41','Driver who needs the tail','Occupant health cost, plus one seed where unfinished trips stayed visible.'],
    ['Chidi, 27','Bus passenger','TRANSTU 2018 total, plus guidance that values waiting time.'],
    ['Rosa, 52','Reader of the record','ONSR compiles crashes. An audit trail is a product analogy, not a room we visited.'],
    ['Marcus, 34','Ambulance crew','Civil Protection exists. A foreign survival figure is cited as foreign. Not lives saved.'],
    ['Omar, 55','Duty officer','A class is not a cause. Stale data must not look healthy.'],
  ],1.7,[2.2,2.8,7.5],5.3);
}

people.forEach((p,i)=>{
  const s=pptx.addSlide();s.background={color:C.navy};
  photo(s,p.file,0,0,4.55,H);
  s.addShape(pptx.ShapeType.rect,{x:0,y:5.35,w:4.55,h:2.15,fill:{color:C.navy,transparency:5},line:{color:C.navy}});
  text(s,`P${i+1} · AGE ${p.age}`,0.35,5.55,3.9,0.3,12,C.teal,{bold:true,charSpacing:1});
  text(s,p.name,0.35,5.92,3.9,0.52,32,C.white,{bold:true,fontFace:'Aptos Display'});
  text(s,p.role,0.35,6.42,3.9,0.34,14,C.white);
  text(s,'Illustration · not an interviewed person',0.35,6.9,3.9,0.25,10.5,C.mute,{italic:true});
  text(s,`Persona ${i+1} — ${p.name}`,4.88,0.35,8.05,0.5,25,C.white,{bold:true,fontFace:'Aptos Display'});
  text(s,`${p.situation} · Tunis design context (assumption)`,4.9,0.86,7.95,0.3,12,C.mute);
  box(s,4.88,1.3,8.0,1.0,C.navy2,p.color);
  text(s,'DESIGN STATEMENT · SYNTHESIS, NOT A QUOTE',5.1,1.42,7.55,0.2,9.5,p.color,{bold:true,charSpacing:0.8});
  text(s,`“${p.statement}”`,5.1,1.68,7.55,0.48,18,C.white,{bold:true,italic:true});
  field(s,'NEED',p.need,4.88,2.55,3.85,1.15,C.green);
  field(s,'FEAR',p.fear,9.03,2.55,3.85,1.15,C.red);
  field(s,'USES',p.uses,4.88,3.92,3.85,1.15,C.blue);
  field(s,'REJECTS',p.rejects,9.03,3.92,3.85,1.15,C.red);
  field(s,'EVIDENCE',p.evidence,4.88,5.3,5.15,1.25,C.teal);
  field(s,'MEASURE · PROPOSED, NOT A RESULT',p.measure,10.3,5.3,2.58,1.25,C.amber);
  text(s,`BIO · ${p.bio}`,4.9,6.72,7.95,0.3,11.5,C.mute);
  text(s,`PERSONALITY · ${p.personality}`,4.9,7.05,7.95,0.22,10,C.mute);
  s.addNotes(`Research-informed design persona, not an interview. ${p.statement} Need: ${p.need} Fear: ${p.fear} Evidence: ${p.evidence}`);
});

// — Empathize: needs and pain points —
{
  const s=stage('Empathize · Needs and pain points','Need, frustration, and what they expect to see.','Taken from the cards. Not from an interview.');
  darkTable(s,[
    ['Who','Need','Pain','Expectation'],
    ['Amara','Enough time to finish','Cars go green while she is still crossing','The conflicting green stays held'],
    ['David','The real duration, including the bad trip','A better mean hides the unfinished trip','Unfinished trips stay on the page'],
    ['Chidi','A regular gap','Three buses after one long wait','An early bus gets nothing'],
    ['Rosa','A reason she can read later','A refusal with no history','A citation, or an abstention'],
    ['Marcus','A path through, then recovery','Green into a full exit','The exit is checked. Delay to others is logged'],
    ['Omar','A class he can trust','A frozen screen, or a guessed cause','Freshness is shown. Stale stays stale'],
  ],1.7,[1.6,3.3,4.0,3.6],5.3);
}

// — Ideation: problem statement —
{
  const s=stage('Ideation · Problem statement','One light. Six needs. A record that does not invent the result.','Refined from the findings. The problem is not “reduce deaths in Tunisia.” That result is not something this evidence can support.');
  text(s,'How might a simulated signal serve the person still crossing, the unfinished trip, the bus gap, the reader of the refusal, the crew at a full exit, and the officer who must not be told a residual is a cause — while only one component writes the light, and every decision keeps a source?',0.5,1.85,12.3,1.6,20,C.white,{valign:'top'});
  text(s,'Out of scope for the claim: lives saved, measured air, a Tunis deployment, and a winner from one seed.',0.5,3.7,12.3,0.6,16,C.amber);
}

// — Ideation: HMW —
{
  const s=stage('Ideation · How might we','One question per person, taken from their pain.','The questions were written from the needs table. They were not collected in a workshop with users.');
  darkTable(s,[
    ['Who','How might we…'],
    ['Amara','…hold the conflicting green until the crossing finishes, and count every time it is cut?'],
    ['David','…show unfinished trips beside the mean, so a better average cannot hide the tail?'],
    ['Chidi','…give green only after an unusual gap, and give an early bus nothing?'],
    ['Rosa','…explain one grant or one denial with a reason code, or abstain?'],
    ['Marcus','…check the exit before green, then recover, without cutting the crossing?'],
    ['Omar','…publish the class, the confidence, and the freshness, and refuse to name the cause?'],
  ],1.7,[2.0,10.5],5.2);
}

// — Ideation: ideas generated —
{
  const s=stage('Ideation · Ideas generated','What we kept, and what we refused.','The refuse column is part of the evidence. A refused idea does not become the solution.');
  darkTable(s,[
    ['Who','Idea we kept','Idea we refused'],
    ['Amara','Hold the green. Count truncations.','A camera that guesses her ability.'],
    ['David','Keep unfinished trips in the count.','A scraped live map treated as his trip.'],
    ['Chidi','Priority only after a real gap.','Green for every bus.'],
    ['Rosa','One cited explanation, or abstain.','A chatbot that negotiates the phase.'],
    ['Marcus','Request, exit check, then recovery.','An always-green corridor, or “lives saved.”'],
    ['Omar','Class, confidence, freshness.','A news scrape that declares a crash.'],
  ],1.7,[1.7,5.2,5.6],5.2);
}

// — Ideation evidence and selection criteria —
{
  const s=stage('Ideation · How we chose','The method, then the criteria.','Method: one idea per persona need, written beside the source, then kept or refused. Not SCAMPER, and not a user workshop.');
  darkTable(s,[
    ['Criterion','A kept idea must…'],
    ['Names the person','Say who is affected. A solution with no person is dropped.'],
    ['Has a source','Point at published data, literature, or a labelled simulation row.'],
    ['Does not invent','No interview quote, no survey percentage, no Tunis digit we do not have.'],
    ['Does not write the light','Specialists may request. Only A1, through the safety mask, sets the phase.'],
    ['Leaves a record','Rosa can read a grant, a denial, or an abstention.'],
  ],1.7,[3.0,9.5],5.0);
}

// — Selected solution —
{
  const s=stage('Ideation · Selected solution','Advisers request. One writer decides. The record stays.','This is the concept we intend to develop. It addresses each need on the card. It does not prevent accidents in Tunisia.');
  darkTable(s,[
    ['Need','What the selected concept does'],
    ['Amara finishes the crossing','A3 asks. A1 holds the conflicting green. Truncations are counted.'],
    ['David sees the bad trip','Unfinished trips stay beside the mean.'],
    ['Chidi gets a gap, not a bunch','A3 asks only for a late bus or a large gap.'],
    ['Rosa can check the no','One cited reason, or an abstention. She does not write the signal.'],
    ['Marcus is not sent into a full exit','A2 asks. A1 checks the exit, then recovers. Civilian delay is logged.'],
    ['Omar is not told a guessed cause','A4 publishes class, confidence, and freshness. Stale stays stale.'],
  ],1.7,[4.2,8.3],4.7);
  text(s,'Incident packs change the street inside SUMO. The language model explains the log, or abstains. It never writes the light.',0.45,6.6,12.4,0.4,14,C.mute);
}

{
  const s=stage('The link','User research, then evidence, then personas, then needs, then the problem, then the ideas, then the selected solution.','Every step above is on a slide. The empty methods stay empty so the link is checkable.');
  text(s,'No lives saved. No measured air. No Tunis deployment. No winner.',0.5,2.2,12.3,0.5,20,C.amber,{bold:true});
}

if(people.length!==6)throw new Error('Expected 6 personas');
const output=path.join(__dirname,'CoFlow-5-Empathize-Ideation-Validation.pptx');
pptx.writeFile({fileName:output}).then(()=>console.log(`SUCCESS ${output}`)).catch((e)=>{console.error(e);process.exit(1);});
