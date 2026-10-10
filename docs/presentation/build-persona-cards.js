'use strict';

const path = require('path');
const pptxgen = require('pptxgenjs');
const pptx = new pptxgen();
pptx.defineLayout({ name: 'CARDS', width: 13.333, height: 7.5 });
pptx.layout = 'CARDS';
pptx.author = 'CoFlow-5 Synapse · ESPRIT 4DS';
pptx.title = 'CoFlow-5 — Persona Cards';
pptx.subject = 'Six personas through empathize, needs, evidence, ideation, solutions, and prevention';
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

{
  const s=stage('Same story as ideate-final-personas.html','The solution names the person it affects.','Ten stages. Six research-informed personas. Survey and interviews are empty because those files are not in the repository.');
  const stages=['1  Empathize','2  Personas','3  Persona needs','4  Evidence','5  Ideation','6  Solutions','7  Online data collection','8  Data analysis','9  Heatmap','10  Accident prevention'];
  stages.forEach((label,i)=>{
    const col=i<5?0:1;
    const row=i%5;
    box(s,0.5+col*6.3,1.85+row*0.95,5.9,0.78,C.card,C.teal);
    text(s,label,0.72+col*6.3,1.85+row*0.95,5.5,0.78,18,C.white,{bold:true});
  });
}

{
  const s=stage('1 · Empathize','Who is on the road, from published counts.','These are groups named by official sources. They are not interviews. 2023 deaths are published as both 2,273 and 1,216, with the same 5,796 crashes. Show both.');
  darkTable(s,[
    ['Group named in the sources','Who carries that need'],
    ['Pedestrians. Older people and people with disabilities, named in the 2024 strategy. Pedestrians were 28% of the 2023 deaths in the WHO case that quotes ONSR.','Amara'],
    ['Occupants of motor vehicles. They carry most of the health cost in that same case.','David'],
    ['TRANSTU passengers in Greater Tunis. 187.4 million paying trips in 2018, not this year.','Chidi'],
    ['The operator and the crash record. One reader. Not a second controller.','Rosa'],
    ['Civil Protection, which answers road emergencies. We did not ride with a crew.','Marcus'],
    ['Readers of the crash file. A residual is not a cause.','Omar'],
  ],1.7,[8.3,4.2],5.3);
  text(s,'2023 deaths are published as both 2,273 and 1,216, with the same 5,796 crashes. Show both.',0.45,7.1,12.4,0.28,12,C.amber);
}

{
  const s=stage('2 · Personas','Six readings of those groups. Not people we interviewed.','Ages and jobs are design readings. The portraits are illustrations. Same six cards as the HTML deck.');
  text(s,'Each card states a need, a fear, and a source. The solution slides later name that same person as the one affected.',0.5,1.75,12.3,0.55,16,C.white,{valign:'top'});
  people.forEach((p,i)=>{
    const col=i%3;
    const row=Math.floor(i/3);
    box(s,0.45+col*4.25,2.55+row*2.2,4.05,2.0,C.card,p.color);
    text(s,`P${i+1}  ${p.name}`,0.62+col*4.25,2.7+row*2.2,3.7,0.4,18,C.white,{bold:true});
    text(s,p.role,0.62+col*4.25,3.15+row*2.2,3.7,0.55,13,C.mute,{valign:'top'});
    text(s,p.affected,0.62+col*4.25,3.75+row*2.2,3.7,0.6,13,C.teal,{valign:'top'});
  });
}

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

{
  const s=stage('3 · Persona needs','Each card has one problem. The solution has to reach that person.','Needs are design readings of the groups on the Empathize slide. They are not interview quotes.');
  darkTable(s,[
    ['Who is affected','Need on their card','Problem'],
    ...people.map((p)=>[p.name,p.need,p.problem]),
  ],1.7,[2.2,5.3,5.0],5.4);
}

{
  const research={
    Amara:'Pedestrians were 28% of the 2023 deaths in the WHO case quoting ONSR. The 2024 strategy names older people and people with disabilities. Clearance guidance is about 1.07 m/s, slower where needed.',
    David:'Occupants carry most of that case’s health cost. One matched seed finished 71, 84, and 70 of 84 trips. Mixed. No winner.',
    Chidi:'TRANSTU: 187.4 million paying passengers in 2018, not this year. Waiting time is valued above in-vehicle time in DfT appraisal guidance.',
    Rosa:'ONSR compiles the crash record. SCATS documents an audit trail. That is an analogy, not a Tunis control room we visited.',
    Marcus:'Civil Protection answers road emergencies. A Taipei survival-per-minute figure is a citation from elsewhere. This simulation does not output lives saved.',
    Omar:'The detector has classes. An anomaly does not name a cause. FHWA’s congestion shares are not a map of these junctions.',
  };
  const s=stage('4 · Evidence','Survey, interviews, and research. Only the research column has a source.','No survey file. No interview transcript. Do not invent a percentage, a sample size, or a quote.');
  darkTable(s,[
    ['Who','Survey','Interview','Research that supports the need'],
    ...people.map((p)=>[p.name,'No survey file','Not interviewed',research[p.name]]),
  ],1.7,[1.5,2.1,2.2,6.7],5.4);
}

