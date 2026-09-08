import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as engine from '../src/engine.mjs';
const canonical=JSON.parse(fs.readFileSync(new URL('../data/canonical.json',import.meta.url)));
const catalog=engine.projectAgentCatalog(canonical);
test('controlled model inventory contains only explicit knowledge model identities',()=>{
 assert.equal(typeof engine.controlledModels,'function');
 assert.deepEqual(engine.controlledModels(catalog),['LUBA 1','LUBA 2','LUBA 2 5000X','LUBA 2X','LUBA 3','LUBA mini 2 1000 Vision']);
});
test('symptoms are filtered by exact supported model and observable area without hiding unscoped PIE intake',()=>{
 assert.equal(typeof engine.controlledSymptoms,'function');
 const ids=(model,area)=>engine.controlledSymptoms(catalog,{model,area}).map(s=>s.symptom_id);
 assert.deepEqual(ids('LUBA 1','Charging'),['SYM-007','SYM-008']);
 assert.deepEqual(ids('LUBA 2','Charging'),['SYM-007','SYM-008','SYM-009']);
 assert.deepEqual(ids('LUBA 2 5000X','Cutting'),['SYM-004','SYM-005']);
 assert.deepEqual(ids('Invented model','Cutting'),[]);assert.deepEqual(ids('LUBA 2','Invented area'),[]);
 assert.deepEqual(ids('LUBA 2','Physical'),['SYM-022','SYM-023','SYM-024']);
});
test('only current allowed symptom IDs or explicit Other validate, never injected or cross-area identifiers',()=>{
 assert.equal(typeof engine.validControlledSelection,'function');
 const good={model:'LUBA 2',area:'Movement',symptomId:'SYM-001'};
 assert.equal(engine.validControlledSelection(catalog,good),true);
 for(const change of [{model:''},{model:'unlisted'},{area:'Charging'},{symptomId:'SYM-999'},{symptomId:'SYM-026'},{symptomId:'One wheel does not move'}])assert.equal(engine.validControlledSelection(catalog,{...good,...change}),false);
 assert.equal(engine.validControlledSelection(catalog,{...good,symptomId:'__other__'}),true);
 assert.equal(engine.validControlledSelection(catalog,{...good,model:'unlisted',symptomId:'__other__'}),false);
});
test('condition choices retain only existing references applicable to the exact selected model',()=>{
 assert.equal(typeof engine.controlledReferences,'function');
 assert.deepEqual(engine.controlledReferences(catalog,{model:'LUBA 2',area:'Cutting',symptomId:'SYM-004'}),[{card_id:'guide-cutting-operation',repair_path_id:'guided'}]);
 assert.deepEqual(engine.controlledReferences(catalog,{model:'LUBA 2 5000X',area:'Cutting',symptomId:'SYM-004'}),[{card_id:'sym-cutting-functional-test',repair_path_id:'software'}]);
 assert.deepEqual(engine.controlledReferences(catalog,{model:'LUBA 1',area:'Charging',symptomId:'SYM-009'}),[]);
});
test('unknown scope cannot become a model-wildcard repair through selection filtering',()=>{
 const copy=structuredClone(catalog),card=copy.cards.find(c=>c.id==='guide-no-charge');card.scope={status:'unknown',models:[],firmware:[]};
 assert.equal(engine.controlledSymptoms(copy,{model:'LUBA 2',area:'Charging'}).some(s=>s.symptom_id==='SYM-007'),false);
});
test('repair authorization binds the exact referenced path, permitting only completed non-direct follow-ups',()=>{
 assert.equal(typeof engine.controlledRepairAllowed,'function');
 const copy=structuredClone(catalog),card=copy.cards.find(c=>c.id==='guide-no-charge'),first=card.paths[0];
 const next={...structuredClone(first),id:'followup',directSelectable:false};
 const unrelated={...structuredClone(first),id:'unrelated',directSelectable:true};card.paths.push(next,unrelated);first.ifNotFixed={kind:'path',pathId:'followup',message:'Continue'};
 const fields={model:'LUBA 2',area:'Charging',symptomId:'SYM-007'};
 assert.equal(engine.controlledRepairAllowed(copy,fields,card.id,'guided',[]),true);
 assert.equal(engine.controlledRepairAllowed(copy,fields,card.id,'unrelated',[]),false);
 assert.equal(engine.controlledRepairAllowed(copy,fields,card.id,'followup',[]),false);
 assert.equal(engine.controlledRepairAllowed(copy,fields,card.id,'followup',['guided']),true);
 assert.equal(engine.controlledRepairAllowed(copy,{...fields,symptomId:'__other__'},card.id,'followup',['guided']),false);
});
