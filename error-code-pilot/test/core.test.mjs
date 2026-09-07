import test from 'node:test';
import assert from 'node:assert/strict';
import {validateCatalog, projectAgentCatalog, searchCards, resolveCard, recordOutcome, exportWorkbench} from '../src/engine.mjs';

// Synthetic contract fixtures: never included in the pilot knowledge/build.
// Breaks caught: sign loss, implicit fuzzy match, scope bypass, failure loops,
// unsupported publication, unverified closure and source metadata leakage.
const repair = {
  id:'repair', symptom:'Same fault with a free mechanism', kind:'repair',
  part:'Test cable', action:['Replace the test cable.'],
  verification:{steps:['Run the functional check.'],canonical:['Run the functional check.']},
  ifNotFixed:{kind:'path',pathId:'board',message:'Use the validated next step.'}
};
const board = {...repair,id:'board',directSelectable:false,part:'Test board',action:['Replace the test board.'],
  ifNotFixed:{kind:'escalate',message:'Contact PIE with the result.'}};
const card = {
  id:'fixture-a',code:'-552',message:'Test motor voltage too low',aliases:['Motor supply low'],
  classification:'SELF_SERVICE_SYMPTOM_SPLIT',lifecycle:'CURRENT',publication:'approved',
  agentVisible:true,scope:{status:'confirmed',models:['Test Model A'],firmware:['1.2.3']},
  evidence:{kind:'promoted_service_rule',refs:['test-fixture#only'],outcome:'recommended',cohortCount:null},
  paths:[repair,board],lastReviewed:'2026-09-07',supersededBy:null
};
const catalog = {schemaVersion:1,knowledgeVersion:'fixture-v1',cards:[card]};
const ctx = {model:'Test Model A',firmware:'1.2.3'};
const copy = value => structuredClone(value);

