import test from 'node:test';
import assert from 'node:assert/strict';
import * as engine from '../src/engine.mjs';

const context={model:'Model A',firmware:'1.2'};
const copy=x=>structuredClone(x);
const path={id:'cable',symptom:'The device does not move',kind:'repair',part:'Fixture cable',action:['Replace fixture cable.'],directSelectable:true,
  verification:{steps:['Run relevant check.'],canonical:['Full canonical verification PRIVATE-CANARY']},
  ifNotFixed:{kind:'escalate',message:'Contact PIE.'},evidence_state:'VERIFIED_RESOLUTION',publication:'approved',agent_visibility:'P0_DESKTOP_SELF_SERVICE',conflict:false,supersededBy:null,
  review:{scopeConfirmed:true,repeatedUse:false,activeMaintenance:false,noContradiction:true,rationale:'Synthetic resolved fixture.'}};
const card={id:'motion',code:'123',message:'Movement error',aliases:['Movement fault'],classification:'SELF_SERVICE_DIRECT',lifecycle:'CURRENT',publication:'approved',agentVisible:true,
  lastReviewed:'2026-09-08',supersededBy:null,scope:{status:'confirmed',models:['Model A'],firmware:['1.2']},
  evidence:{kind:'promoted_case_outcome',refs:['fixture'],outcome:'resolved',cohortCount:null},paths:[path]};
const symptom={symptom_id:'SYM-001',observable_area:'Movement',label_en:'Does not move',label_cn:'无法移动',aliases:['Cannot move'],agent_visibility:'NAVIGATION',repair_refs:[{card_id:'motion',repair_path_id:'cable'}]};
const catalog={schemaVersion:2,knowledgeVersion:'desktop-fixture',cards:[card],symptoms:[symptom]};

