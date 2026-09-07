import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {validateCatalog,projectAgentCatalog,searchCards,resolveCard,recordOutcome,exportWorkbench} from '../src/engine.mjs';
const catalog=JSON.parse(fs.readFileSync(new URL('../data/canonical.json',import.meta.url)));
test('real pilot data satisfies the canonical contract',()=>assert.deepEqual(validateCatalog(catalog),[]));
test('real exact code, multilingual alias and exact message select the intended guide',()=>{
  const cards=projectAgentCatalog(catalog).cards;
  for(const [query,want] of [['1202','ec-1202'],['Schneidscheibe blockiert','ec-1202'],['Robot is locked','ec-1008'],['Chassis data serial port disconnected','ec-1500'],['DT-041','ec-dt041']]) assert.equal(searchCards(cards,query).matches[0].id,want);
});
test('undocumented 1202 scope cannot leak replacement instruction into agent build',()=>{
  const canonical=catalog.cards.find(c=>c.code==='1202');
  const projected=projectAgentCatalog(catalog).cards.find(c=>c.code==='1202');
  if(canonical.scope.status==='unknown') {
    assert.equal(JSON.stringify(projected).includes('Upper Shell Adapter Cable'),false);
    assert.equal(resolveCard(projected,{pathId:'cable',model:'LUBA 3'}).kind,'escalate');
  } else assert.equal(canonical.scope.status,'confirmed');
});
test('5510 success does not make an abnormal mower a no-repair case',()=>{
  const c=projectAgentCatalog(catalog).cards.find(c=>c.code==='5510');
  assert.equal(resolveCard(c,{pathId:'normal'}).kind,'information');
  assert.equal(resolveCard(c,{pathId:'abnormal'}).kind,'escalate');
});
test('historical firmware stays internal and real cohorts are not invented',()=>{
  const c=catalog.cards.find(c=>c.code==='1000022');
  assert.equal(resolveCard(c,{model:'LUBA mini 2 1000 Vision'}).kind,'escalate');
  assert.equal(JSON.stringify(projectAgentCatalog(catalog)).includes('2.3.30.26'),false);
  assert.ok(catalog.cards.every(c=>c.evidence.cohortCount===null));
});
test('local approval remains a non-decisive read-only export without changing MAIN',()=>{
  const exported=exportWorkbench(catalog);
  assert.equal(exported.readOnly,true);
  assert.ok(exported.entries.every(e=>e.decisive===false));
});
test('uncleared physical blockage cannot advance to a cable replacement even after model approval',()=>{
  const card=structuredClone(catalog.cards.find(c=>c.code==='1202'));
  card.scope={status:'confirmed',models:['TEST MODEL'],firmware:[]};
  const result=recordOutcome(card,'blocked','not_fixed',{model:'TEST MODEL',verificationComplete:false});
  assert.equal(result.kind,'escalate');
  assert.equal(result.part,null);
});

test('desktop data contains exactly the approved 28 symptoms in 10 areas',()=>{
  assert.equal(catalog.schemaVersion,2);
  assert.deepEqual(catalog.symptoms.map(s=>s.symptom_id),Array.from({length:28},(_,i)=>'SYM-'+String(i+1).padStart(3,'0')));
  assert.equal(new Set(catalog.symptoms.map(s=>s.observable_area)).size,10);
  assert.equal(catalog.symptoms.filter(s=>s.agent_visibility==='NAVIGATION').length,25);
  assert.ok(catalog.symptoms.slice(25).every(s=>s.agent_visibility==='PIE_ONLY'&&s.repair_refs.length===0));
});

test('narrow maintained Function Test fix is symptom-only with exact model and version scope',()=>{
  const c=catalog.cards.find(c=>c.id==='sym-cutting-functional-test');
  assert.ok(c);
  assert.equal(c.code,null);
  assert.deepEqual(c.scope.models,['LUBA 2 5000X']);
  assert.deepEqual(c.scope.firmware,['1.30.31.10']);
  const p=c.paths.find(p=>p.id==='software');
  assert.equal(p.evidence_state,'STABLE_OPERATIONAL_GUIDANCE');
  assert.ok(p.qualifier.includes('Auto Run'));
  for(const item of ['Functional Test','Communication Check','Auto Map Run','Retain all three reports','Connect Checking screenshot'])assert.ok(p.verification.canonical.includes(item));
  assert.ok(catalog.symptoms.find(s=>s.symptom_id==='SYM-004').repair_refs.some(r=>r.card_id===c.id));
});

test('signed LiDAR timestamp stays a conditional secondary-fault guardrail, never a replacement',()=>{
  const c=catalog.cards.find(c=>c.code==='-2000303');
  assert.ok(c);
  assert.ok(c.paths.every(p=>p.kind!=='repair'));
  assert.ok(c.paths.some(p=>p.action.join(' ').includes('shared-power')));
});