test('schema accepts a scoped complete repair and rejects missing failure evidence',()=>{
  assert.deepEqual(validateCatalog(catalog),[]);
  const bad=copy(catalog);delete bad.cards[0].paths[0].ifNotFixed;
  assert.ok(validateCatalog(bad).some(x=>x.includes('ifNotFixed')));
});
test('schema rejects raw-only replacement, invented counts and undocumented model scope',()=>{
  for(const mutate of [
    c=>c.cards[0].evidence.kind='raw_reference',
    c=>c.cards[0].evidence.cohortCount=-1,
    c=>c.cards[0].scope.models=[],
    c=>c.cards[0].evidence.refs=[]
  ]) {const bad=copy(catalog);mutate(bad);assert.ok(validateCatalog(bad).length);}
});
test('schema rejects duplicate ids, dangling and cyclic failure transitions',()=>{
  for(const mutate of [
    c=>c.cards.push(copy(c.cards[0])),
    c=>c.cards[0].paths[0].ifNotFixed.pathId='missing',
    c=>c.cards[0].paths[1].ifNotFixed={kind:'path',pathId:'repair',message:'Repeat'}
  ]) {const bad=copy(catalog);mutate(bad);assert.ok(validateCatalog(bad).length);}
});
test('agent projection removes internal fields and hidden/deprecated records',()=>{
  const data=copy(catalog);
  data.cards[0].evidence.notes='INTERNAL-CANARY';
  data.cards[0].scope.internalNote='SCOPE-PRIVATE-CANARY';
  data.cards[0].paths[0].ifNotFixed.internalSource='FALLBACK-PRIVATE-CANARY';
  data.cards.push({...copy(card),id:'retired',code:'11',lifecycle:'RETIRED'});
  data.cards.push({...copy(card),id:'hidden',code:'12',agentVisible:false});
  const projected=projectAgentCatalog(data);
  assert.equal(projected.cards.length,1);
  assert.equal(JSON.stringify(projected).includes('INTERNAL-CANARY'),false);
  assert.equal(JSON.stringify(projected).includes('PRIVATE-CANARY'),false);
  assert.equal('evidence' in projected.cards[0],false);
  assert.equal('lastReviewed' in projected.cards[0],false);
});
test('exact signed codes, Unicode minus and code zero preserve identity',()=>{
  const cards=[card,{...card,id:'positive',code:'552'},{...card,id:'zero',code:'0'}];
  assert.equal(searchCards(cards,'−552').matches[0].id,'fixture-a');
  assert.equal(searchCards(cards,'552').matches[0].id,'positive');
  assert.equal(searchCards(cards,'0').matches[0].id,'zero');
  assert.equal(searchCards([card],'552').kind,'unsupported');
});
test('exact message/alias match survives surrounding whitespace and case',()=>{
  assert.equal(searchCards([card],'  MOTOR SUPPLY LOW ').kind,'exact_message');
  assert.equal(searchCards([card],card.message).kind,'exact_message');
});
test('pasted code and message find an exact candidate without misreading multiple codes',()=>{
  assert.equal(searchCards([card],'Error code: -552').kind,'exact_code');
  const r=searchCards([card,{...card,id:'other',code:'-584'}],'-552 and -584');
  assert.equal(r.kind,'candidates');assert.equal(r.matches.length,2);
});
test('fuzzy message shows several candidates and never returns an automatic repair',()=>{
  const r=searchCards([card,{...card,id:'other',code:'-584',message:'Test wheel voltage too low'}],'voltage low');
  assert.equal(r.kind,'candidates');assert.equal(r.matches.length,2);
  assert.equal(r.autoOpen,false);
});
test('unknown numbers and arbitrary text remain unsupported',()=>{
  assert.equal(searchCards([card],'999999').kind,'unsupported');
  assert.equal(searchCards([card],'banana').kind,'unsupported');
  assert.equal(searchCards([card],'').kind,'empty');
});
test('model/version mismatch or missing context blocks replacement',()=>{
  for(const c of [{},{model:'Test Model B',firmware:'1.2.3'},{model:'Test Model A'},{model:'Test Model A',firmware:'2.0'}]) {
    const r=resolveCard(card,c);assert.equal(r.kind,'scope_required');assert.equal(r.part,null);
  }
  assert.equal(resolveCard(card,ctx).part,'Test cable');
});
test('unknown model scope cannot be bypassed by arbitrary user model input',()=>{
  const c=copy(card);c.scope={status:'unknown',models:[],firmware:[]};
  assert.equal(resolveCard(c,ctx).kind,'escalate');
  assert.equal(resolveCard(c,ctx).part,null);
});
test('historical and superseded knowledge cannot silently return current repair',()=>{
  for(const lifecycle of ['HISTORICAL','SUPERSEDED','RETIRED','REVIEW_REQUIRED']) {
    const c={...card,lifecycle};
    assert.equal(resolveCard(c,ctx).kind,'escalate');
    assert.equal(resolveCard(c,ctx).part,null);
  }
});
test('multiple selectable symptoms require selection before revealing a part',()=>{
  const c=copy(card);c.paths.unshift({...copy(repair),id:'other',symptom:'Different observed symptom'});
  assert.equal(resolveCard(c,ctx).kind,'choose_symptom');
  assert.equal(resolveCard(c,{...ctx,pathId:'repair'}).part,'Test cable');
  assert.equal(resolveCard(c,{...ctx,pathId:'bogus'}).kind,'escalate');
});
test('follow-up-only repair cannot be opened without previous failed repair',()=>{
  assert.equal(resolveCard(card,{...ctx,pathId:'board'}).kind,'escalate');
});
test('failed replacement advances once then escalates instead of looping',()=>{
  const first=recordOutcome(card,'repair','not_fixed',ctx);
  assert.equal(first.kind,'repair');assert.equal(first.part,'Test board');
  const final=recordOutcome(card,'board','not_fixed',{...ctx,completedRepairs:['repair']});
  assert.equal(final.kind,'escalate');assert.equal(final.part,null);
  assert.equal(resolveCard(card,{...ctx,completedRepairs:['repair','board']}).kind,'escalate');
});
test('returned issue routes to PIE rather than restarting a replacement sequence',()=>{
  const result=resolveCard(card,{...ctx,returned:true});
  assert.equal(result.kind,'escalate');assert.equal(result.part,null);
});
test('Fixed requires verification and never claims a verified case closure',()=>{
  assert.equal(recordOutcome(card,'repair','fixed',ctx).kind,'verification_required');
  const r=recordOutcome(card,'repair','fixed',{...ctx,verificationComplete:true});
  assert.equal(r.kind,'reported_fixed');assert.equal(r.caseClosed,false);
});
test('informational normal-function branch gives no repair and abnormal branch escalates',()=>{
  const c={...copy(card),scope:{status:'not_required',models:[],firmware:[]},paths:[
    {...repair,id:'normal',symptom:'Function is normal',kind:'information',part:null,action:['No repair is needed for this success message.'],ifNotFixed:{kind:'escalate',message:'Contact PIE.'}},
    {...repair,id:'abnormal',symptom:'A fault is still present',kind:'escalate',part:null,action:['Contact PIE about the actual fault.'],ifNotFixed:{kind:'escalate',message:'Contact PIE.'}}
  ]};
  assert.equal(resolveCard(c,{}).kind,'choose_symptom');
  assert.equal(resolveCard(c,{pathId:'normal'}).kind,'information');
  assert.equal(resolveCard(c,{pathId:'abnormal'}).kind,'escalate');
});
test('Workbench default export withholds pilot candidates and keeps approval distinct from applicability',()=>{
  const pilot=copy(catalog);pilot.cards[0].publication='pilot';
  assert.deepEqual(exportWorkbench(pilot,ctx).entries,[]);
  const approved=copy(catalog);approved.cards[0].publication='approved';
  assert.equal(exportWorkbench(approved,ctx).entries[0].applicable,true);
  assert.equal(exportWorkbench(approved,{model:'wrong'}).entries[0].applicable,false);
  assert.equal(exportWorkbench(approved,ctx).readOnly,true);
});