// Schema regressions: identity collisions, invalid evidence and broken navigation must never build.
test('v2 accepts controlled symptom references including symptom-only cards',()=>{
  assert.deepEqual(engine.validateCatalog(catalog),[]);
  const c=copy(catalog);c.cards[0].code=null;
  assert.deepEqual(engine.validateCatalog(c),[]);
  assert.equal(engine.searchCards(c.cards,'null').kind,'unsupported');
});
test('v2 rejects duplicate symptoms, unknown areas, unknown evidence and dangling references',()=>{
  for(const change of [c=>c.symptoms.push(copy(symptom)),c=>c.symptoms[0].observable_area='Parts',c=>c.symptoms[0].label_en='',c=>c.symptoms[0].label_cn='',c=>c.symptoms[0].agent_visibility='P0',c=>c.symptoms[0].repair_refs[0].card_id='missing',c=>c.symptoms[0].repair_refs[0].repair_path_id='missing',c=>c.cards[0].paths[0].evidence_state='OLD_ENOUGH',c=>delete c.cards[0].paths[0].review,c=>delete c.cards[0].paths[0].verification,c=>delete c.cards[0].paths[0].ifNotFixed]) {
    const c=copy(catalog);change(c);assert.ok(engine.validateCatalog(c).length,change.toString());
  }
});
test('the ten controlled areas are usable while PIE-only reserved symptoms cannot become navigation',()=>{
  assert.deepEqual(engine.OBSERVABLE_AREAS,['Movement','Cutting','Charging','Docking','Power','Positioning','Connectivity','Sensors','Physical','Software']);
  const c=copy(catalog);c.symptoms[0].symptom_id='SYM-026';assert.ok(engine.validateCatalog(c).length);
});
test('public cards require approved publication independently of agent visibility and priority',()=>{
  for(const publication of ['candidate','withheld','pilot']) {
    const c=copy(catalog);c.cards[0].publication=publication;
    assert.equal(engine.projectAgentCatalog(c).cards.length,0);
    assert.equal(engine.resolveCard(c.cards[0],context).kind,'escalate');
  }
});
test('repair recommendation, incomplete stability, conflict, supersession and PIE-only priority stay withheld',()=>{
  for(const change of [p=>p.evidence_state='SOURCE_RECOMMENDATION',p=>p.evidence_state='ACTION_PERFORMED_OUTCOME_UNKNOWN',p=>p.evidence_state='CONFLICTING_EVIDENCE',p=>p.evidence_state='STABLE_OPERATIONAL_GUIDANCE',p=>p.conflict=true,p=>p.supersededBy='newer',p=>p.publication='candidate',p=>p.agent_visibility='PIE_ONLY',p=>p.review.scopeConfirmed=false]) {
    const c=copy(catalog);change(c.cards[0].paths[0]);
    const publicCard=engine.projectAgentCatalog(c).cards[0];
    assert.equal(publicCard.paths[0].kind,'escalate',change.toString());
    assert.equal(engine.resolveCard(c.cards[0],context).kind,'escalate');
    assert.equal(JSON.stringify(publicCard).includes('Fixture cable'),false);
    assert.equal(JSON.stringify(publicCard).includes('PRIVATE-CANARY'),false);
  }
});
test('maintained repeated conflict-free scoped stability permits a repair without solved feedback',()=>{
  const c=copy(catalog);const p=c.cards[0].paths[0];p.evidence_state='STABLE_OPERATIONAL_GUIDANCE';Object.assign(p.review,{repeatedUse:true,activeMaintenance:true,noContradiction:true});c.cards[0].evidence.outcome='recommended';
  assert.equal(engine.projectAgentCatalog(c).cards[0].paths[0].kind,'repair');
  assert.equal(engine.resolveCard(c.cards[0],context).part,'Fixture cable');
  p.review.noContradiction=false;assert.equal(engine.resolveCard(c.cards[0],context).kind,'escalate');
});
test('approved safe nonrepair guardrails may use source recommendations but check and information scope is enforced',()=>{
  for(const kind of ['check','information']) {
    const c=copy(catalog);Object.assign(c.cards[0].paths[0],{kind,part:null,evidence_state:'SOURCE_RECOMMENDATION'});
    assert.equal(engine.projectAgentCatalog(c).cards[0].paths[0].kind,kind);
    assert.equal(engine.resolveCard(c.cards[0],{}).kind,'scope_required');
    assert.equal(engine.resolveCard(c.cards[0],context).kind,kind);
  }
});
test('1202 repair freeze cannot be bypassed by schema, publication, scope or direct resolver/export entry',()=>{
  for(const schemaVersion of [1,2]) {
    const c=copy(catalog);c.schemaVersion=schemaVersion;c.cards[0].code='1202';
    if(schemaVersion===1) for(const k of ['evidence_state','publication','agent_visibility','conflict','supersededBy','review']) delete c.cards[0].paths[0][k];
    assert.equal(engine.projectAgentCatalog(c).cards[0].paths[0].kind,'escalate');
    assert.equal(engine.resolveCard(c.cards[0],context).kind,'escalate');
    assert.equal(engine.exportWorkbench(c,context).entries[0].result.kind,'escalate');
  }
});
test('projection strips canonical verification and internal symptom metadata while preserving usable references',()=>{
  const c=copy(catalog);c.symptoms[0].internal='PRIVATE-CANARY';
  const publicCatalog=engine.projectAgentCatalog(c);
  assert.deepEqual(Object.keys(publicCatalog.symptoms[0]).sort(),['aliases','label_en','observable_area','repair_refs','symptom_id']);
  assert.equal(JSON.stringify(publicCatalog).includes('PRIVATE-CANARY'),false);
  assert.deepEqual(engine.resolveCard(c.cards[0],context).verification,{steps:['Run relevant check.']});
  c.cards[0].publication='candidate';assert.deepEqual(engine.projectAgentCatalog(c).symptoms[0].repair_refs,[]);
});
test('symptom and code entry produce the same repair contract, and multiple refs require selection',()=>{
  assert.equal(typeof engine.resolveSymptom,'function');
  const publicCatalog=engine.projectAgentCatalog(catalog);
  const result=engine.resolveSymptom(publicCatalog,'SYM-001',context);
  assert.equal(result.part,'Fixture cable');
  assert.deepEqual(result,engine.resolveCard(publicCatalog.cards[0],{...context,pathId:'cable'}));
  const c=copy(catalog);c.cards.push({...copy(card),id:'second',code:null});c.symptoms[0].repair_refs.push({card_id:'second',repair_path_id:'cable'});
  const choice=engine.resolveSymptom(engine.projectAgentCatalog(c),'SYM-001',context);
  assert.equal(choice.kind,'choose_path');assert.equal(choice.choices.length,2);assert.deepEqual(choice.choices[1],{cardId:'second',pathId:'cable',label:'The device does not move'});
});
test('PIE-only, unsupported and unlinked symptoms escalate with no private repair content',()=>{
  assert.equal(typeof engine.resolveSymptom,'function');
  const c=copy(catalog);c.symptoms[0].agent_visibility='PIE_ONLY';
  assert.equal(engine.resolveSymptom(c,'SYM-001',context).kind,'escalate');
  assert.equal(engine.projectAgentCatalog(c).symptoms.length,0);
  c.symptoms[0].agent_visibility='NAVIGATION';c.symptoms[0].repair_refs=[];
  assert.equal(engine.resolveSymptom(c,'SYM-001',context).kind,'escalate');
  assert.equal(engine.resolveSymptom(c,'no-such-symptom',context).kind,'escalate');
});
test('symptom search matches only controlled English labels and aliases, never inferred free text',()=>{
  assert.equal(typeof engine.searchSymptoms,'function');
  assert.equal(engine.searchSymptoms([symptom],'  CANNOT MOVE  ').matches[0].symptom_id,'SYM-001');
  for(const q of ['moving slowly because cable broken','cannot','无法移动','99999']) assert.equal(engine.searchSymptoms([symptom],q).kind,'unsupported');
  assert.equal(engine.searchSymptoms([symptom],'').kind,'empty');
});
test('failed repair cannot leak a candidate next action through direct resolution or outcome handling',()=>{
  const c=copy(catalog);c.cards[0].paths.push({...copy(path),id:'hidden',directSelectable:false,publication:'candidate',action:['PRIVATE-CANARY next repair']});
  c.cards[0].paths[0].ifNotFixed={kind:'path',pathId:'hidden',message:'PRIVATE-CANARY candidate details'};
  const publicCard=engine.projectAgentCatalog(c).cards[0];
  assert.equal(JSON.stringify(publicCard).includes('PRIVATE-CANARY'),false);
  assert.equal(engine.recordOutcome(c.cards[0],'cable','not_fixed',context).kind,'escalate');
  assert.equal(engine.resolveCard(c.cards[0],{...context,pathId:'hidden',completedRepairs:['cable']}).kind,'escalate');
});
test('a qualifier requires explicit confirmation before either entry route can execute',()=>{
  const c=copy(catalog);c.cards[0].paths[0].qualifier='The observed condition is present';
  const p=engine.projectAgentCatalog(c);
  assert.equal(p.cards[0].paths[0].qualifier,'The observed condition is present');
  assert.equal(engine.resolveCard(c.cards[0],context).kind,'qualifier_required');
  assert.equal(engine.resolveSymptom(p,'SYM-001',context).kind,'qualifier_required');
  assert.equal(engine.resolveSymptom(p,'SYM-001',{...context,qualifierConfirmed:true}).kind,'repair');
});
test('direct canonical resolution fails closed on incomplete verification, review and fallback contracts',()=>{
  for(const change of [p=>delete p.verification.canonical,p=>p.ifNotFixed.kind='unknown',p=>delete p.review.rationale,p=>delete p.review.repeatedUse]) {
    const c=copy(catalog);change(c.cards[0].paths[0]);
    assert.ok(engine.validateCatalog(c).length);
    assert.equal(engine.resolveCard(c.cards[0],context).kind,'escalate',change.toString());
  }
});
test('a confirmed qualifier from a failed step cannot silently authorize a different next-step condition',()=>{
  const c=copy(catalog);c.cards[0].paths[0].qualifier='First condition';
  c.cards[0].paths.push({...copy(path),id:'next',directSelectable:false,qualifier:'Different next condition'});
  c.cards[0].paths[0].ifNotFixed={kind:'path',pathId:'next',message:'Continue to the next check.'};
  const result=engine.recordOutcome(c.cards[0],'cable','not_fixed',{...context,qualifierConfirmed:true});
  assert.equal(result.kind,'qualifier_required');assert.equal(result.pathId,'next');
});
test('approved PIE-only escalation preserves reviewed guidance and strips nested internal metadata',()=>{
  const c=copy(catalog);const p=c.cards[0].paths[0];
  Object.assign(p,{kind:'escalate',part:null,agent_visibility:'PIE_ONLY',evidence_state:'SOURCE_RECOMMENDATION',action:['If this fault recurs, send the observed symptom and prior repair result to PIE.']});
  p.verification.steps=['Retain the relevant fault observation for PIE.'];
  p.verification.internal={notes:'PRIVATE-CANARY'};
  p.ifNotFixed.internal={source:'PRIVATE-CANARY'};
  p.review.internal={ticket:'PRIVATE-CANARY'};
  const projected=engine.projectAgentCatalog(c);const result=engine.resolveCard(c.cards[0],context);
  assert.deepEqual(projected.cards[0].paths[0].action,['If this fault recurs, send the observed symptom and prior repair result to PIE.']);
  assert.deepEqual(result.action,['If this fault recurs, send the observed symptom and prior repair result to PIE.']);
  assert.deepEqual(result.verification,{steps:['Retain the relevant fault observation for PIE.']});
  assert.equal(JSON.stringify(projected).includes('PRIVATE-CANARY'),false);
  assert.equal(JSON.stringify(result).includes('PRIVATE-CANARY'),false);
  for(const change of [p=>p.publication='candidate',p=>p.conflict=true,p=>p.supersededBy='newer',p=>p.evidence_state='CONFLICTING_EVIDENCE']) {
    const blocked=copy(c);change(blocked.cards[0].paths[0]);
    assert.equal(JSON.stringify(engine.projectAgentCatalog(blocked)).includes('If this fault recurs'),false);
  }
});
test('PIE-only repair, check and information paths never become direct self-service',()=>{
  for(const kind of ['repair','check','information']) {
    const c=copy(catalog);Object.assign(c.cards[0].paths[0],{kind,part:kind==='repair'?'Fixture cable':null,agent_visibility:'PIE_ONLY',action:['PRIVATE-CANARY executable action']});
    const projected=engine.projectAgentCatalog(c);
    assert.equal(projected.cards[0].paths[0].kind,'escalate');
    assert.equal(engine.resolveCard(c.cards[0],context).kind,'escalate');
    assert.equal(JSON.stringify(projected).includes('PRIVATE-CANARY'),false);
  }
});
