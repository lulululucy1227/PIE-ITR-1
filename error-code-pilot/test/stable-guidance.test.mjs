import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {validateCatalog,projectAgentCatalog,resolveCard,resolveSymptom,recordOutcome,searchCards} from '../src/engine.mjs';
import {validateCandidates,candidateCounts} from '../lib/candidates.mjs';
const canonical=JSON.parse(fs.readFileSync(new URL('../data/canonical.json',import.meta.url)));
const candidates=JSON.parse(fs.readFileSync(new URL('../data/feishu-candidates.json',import.meta.url)));
const payload=fs.readFileSync(new URL('../../docs/troubleshooter/FEISHU_CANDIDATE_PAYLOAD_2026-09-08.md',import.meta.url),'utf8');
const approved=['REP-WHEEL-001','REP-CUT-001','REP-CHARGE-001','REP-DOCK-001','REP-POWER-001','REP-RTK-001','REP-BUMP-001','REP-CABLE-001','REP-FW-001'];
const publicData=projectAgentCatalog(canonical);
const guideCards=()=>publicData.cards.filter(c=>c.id.startsWith('guide-'));
test('exact nine supervisor-approved candidates publish scoped stable portions with reciprocal references',()=>{
 assert.deepEqual(candidates.candidates.filter(c=>c.review.visibility==='AGENT_GUIDED').map(c=>c.repair_path_id).sort(),approved.slice().sort());
 assert.deepEqual(validateCatalog(canonical),[]);assert.deepEqual(validateCandidates(candidates,canonical,{payloadText:payload}),[]);
 assert.equal(guideCards().length,10,'charge and station recognition keep their different model scopes');
 for(const c of candidates.candidates.filter(c=>approved.includes(c.repair_path_id))){assert.equal(c.review.evidence_state,'STABLE_OPERATIONAL_GUIDANCE');assert.ok(c.review.repeated_use_signal.includes('supervisor'));assert.equal(c.review.first_seen,null);assert.ok(c.review.promoted_refs.length);}
 assert.deepEqual(candidateCounts(candidates).visibility,{AGENT_GUIDED:9,PIE_ONLY:10});
});
test('every new path requires known model, retains canonical verification, and stops after failed or returned action',()=>{
 assert.equal(guideCards().length,10);
 for(const card of guideCards()){
  const path=card.paths[0],full=canonical.cards.find(c=>c.id===card.id).paths[0];
  assert.equal(resolveCard(card).kind,'scope_required',card.id);assert.equal(resolveCard(card,{model:'YUKA',qualifierConfirmed:true}).kind,'scope_required');
  const context={model:card.scope.models[0],qualifierConfirmed:true};assert.ok(['repair','check'].includes(resolveCard(card,context).kind));
  for(const item of ['Functional Test','Communication Check','Auto Map Run','Retain all three reports','Connect Checking screenshot'])assert.ok(full.verification.canonical.includes(item),card.id+item);
  assert.equal(path.ifNotFixed.kind,'escalate');assert.equal(recordOutcome(card,path.id,'not_fixed',context).kind,'escalate');assert.equal(recordOutcome(card,path.id,'returned',context).kind,'escalate');
  assert.equal(recordOutcome(card,path.id,'fixed',context).kind,'verification_required');
  assert.equal(resolveCard(card,{...context,completedRepairs:[path.id]}).kind,'escalate');
 }
});
test('non1202 cutting guidance needs explicit actual-operation condition and cannot replace the exact code route',()=>{
 const card=publicData.cards.find(c=>c.id==='guide-cutting-operation');assert.ok(card);
 assert.equal(resolveCard(card,{model:'LUBA 2'}).kind,'qualifier_required');assert.match(card.paths[0].qualifier,/1202/);assert.match(card.paths[0].qualifier,/actual mowing|manual operation/);
 const choices=resolveSymptom(publicData,'SYM-004',{model:'LUBA 2'});assert.equal(choices.kind,'choose_path');assert.equal(choices.choices.length,2);
 assert.equal(searchCards(publicData.cards,'1202').matches[0].id,'ec-1202');
 const frozen=publicData.cards.find(c=>c.id==='ec-1202');assert.equal(resolveCard(frozen,{model:'LUBA 2',pathId:'cable',qualifierConfirmed:true}).kind,'escalate');
 assert.equal(candidates.frozen[0].review.visibility,'WITHHELD');
});
test('charging scope and observation are separate; uncertain splits and weaker paths remain PIE',()=>{
 const charge=publicData.cards.find(c=>c.id==='guide-no-charge'),station=publicData.cards.find(c=>c.id==='guide-station-recognition');assert.ok(charge);assert.ok(station);
 assert.equal(resolveCard(charge,{model:'LUBA 1'}).kind,'repair');assert.equal(resolveCard(station,{model:'LUBA 1'}).kind,'scope_required');
 for(const id of ['SYM-003','SYM-005','SYM-008','SYM-012','SYM-014','SYM-016','SYM-017','SYM-018','SYM-019','SYM-021','SYM-022','SYM-024'])assert.equal(resolveSymptom(publicData,id,{model:'LUBA 2'}).kind,'escalate',id);
});
test('stable promotion keeps original source private and exposes no speculative downstream board chain',()=>{
 assert.equal(guideCards().length,10);
 const text=JSON.stringify(publicData);assert.doesNotMatch(text,/REP-[A-Z0-9]+-\d{3}|candidate_refs|publication_scope|repeated_use_signal|STABILITY_SUPPORTED/);
 for(const card of guideCards()){const body=card.paths[0].action.join(' ');assert.doesNotMatch(body,/then replace (the )?mainboard|then replace (the )?driver board|1\.30\.29\.19/i);assert.match(card.paths[0].ifNotFixed.message,/PIE/);}
});
