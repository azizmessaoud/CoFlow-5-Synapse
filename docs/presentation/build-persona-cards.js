'use strict';

const path = require('path');
const pptxgen = require('pptxgenjs');
const pptx = new pptxgen();
pptx.defineLayout({ name: 'CARDS', width: 13.333, height: 7.5 });
pptx.layout = 'CARDS';
pptx.author = 'CoFlow-5 Synapse · ESPRIT 4DS';
pptx.title = 'CoFlow-5 — Persona Cards';
pptx.subject = 'Eight research-informed Design Thinking persona cards';
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
  },
  {
    name:'David', file:'p2-david.png', age:'41', role:'Delivery-van driver', situation:'More than 60 time-sensitive stops per workday',
    statement:'I can plan around a longer trip if I know how long it will actually take.',
    personality:'Organised and schedule-focused; design assumption.', bio:'Represents reliability and the severe tail—not only the average.',
    need:'Predictable journeys, fewer stops and visible incidents.', fear:'A better mean hides unfinished or extreme trips.',
    uses:'Work phone, GPS/navigation and delivery-round tools.', rejects:'Best-case headlines and deleted unfinished trips.',
    evidence:'DfT TAG uses 0.4 as an appraisal reliability ratio for journey-time variability [C05].',
    measure:'Completed/unfinished trips, P95/max duration, stops and standstill.', color:C.blue,
  },
  {
    name:'Chidi', file:'p3-chidi.png', age:'27', role:'Frequent bus passenger', situation:'Uses a high-frequency corridor where regularity is the service',
    statement:'Buses should arrive regularly—not three at once after a long wait.',
    personality:'Routine-oriented and uncertainty-sensitive; design assumption.', bio:'Represents passengers harmed by bunching and unpredictable gaps.',
    need:'Priority only for a late bus or a large headway gap.', fear:'Three buses arrive together after one long gap.',
    uses:'Passenger-information app when available; otherwise the stop.', rejects:'Every-bus priority and pedestrian clearance sacrificed for transit.',
    evidence:'DfT TAG applies a 2× value-of-time multiplier to public-transport waiting [C05].',
    measure:'Lateness, headway variation, passenger-wait proxy and car externality.', color:C.blue,
  },
  {
    name:'Rosa', file:'p4-rosa.png', age:'52', role:'Bus depot controller', situation:'Supervises service disruption and priority decisions',
    statement:'Show me why priority was granted or denied, and let me respond safely.',
    personality:'Calm, responsible and evidence-seeking; design assumption.', bio:'Represents operators who must defend automated priority decisions.',
    need:'Positions, headways, confidence, reason codes and a joined audit trail.', fear:'A black box refuses priority and leaves no history.',
    uses:'Depot tools, vehicle-location screen, radio and dashboard.', rejects:'Unsupported predictions or override outside the safety mask.',
    evidence:'SCATS documentation describes monitoring, manual intervention and audit trails [C08].',
    measure:'Reason-code coverage and operator explanation of one yes and one no.', color:C.amber,
  },
  {
    name:'Marcus', file:'p5-marcus.png', age:'34', role:'Urban ambulance crew', situation:'Responds through congested streets during peak periods',
    statement:'Get us through safely, and make sure traffic recovers after we pass.',
    personality:'Urgent, precise and aware of other road users; design assumption.', bio:'Represents passage plus recovery and the civilian cost of priority.',
    need:'Trusted route/ETA request, downstream check and controlled recovery.', fear:'A green into a full link simply moves the queue.',
    uses:'Dispatch tablet, GPS, radio, lights and siren.', rejects:'Cutting an occupied crossing or translating simulation into casualties.',
    evidence:'One Taipei cohort associated each extra ALS minute with 7% lower adjusted odds [C06]. Preemption can impose network delay [C07].',
    measure:'Emergency effect, civilian delay, downstream rejection and recovery.', color:C.red,
  },
  {
    name:'Yuki', file:'p6-yuki.png', age:'47', role:'Traffic engineer / operations', situation:'Accountable for safe automated network performance',
    statement:'Automation should support my decisions—not leave me responsible for a system I cannot control.',
    personality:'Careful, process-driven and accountable; design assumption.', bio:'Represents diagnosis, safe override and predictable fallback.',
    need:'Mode, health, freshness, constraints, safe override and recovery.', fear:'Stale data looks healthy while control degrades.',
    uses:'Signal supervisor, logs, sensor health and GIS tools.', rejects:'Silent degradation, LLM actuation or unsafe manual commands.',
    evidence:'Operational documentation motivates intervention and audit [C08]; CoFlow-5 fixes the exact authority and ladder [C16].',
    measure:'Legal actions, transition reasons, health evidence and fallback order.', color:C.teal,
  },
  {
    name:'Maria', file:'p7-maria.png', age:'38', role:'Parent living near an arterial', situation:'Walks her child along a school-adjacent street',
    statement:'Cleaner traffic on the main road must not mean more exhaust outside our homes.',
    personality:'Protective, local and sceptical of averages; design assumption.', bio:'Represents residents who can bear hidden local displacement.',
    need:'Link-level maps, school-sensitive checks and explicit displacement limits.', fear:'The main road improves by moving queues to her street.',
    uses:'No specialist tool; she needs understandable maps and labels.', rejects:'Calling HBEFA air quality or claiming a Tunis deployment.',
    evidence:'In 2005–2006, 6.4M students (12.5% of the studied US population) attended schools within 250 m of a major road [C09].',
    measure:'Per-link stops and emission proxies near selected receptors.', color:C.green,
  },
  {
    name:'Omar', file:'p8-omar.png', age:'55', role:'Network duty officer', situation:'Monitors incidents and coordinates operational response',
    statement:'Tell me what is wrong, why you think so, and whether I can still trust the data.',
    personality:'Sceptical, methodical and operational; design assumption.', bio:'Represents the difference between “nothing detected” and “cannot see.”',
    need:'Severity, observations, uncertainty, freshness and data-health warnings.', fear:'False alarms or a frozen screen hide the real condition.',
    uses:'Radio, camera wall, incident tools and dashboard.', rejects:'Alerts without evidence or anomaly presented as proven cause.',
    evidence:'FHWA estimates incidents account for about 25–30% of congestion in many US metropolitan contexts—not Tunis [C10].',
    measure:'Detection delay, false alarms, misses, stale data and recovery.', color:C.navy2,
  },
];

