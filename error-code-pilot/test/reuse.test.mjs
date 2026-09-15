import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {enrichKnowledge,validateReuse,reuseCounts,snapshotDigest} from '../lib/reuse.mjs';
import {projectAgentCatalog,resolveCard} from '../src/engine.mjs';
const read=name=>JSON.parse(fs.readFileSync(new URL('../data/'+name,import.meta.url),'utf8'));
const canonical=read('canonical.json'),manifest=read('reuse-manifest.json'),snapshot=read('reuse-snapshot.json');
const copy=x=>structuredClone(x);

test('reviewed minimal snapshot covers all five source families and seven disposition classes',()=>{
 assert.deepEqual(validateReuse(manifest,snapshot,canonical),[]);
 assert.equal(manifest.sources.length,11);
 assert.equal(snapshotDigest(snapshot),manifest.snapshotSha256);
 assert.deepEqual(Object.keys(reuseCounts(snapshot).classes).sort(),['PUBLIC_REPAIR_FACT','PUBLIC_TOOL_STEP','PUBLIC_PART_FACT','PRIVATE_INTERNAL','NEEDS_SCOPE_REVIEW','CONFLICT','DUPLICATE'].sort());
 assert.equal(reuseCounts(snapshot).published,5);
});

test('build enrichment gives actionable checks only to existing mature scoped paths',()=>{
 const before=copy(canonical),enriched=enrichKnowledge(canonical,manifest,snapshot),published=projectAgentCatalog(enriched);
 assert.deepEqual(canonical,before,'never mutate the canonical knowledge or source');
 assert.equal(published.knowledgeVersion,'2026-09-15-simple-knowledge-reuse.1');
 assert.equal(published.cards.length,31);assert.equal(published.symptoms.length,25);
 const charge=published.cards.find(c=>c.id==='guide-no-charge');
 assert.match(charge.paths[0].action[0],/one component at a time/);
 const cable=published.cards.find(c=>c.id==='guide-visible-cable-damage');
 assert.match(cable.paths[0].action[0],/SBOM/);
 assert.equal(resolveCard(charge,{model:'YUKA'}).kind,'scope_required');
 for(const c of enriched.cards){const original=canonical.cards.find(x=>x.id===c.id);assert.deepEqual(c.scope,original.scope);assert.equal(c.paths.length,original.paths.length);for(const p of c.paths){const prior=original.paths.find(x=>x.id===p.id);assert.deepEqual(p.ifNotFixed,prior.ifNotFixed);assert.equal(p.kind,prior.kind);assert.equal(p.part,prior.part);assert.equal(p.qualifier,prior.qualifier);}}
});

test('1202, PIE-only, positioning, WIFI, water and software correction remain byte-equivalent',()=>{
 const enriched=enrichKnowledge(canonical,manifest,snapshot);
 const allowed=new Set(['guide-no-charge','guide-bumper','guide-update-failure','guide-visible-cable-damage','guide-power']);
 for(const card of canonical.cards)if(!allowed.has(card.id))assert.deepEqual(enriched.cards.find(c=>c.id===card.id),card,card.id);
});

test('public projection contains selected advice and no private sources, identifiers, review or SKU content',()=>{
 const output=JSON.stringify(projectAgentCatalog(enrichKnowledge(canonical,manifest,snapshot)));
 assert.doesNotMatch(output,/reuse-|snapshotSha256|sourceSha256|ticket_assist|source_file|PRIVATE_INTERNAL|C\.P\.SH\.|W\.D\.XC\.|password|api.token|[A-Z]:[\\/]/i);
 for(const entry of snapshot.entries.filter(e=>!e.publication))assert.ok(!output.includes(entry.id));
});

test('tampered snapshot and broken provenance are rejected before publication',()=>{
 const changed=copy(snapshot);changed.entries.find(e=>e.publication).text+=' unreviewed';
 assert.throws(()=>enrichKnowledge(canonical,manifest,changed),/snapshot digest/);
 const broken=copy(manifest);broken.sources[0].sha256='bad';
 assert.throws(()=>enrichKnowledge(canonical,broken,snapshot),/source hash|source provenance/);
});

test('unreviewed publication, unknown target and unresolved conflicts fail closed',()=>{
 for(const mutation of [e=>{e.classification='CONFLICT';},e=>{e.review.scopeConfirmed=false;},e=>{e.publication.cardId='ec-1202';},e=>{e.publication.field='part';}]){
  const changed=copy(snapshot);mutation(changed.entries.find(e=>e.publication));const m=copy(manifest);m.snapshotSha256=snapshotDigest(changed);
  assert.throws(()=>enrichKnowledge(canonical,m,changed),/publication|review|allowlist/);
 }
});

test('withdrawn or differently scoped canonical target cannot inherit approved advice',()=>{
 for(const mutation of [c=>{c.publication='withheld';},c=>{c.scope.models.push('YUKA');},c=>{c.paths[0].review.noContradiction=false;}]){
  const changed=copy(canonical);mutation(changed.cards.find(c=>c.id==='guide-no-charge'));
  assert.throws(()=>enrichKnowledge(changed,manifest,snapshot),/target|scope/);
 }
});

test('a changed canonical instruction requires a new reuse review instead of silently being overwritten',()=>{
 const changed=copy(canonical);
 changed.cards.find(c=>c.id==='guide-no-charge').paths[0].action[0]='A newly reviewed charging instruction.';
 assert.throws(()=>enrichKnowledge(changed,manifest,snapshot),/target instruction changed/);
});
