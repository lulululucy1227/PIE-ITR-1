import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {projectAgentCatalog} from '../src/engine.mjs';
import {enrichKnowledge} from '../lib/reuse.mjs';
import {projectHardwareSupport} from '../lib/hardware-support.mjs';
const read=name=>JSON.parse(fs.readFileSync(new URL('../data/'+name,import.meta.url)));
const audit=read('hardware-top10-audit.json'),raw=read('canonical.json');
const catalog=projectAgentCatalog(enrichKnowledge(raw,read('reuse-manifest.json'),read('reuse-snapshot.json')));
catalog.knowledgeVersion='2026-09-16-hardware-top10.1';
const support=projectHardwareSupport(read('hardware-step-support.json'),catalog);
test('hardware priorities are a source-bounded non-frequency selection with explicit incomplete window',()=>{
 assert.equal(audit.ranking.method,'priority-based');assert.equal(audit.ranking.frequencyCountsAvailable,false);
 assert.equal(audit.evidenceWindow.populationComplete,false);assert.equal(audit.evidenceWindow.requested90DayWindowSupported,false);
 assert.equal(audit.evidenceWindow.start,'2026-08-18');assert.equal(audit.evidenceWindow.end,'2026-08-21');
 assert.equal(audit.evidenceWindow.technicalReferencesAsOf,'2026-09-14');
 assert.equal(audit.selected.length+audit.excluded.length,audit.ranking.candidateCount);
 assert.equal(audit.selected.length,10);assert.deepEqual(audit.selected.map(x=>x.rank),[1,2,3,4,5,6,7,8,9,10]);
 for(const item of audit.selected){
  for(const key of ['symptom','solution','verification','fallback','hardwareDomain','rationale'])assert.ok(item[key]?.trim(),item.id+key);
  assert.equal(item.frequency,null);assert.equal(item.newPublicRepairPath,false);
  assert.ok(!item.existingCards.includes('guide-update-failure'));
  for(const field of ['part','sku','qty','tool','toolUsage','disassembly','expectedResult','verification','fallback'])assert.ok(item.fieldAudit[field]?.classification,item.id+field);
  for(const ref of item.sourceRefs)assert.ok(audit.sourceManifest.some(s=>s.id===ref.sourceId&&s.section.sha256===ref.sectionSha256));
 }
 assert.equal(audit.selected.filter(x=>x.publicationStatus==='PIE_ONLY').length,2);
});
test('published additions enrich existing hardware actions only and excluded identifiers never leak',()=>{
 assert.equal(new Set(support.map(r=>r.binding.cardId)).size,9);
 assert.ok(support.length>0);assert.ok(!support.some(r=>r.kind==='parts'||r.kind==='disassembly'));
 for(const r of support)assert.ok(audit.selected.some(x=>x.publicationStatus==='GUIDED'&&x.existingCards.includes(r.binding.cardId)));
 for(const s of audit.sourceManifest){assert.match(s.sha256Before,/^[a-f0-9]{64}$/);assert.equal(s.sha256Before,s.sha256After);}
 const publicText=JSON.stringify({catalog,support});
 assert.doesNotMatch(publicText,/hardware-top10-audit|sourceResolution|sourceRefs|sourceSha256|PRIVATE_ONLY|C\.P\.SH\.000184000|C\.P\.XS\.000121005|ticket_assist|NFF/);
 assert.equal(catalog.cards.find(c=>c.id==='ec-5501').paths.every(p=>p.kind==='escalate'),true);
 assert.equal(catalog.cards.find(c=>c.id==='ec-1202').paths.some(p=>p.kind==='repair'),false);
 assert.ok(!support.some(r=>['ec-1202','ec-5501'].includes(r.binding.cardId)));
});
