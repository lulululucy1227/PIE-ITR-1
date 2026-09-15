import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {projectAgentCatalog} from '../src/engine.mjs';
const catalog=JSON.parse(fs.readFileSync(new URL('../data/canonical.json',import.meta.url)));
const published=projectAgentCatalog(catalog);
test('current repair completion includes post-final-test logs without exposing internal closure policy',()=>{
 for(const card of published.cards)for(const p of card.paths)if(p.kind==='repair'){
  assert.match(p.verification.steps.join(' '),/fresh logs.*final test/i,card.id);
  assert.doesNotMatch(p.verification.steps.join(' '),/NFF|case number|Repair Completed - Passed/);
  assert.doesNotMatch(catalog.cards.find(c=>c.id===card.id).paths.find(x=>x.id===p.id).verification.canonical.join(' '),/ultrasonic failure alone is not a blocker/);
 }
});
test('Burn-in is conditional on actual relevant repair and charging station/contact exceptions remain explicit',()=>{
 for(const id of ['guide-wheel-movement','guide-cutting-operation','guide-power'])assert.match(published.cards.find(c=>c.id===id).paths[0].verification.steps.join(' '),/after.*repair.*Burn-in/i,id);
 for(const id of ['guide-no-charge','guide-station-recognition']){
  const body=published.cards.find(c=>c.id===id).paths[0].verification.steps.join(' ');
  assert.match(body,/power-adapter repair/);assert.match(body,/station.*contact.*does not require Burn-in/i);
 }
 for(const id of ['guide-docking','guide-bumper','guide-update-failure','sym-cutting-functional-test'])assert.doesNotMatch(published.cards.find(c=>c.id===id).paths[0].verification.steps.join(' '),/Burn-in/);
});
