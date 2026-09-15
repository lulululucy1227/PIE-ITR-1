import test from 'node:test';
import assert from 'node:assert/strict';
import {projectHardwareSupport} from '../lib/hardware-support.mjs';
import {buildAgentServicePlan} from '../src/service-plan.mjs';

const card={id:'guide-fixture',scope:{status:'confirmed',models:['Fixture model'],firmware:[]},paths:[{id:'guided',kind:'repair',action:['Use the supported test.'],verification:{steps:['Repeat test.']},ifNotFixed:{message:'Contact PIE.'}}]};
const catalog={knowledgeVersion:'fixture-v1',cards:[card]};
const source={id:'source',sha256:'a'.repeat(64)};
const record=()=>({id:'tool-fixture',kind:'tools',status:'APPROVED',review:{scopeConfirmed:true,safetyReviewed:true,current:true},sourceRefs:[{sourceId:'source',sha256:source.sha256,section:'Supported test'}],binding:{cardId:card.id,pathId:'guided',model:'Fixture model',firmware:'',knowledgeVersion:'fixture-v1',actionIndex:0,instruction:card.paths[0].action[0]},title:'Supported tool',lines:['Read the test result before choosing the next action.']});
const input=r=>({schemaVersion:1,sources:[source],records:[r]});
const result={...card.paths[0],pathId:'guided'};
const context={cardId:card.id,model:'Fixture model',firmware:'',knowledgeVersion:'fixture-v1'};

test('reviewed tool detail projects without source/review metadata and binds to the current action',()=>{
 const published=projectHardwareSupport(input(record()),catalog);
 const plan=buildAgentServicePlan(result,context,published);
 assert.equal(plan.steps[0].support[0].title,'Supported tool');
 assert.doesNotMatch(JSON.stringify(published),/sourceRefs|sha256|APPROVED|"review"/);
 for(const key of ['model','firmware','knowledgeVersion','cardId'])assert.deepEqual(buildAgentServicePlan(result,{...context,[key]:'other'},published).steps[0].support,[]);
 assert.deepEqual(buildAgentServicePlan({...result,action:['Changed action.']},context,published).steps[0].support,[]);
 assert.equal(buildAgentServicePlan({...result,kind:'escalate'},context,published),null);
});

test('unreviewed, stale, cross-model, altered instruction and source-mismatched details fail before publishing',()=>{
 for(const mutate of [r=>r.status='DRAFT',r=>r.review.current=false,r=>r.binding.model='Other',r=>r.binding.instruction='Changed',r=>r.binding.knowledgeVersion='old',r=>r.sourceRefs[0].sha256='b'.repeat(64),r=>r.lines=['PRIVATE-CANARY'],r=>r.kind='uncontrolled',r=>r.id='person@example.com',r=>r.requires=['person@example.com']]){
  const r=record();mutate(r);assert.throws(()=>projectHardwareSupport(input(r),catalog));
 }
 assert.throws(()=>projectHardwareSupport(input(record()),{...catalog,cards:[{...card,paths:[{...card.paths[0],kind:'escalate'}]}]}));
});

test('part and disassembly details cannot publish without explicit fitment/quantity and safety requirements',()=>{
 const part={...record(),kind:'parts',partNumber:'FIXTURE-PART',quantity:1};
 assert.throws(()=>projectHardwareSupport(input(part),catalog));
 part.requires=['part-fitment-confirmed','replacement-target-confirmed'];
 const published=projectHardwareSupport(input(part),catalog);
 assert.deepEqual(buildAgentServicePlan(result,context,published).steps[0].support,[]);
 assert.equal(buildAgentServicePlan(result,{...context,confirmedFacts:part.requires},published).steps[0].support.length,1);
 const badPart={...part,partNumber:'person@example.com'};assert.throws(()=>projectHardwareSupport(input(badPart),catalog));
 delete part.quantity;assert.throws(()=>projectHardwareSupport(input(part),catalog));
 const disassembly={...record(),kind:'disassembly'};assert.throws(()=>projectHardwareSupport(input(disassembly),catalog));
});