{
  const s=stage('5 · Ideation','Each idea starts from that person’s need.','A later idea still needs a file. A rejected idea does not become a solution. A sentence must not become the signal.');
  darkTable(s,[
    ['Who is affected','Need','Idea we keep'],
    ...people.map((p)=>[p.name,p.problem,p.idea]),
  ],1.7,[2.3,4.6,5.6],5.2);
  text(s,'Refused: a scraped map as truth, a camera that guesses ability, a chatbot that writes the light, a lives-saved claim.',0.45,7.05,12.4,0.28,12,C.mute);
}

{
  const s=stage('6 · Solutions','Who is affected, then the solution that reaches them.','Only A1 writes the signal. Synapse explains the log or abstains.');
  darkTable(s,[
    ['Who is affected','Problem','Solution'],
    ...people.map((p)=>[p.affected,p.problem,p.solution]),
  ],1.7,[3.3,4.2,5.0],5.4);
}

{
  const s=stage('7 · Online data collection','Accidents, roads, intersections, lights, weather, and transport are different files.','A scraped map colour or a news post is not a ground-truth crash.');
  darkTable(s,[
    ['Source','Status','What it can support'],
    ['Accidents — ONSR, INS, WHO published totals','Context','Who is harmed, at national or governorate scale. Not this junction and this hour.'],
    ['Roads and intersections — OpenStreetMap','Later','A labelled map. Row 14 is not started. Not today’s speeds.'],
    ['Traffic lights — our SUMO runs','Now','Reason codes and legal phases in the model. No public adaptive network in Tunis was found.'],
    ['Weather — station joined to junction and hour','Later','A regime tag, after that table exists. Not “rain caused the crash.”'],
    ['Traffic and public transport — TRANSTU, with the year','Later','187.4 million paying passengers in 2018. Not a live bus.'],
  ],1.7,[5.2,1.6,5.7],5.3);
}

{
  const s=stage('8 · Data analysis','Patterns we can name. Not a hotspot model.','A risk factor for one intersection, hour, and weather type was not found.');
  const lines=[
    'ONSR press briefing: inattention about 42% of crashes, speeding about 14% of crashes and about 30% of deaths, unsafe pedestrian crossing about 8% of crashes. Cause classes in that briefing, not a model of our junction.',
    'Men are the large majority of recorded deaths in the WHO profile and the investment case.',
    'One matched seed: actuated finished more trips and had a lower mean wait. Max-Pressure did not win. Unfinished trips stayed in the count.',
    'Emission-proxy fixture: one link improved and one worsened. Displacement, not measured air.',
  ];
  lines.forEach((line,i)=>{
    box(s,0.45,1.75+i*1.25,12.4,1.1,C.card,C.line);
    text(s,line,0.65,1.75+i*1.25,12.0,1.1,14,C.white,{valign:'mid'});
  });
}

{
  const s=stage('9 · Heatmap','No hotspot map until the table exists.','A dark cell is not a cause and not a life saved.');
  text(s,'A shaded map needs rows of intersection, time, and the thing being counted, plus the denominator. That table is not in the repository.',0.5,1.8,12.3,0.9,18,C.white,{valign:'top'});
  box(s,0.45,2.9,6.1,3.5,C.card,C.red);
  text(s,'WILL NOT DRAW',0.7,3.1,5.6,0.35,13,C.red,{bold:true,charSpacing:1});
  text(s,'Rain over roads. Crash pins from the news. A green map that hides the link whose proxy got worse.',0.7,3.55,5.6,2.5,16,C.white,{valign:'top'});
  box(s,6.75,2.9,6.1,3.5,C.card,C.teal);
  text(s,'LATER, WITH THE METHOD PRINTED',0.98,3.1,5.6,0.35,12,C.teal,{bold:true,charSpacing:0.6});
  text(s,'Counts of a class, or delay, by link and by time window, with the sample size on the cell.',0.98,3.55,5.6,2.5,16,C.white,{valign:'top'});
}

{
  const s=stage('10 · Accident prevention','How each solution addresses that person’s problem.','Fewer conflicts in the model. Not fewer deaths in Tunisia. No lives saved. No measured air. No Tunis deployment. No winner.');
  darkTable(s,[
    ['Who is affected','What changes for them'],
    ...people.map((p)=>[p.name,p.prevention]),
  ],1.7,[2.4,10.1],5.15);
  text(s,'No lives saved. No measured air. No Tunis deployment. No winner.',0.45,7.05,12.4,0.28,13,C.amber,{bold:true});
}

if(people.length!==6)throw new Error('Expected 6 personas');
const output=path.join(__dirname,'CoFlow-5-Persona-Cards.pptx');
pptx.writeFile({fileName:output}).then(()=>console.log(`SUCCESS ${output}`)).catch((e)=>{console.error(e);process.exit(1);});
