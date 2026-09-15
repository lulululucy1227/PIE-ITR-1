import crypto from 'node:crypto';
import {projectAgentCatalog} from '../src/engine.mjs';

export const REUSE_CLASSES=Object.freeze(['PUBLIC_REPAIR_FACT','PUBLIC_TOOL_STEP','PUBLIC_PART_FACT','PRIVATE_INTERNAL','NEEDS_SCOPE_REVIEW','CONFLICT','DUPLICATE']);
const targets=Object.freeze({
 'reuse-charge-comparison':['guide-no-charge','guided',0,['LUBA 1','LUBA 2','LUBA 2X','LUBA 3'],'f76dff25714050980cc65dca54e0fc85972a78eb9b64cb7901c6fe6da4779d02'],
 'reuse-bumper-crosscheck':['guide-bumper','guided',1,['LUBA 2','LUBA 2X','LUBA 3'],'45349866ce7f1ab3f07f72cab06cf2f80588425980ee0020933f8734de7f7078'],
 'reuse-cable-part-check':['guide-visible-cable-damage','guided',0,['LUBA 2','LUBA 2X','LUBA 3'],'7c63983eba29efb63c34afc200fdcda47c536af65d1fd171998f42a0a915a6d1'],
 'reuse-power-observation':['guide-power','guided',0,['LUBA 2','LUBA 2X','LUBA 3'],'63c92dc39fb8dbb0e2defc43da2f0649adb2ef2ecb772557c29affb5c4a6b1fa'],
 'reuse-update-evidence':['guide-update-failure','guided',0,['LUBA 2','LUBA 2X','LUBA 3'],'82bc2313e868b7c3f0cc85c3153c728520a6110fa5de2a8addbb402f967d6257']
});
const digest=value=>crypto.createHash('sha256').update(value).digest('hex');
export const snapshotDigest=snapshot=>digest(JSON.stringify(snapshot));
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const text=value=>typeof value==='string'&&value.trim().length>0;
const sha=value=>typeof value==='string'&&/^[a-f0-9]{64}$/.test(value);
const forbidden=/password|api[_ -]?key|access[_ -]?token|bearer\s|https?:\/\/|[a-z]:[\\/]|[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}|\b(?:C\.P\.|W\.D\.|W\.Z\.)/i;

export function reuseCounts(snapshot) {
 const classes=Object.fromEntries(REUSE_CLASSES.map(k=>[k,0]));
 for(const e of snapshot.entries||[])if(Object.hasOwn(classes,e.classification))classes[e.classification]++;
 return {reviewed:snapshot.entries.length,published:snapshot.entries.filter(e=>e.publication).length,classes};
}

export function validateReuse(manifest,snapshot,catalog) {
 const errors=[];
 if(manifest?.schemaVersion!==1||snapshot?.schemaVersion!==1||!Array.isArray(manifest.sources)||!Array.isArray(snapshot.entries))return ['Invalid reuse header'];
 if(manifest.snapshotSha256!==snapshotDigest(snapshot))errors.push('Reuse snapshot digest mismatch');
 const sources=new Map(),ids=new Set(),slots=new Set();
 for(const source of manifest.sources){
  if(!text(source.id)||sources.has(source.id)||!sha(source.sha256)||!text(source.file)||!manifest.roots?.some(r=>r.id===source.root))errors.push('Invalid reuse source hash/identity');
  sources.set(source.id,source);
 }
 let publicCatalog;
 try{publicCatalog=projectAgentCatalog(catalog);}catch(error){return [...errors,error.message];}
 for(const e of snapshot.entries){
  if(!text(e.id)||ids.has(e.id)||!REUSE_CLASSES.includes(e.classification)||!text(e.text))errors.push('Invalid reuse entry');
  ids.add(e.id);
  if(!Array.isArray(e.sources)||!e.sources.length||e.sources.some(s=>sources.get(s.sourceId)?.sha256!==s.sha256||!text(s.section)))errors.push(e.id+': source provenance mismatch');
  if(!e.publication)continue;
  const p=e.publication,allow=targets[e.id];
  if(!allow||!e.classification.startsWith('PUBLIC_')||p.field!=='action'||p.cardId!==allow[0]||p.pathId!==allow[1]||p.index!==allow[2]||!same(p.models,allow[3])){errors.push(e.id+': publication allowlist mismatch');continue;}
  if(e.review?.approved!==true||e.review?.scopeConfirmed!==true||e.review?.noContradiction!==true||e.review?.evidenceState!=='STABLE_OPERATIONAL_GUIDANCE'||!text(e.review?.authority))errors.push(e.id+': publication review missing');
  if(forbidden.test(e.text)||e.text.length>500)errors.push(e.id+': publication text is not minimal public advice');
  const original=catalog.cards.find(c=>c.id===p.cardId),path=original?.paths.find(x=>x.id===p.pathId),published=publicCatalog.cards.find(c=>c.id===p.cardId)?.paths.find(x=>x.id===p.pathId);
  if(!original||original.lifecycle!=='CURRENT'||original.publication!=='approved'||original.scope.status!=='confirmed'||!same(original.scope.models,p.models)||original.scope.firmware.length||path?.publication!=='approved'||path?.evidence_state!=='STABLE_OPERATIONAL_GUIDANCE'||path?.review?.noContradiction!==true||!['repair','check'].includes(published?.kind)||!text(path.action[p.index]))errors.push(e.id+': target unavailable or scope changed');
  if(text(path?.action?.[p.index])&&digest(path.action[p.index])!==allow[4])errors.push(e.id+': target instruction changed; review reuse again');
  const slot=p.cardId+':'+p.pathId+':'+p.index;
  if(slots.has(slot))errors.push(e.id+': duplicate publication target');
  slots.add(slot);
 }
 return errors;
}

// Build-time only. Browser receives the normal explicit engine projection, never
// source manifests, excluded candidates, review metadata or external paths.
export function enrichKnowledge(catalog,manifest,snapshot) {
 const errors=validateReuse(manifest,snapshot,catalog);
 if(errors.length)throw new Error(errors.join('\n'));
 const result=structuredClone(catalog);
 result.knowledgeVersion='2026-09-15-simple-knowledge-reuse.1';
 for(const e of snapshot.entries.filter(e=>e.publication)){
  const p=e.publication;
  result.cards.find(c=>c.id===p.cardId).paths.find(x=>x.id===p.pathId).action[p.index]=e.text;
 }
 return result;
}
