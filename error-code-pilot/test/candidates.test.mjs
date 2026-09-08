import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {parseCandidatePayload,validateCandidates,payloadDigest,CANDIDATE_IDS} from '../lib/candidates.mjs';
import {projectAgentCatalog,resolveSymptom} from '../src/engine.mjs';
const payload=fs.readFileSync(new URL('../../docs/troubleshooter/FEISHU_CANDIDATE_PAYLOAD_2026-09-08.md',import.meta.url),'utf8');
const canonical=JSON.parse(fs.readFileSync(new URL('../data/canonical.json',import.meta.url)));
const read=()=>JSON.parse(fs.readFileSync(new URL('../data/feishu-candidates.json',import.meta.url)));

test('actual sanitized payload imports exactly19stable IDs plus separately frozen1202',()=>{
 const parsed=parseCandidatePayload(payload);
 assert.equal(parsed.candidates.length,19);assert.deepEqual(parsed.candidates.map(p=>p.repair_path_id),CANDIDATE_IDS);
 assert.deepEqual(parsed.frozen.map(p=>p.repair_path_id),['REP-1202-001']);
 assert.equal(parsed.candidates.flatMap(p=>p.symptom_ids).length,25);
 assert.equal(new Set(parsed.candidates.flatMap(p=>p.symptom_ids)).size,25);
});
test('source fields and limits remain exact; frozen missing repair facts are not fabricated',()=>{
 const parsed=parseCandidatePayload(payload),wheel=parsed.candidates[0].source;
 assert.deepEqual(wheel.action,['Run Motor Test in MammoSuite.','If the motor fails, replace the wheel hub motor.','If the motor is OK, replace the driver board.']);
 assert.equal(wheel.evidence_label,'ACTION_PERFORMED_OUTCOME_UNKNOWN');
 assert.equal(parsed.candidates.find(p=>p.repair_path_id==='REP-CHARGE-001').source.scope,'LUBA 1 / LUBA 2 / LUBA 2X / LUBA 3 for `SYM-007`; LUBA 2 / 2X / 3 for `SYM-009`');
 const frozen=parsed.frozen[0];assert.equal(frozen.source.error_code,'1202');assert.equal(frozen.source.hardware_publication,'FROZEN');
 for(const field of ['scope','target','verification','fallback','evidence_label'])assert.equal(frozen.source[field],null,field);
 assert.deepEqual(frozen.source.action,[]);
});
test('sync error claims are reconciliation-only and signed identities are preserved',()=>{
 const parsed=parseCandidatePayload(payload);assert.deepEqual(parsed.error_reconciliation.map(e=>e.codes),[['2401','2407'],['2000303','-2000303'],['1000022'],['1420'],['1500']]);
 assert.ok(parsed.error_reconciliation.every(e=>e.publication==='RECONCILIATION_ONLY'));
 assert.ok(parsed.error_reconciliation[1].statement.includes('false alarm'));
});
test('import is reproducible across newline convention and fails on duplicate or unknown fields',()=>{
 assert.deepEqual(parseCandidatePayload(payload),parseCandidatePayload(payload.replace(/\r?\n/g,'\r\n')));
 assert.equal(payloadDigest(payload),payloadDigest(payload.replace(/\r?\n/g,'\r\n')));
 assert.throws(()=>parseCandidatePayload(payload.replace('### REP-WHEEL-003','### REP-WHEEL-001')),/duplicate/i);
 assert.throws(()=>parseCandidatePayload(payload.replace('- candidate priority: P0','- invented field: P0')),/unknown field/i);
});
test('all imported records retain exact source fields and independent per-record reviewed decisions',()=>{
 const input=read();assert.deepEqual(validateCandidates(input,canonical,{payloadText:payload}),[]);
 const parsed=parseCandidatePayload(payload);
 assert.deepEqual(input.candidates.map(({review,...source})=>source),parsed.candidates);
 assert.deepEqual(input.frozen.map(({review,...source})=>source),parsed.frozen);
 assert.deepEqual(input.error_reconciliation.map(({review,...source})=>source),parsed.error_reconciliation);
 for(const record of [...input.candidates,...input.frozen]){assert.ok(record.review.rationale.length>30);assert.equal(record.review.first_seen,null);if(record.review.evidence_state==='STABLE_OPERATIONAL_GUIDANCE')assert.match(record.review.repeated_use_signal,/supervisor/);else assert.equal(record.review.repeated_use_signal,null);}
});
test('candidate validation rejects orphan IDs, missing records, review defects and source drift',()=>{
 for(const mutate of [
  c=>c.candidates.pop(),c=>c.candidates[0].symptom_ids=['SYM-999'],c=>c.candidates[0].repair_path_id='REP-FAKE-001',
  c=>c.candidates[0].source.action=[],c=>c.candidates[0].review.evidence_state='P0',c=>c.candidates[0].review.rationale='',
  c=>c.source.sha256='bad',c=>c.candidates[0].source.scope='ALL',c=>c.frozen[0].review.visibility='AGENT_GUIDED'
 ]){const data=read();mutate(data);assert.ok(validateCandidates(data,canonical,{payloadText:payload}).length);}
});
test('P0 and publication flags cannot promote weak candidates or link to unrelated existing repair',()=>{
 for(const id of ['REP-WHEEL-001','REP-FW-001','REP-1202-001']){
  const input=read();const record=[...input.candidates,...input.frozen].find(p=>p.repair_path_id===id);
  record.review.visibility='AGENT_GUIDED';record.review.promoted_refs=[{card_id:'sym-cutting-functional-test',repair_path_id:'software'}];
  assert.ok(validateCandidates(input,canonical,{payloadText:payload}).length);
 }
});
test('private symptom crosswalk cannot leak candidate actions or replace approved card routing',()=>{
 const data=read(),publicData=projectAgentCatalog(canonical);const publicText=JSON.stringify(publicData);
 for(const id of [...CANDIDATE_IDS,'REP-1202-001'])assert.equal(publicText.includes(id),false,id);
 for(const key of ['candidate_refs','source_fields','feishu','repeated_use_signal'])assert.equal(publicText.includes(key),false,key);
 const refs=canonical.symptoms.flatMap(s=>s.candidate_refs||[]);assert.equal(new Set(refs).size,20);
 assert.equal(resolveSymptom(publicData,'SYM-008').kind,'escalate');
 for(const s of canonical.symptoms.slice(25))assert.equal(resolveSymptom(canonical,s.symptom_id).kind,'escalate');
 assert.equal(data.frozen[0].review.evidence_state,'CONFLICTING_EVIDENCE');
 assert.equal(publicData.cards.filter(c=>c.paths.some(p=>p.kind==='repair')).length,8);
});

test('canonical action provenance cannot point at private, dangling or nonreciprocal candidates',()=>{
 for(const refs of [['REP-CUT-001'],['REP-FAKE-001'],['REP-FW-001'],['REP-CUT-001','REP-CUT-001'],'REP-CUT-001']){
  const changed=structuredClone(canonical);
  changed.cards.find(c=>c.id==='sym-cutting-functional-test').paths[0].candidate_refs=refs;
  assert.ok(validateCandidates(read(),changed,{payloadText:payload}).length,JSON.stringify(refs));
 }
});