function text(s,v,x,y,w,h,size=15,color=C.white,extra={}){s.addText(v,{x,y,w,h,fontFace:'Aptos',fontSize:size,color,margin:0,fit:'shrink',valign:'mid',...extra});}
function box(s,x,y,w,h,fill=C.card,line=C.line){s.addShape(pptx.ShapeType.roundRect,{x,y,w,h,rectRadius:0.08,fill:{color:fill},line:{color:line,width:0.8}});}
function field(s,title,value,x,y,w,h,color=C.teal){box(s,x,y,w,h,C.card,color);text(s,title,x+0.18,y+0.1,w-0.36,0.23,10,color,{bold:true,charSpacing:1});text(s,value,x+0.18,y+0.38,w-0.36,h-0.5,13,C.white,{valign:'top'});}

people.forEach((p,i)=>{
  const s=pptx.addSlide();s.background={color:C.navy};
  s.addImage({path:PHOTO(p.file),x:0,y:0,w:4.55,h:H,sizing:{type:'cover',w:4.55,h:H}});
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
  s.addNotes(`Research-informed design persona, not an interview. ${p.statement} Need: ${p.need} Fear: ${p.fear} Evidence: ${p.evidence} Proposed measure: ${p.measure}`);
});

if(people.length!==8)throw new Error('Expected 8 personas');
const output=path.join(__dirname,'CoFlow-5-Persona-Cards.pptx');
pptx.writeFile({fileName:output}).then(()=>console.log(`SUCCESS ${output} slides=8`)).catch((e)=>{console.error(e);process.exit(1);});
