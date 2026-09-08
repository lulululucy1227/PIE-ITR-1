import test from 'node:test';
import assert from 'node:assert/strict';
import {buildServicePlan} from '../src/service-plan.mjs';

const context={cardId:'fixture-card',model:'FIXTURE MODEL',firmware:'1.2',knowledgeVersion:'fixture-v1',confirmedFacts:['part-fitment-confirmed','replacement-target-confirmed']};
const result={kind:'repair',pathId:'fixture-path',part:'Confirmed test target',action:['Confirm the fault with the supported test.','Perform the confirmed service action.'],verification:{steps:['Repeat the supported test.']},ifNotFixed:{kind:'escalate',message:'Contact PIE.'}};
const resource=()=>({id:'fixture-support',kind:'parts',status:'APPROVED',review:{scopeConfirmed:true,safetyReviewed:true},binding:{...context,pathId:result.pathId,actionIndex:1,instruction:result.action[1]},title:'Approved fixture part',lines:['Check the supplied service instruction.'],requires:['part-fitment-confirmed','replacement-target-confirmed'],partNumber:'FIXTURE-PART',quantity:1});

test('legacy guidance becomes ordered steps without rewriting instructions or inventing support',()=>{
 const plan=buildServicePlan(result,context);
 assert.deepEqual(plan.steps.map(s=>s.instruction),result.action);
 assert.deepEqual(plan.verification,result.verification.steps);
 assert.deepEqual(plan.steps.map(s=>s.support),[[],[]]);
 assert.equal(plan.fallback,result.ifNotFixed.message);
});
test('future support is bound to the exact approved instruction, model, version and path',()=>{
 const plan=buildServicePlan(result,context,[resource()]);
 assert.equal(plan.steps[0].support.length,0);
 assert.equal(plan.steps[1].support[0].partNumber,'FIXTURE-PART');
 assert.equal('review' in plan.steps[1].support[0],false);
 for(const key of ['cardId','model','firmware','knowledgeVersion','pathId','instruction']){
  const record=resource();record.binding[key]='unrelated';
  assert.deepEqual(buildServicePlan(result,context,[record]).steps[1].support,[],key);
 }
});
test('draft, unreviewed, malformed and incompatible parts never become optional guidance',()=>{
 const variants=[r=>r.status='DRAFT',r=>r.review.safetyReviewed=false,r=>r.review.scopeConfirmed=false,r=>r.binding.model='',r=>r.quantity=0,r=>r.partNumber='',r=>r.kind='uncontrolled',r=>r.lines=[],r=>r.binding.actionIndex=-1];
 for(const mutate of variants){const r=resource();mutate(r);assert.equal(buildServicePlan(result,context,[r]).steps.flatMap(s=>s.support).length,0);}
});
test('support never creates a solution for unresolved or PIE-only results',()=>{
 for(const kind of ['escalate','choose_symptom','scope_required','qualifier_required','reported_fixed'])assert.equal(buildServicePlan({...result,kind},context,[resource()]),null);
});
test('check/information paths cannot acquire a parts recommendation through future support',()=>{
 for(const kind of ['check','information'])assert.deepEqual(buildServicePlan({...result,kind},context,[resource()]).steps[1].support,[]);
});
test('source data is not mutated and private extra fields are never carried into the plan',()=>{
 const r=resource();r.privateSource='PRIVATE-CANARY';const before=JSON.stringify([result,context,r]);
 const plan=buildServicePlan(result,context,[r]);assert.equal(JSON.stringify(plan).includes('PRIVATE-CANARY'),false);assert.equal(JSON.stringify([result,context,r]),before);
});
test('a likely target is not enough to recommend a part without confirmed fitment and target',()=>{
 for(const confirmedFacts of [[],['part-fitment-confirmed'],['replacement-target-confirmed']])assert.deepEqual(buildServicePlan(result,{...context,confirmedFacts},[resource()]).steps[1].support,[]);
 const r=resource();r.requires=[];assert.deepEqual(buildServicePlan(result,context,[r]).steps[1].support,[]);
});
test('disassembly supplements require explicit safe-to-open and procedure-scope facts',()=>{
 const r={...resource(),kind:'disassembly',requires:['safe-to-open-confirmed','service-procedure-scope-confirmed']};
 assert.deepEqual(buildServicePlan(result,context,[r]).steps[1].support,[]);
 assert.equal(buildServicePlan(result,{...context,confirmedFacts:r.requires},[r]).steps[1].support.length,1);
});
