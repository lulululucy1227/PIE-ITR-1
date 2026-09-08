// Build-time/private only. This module and its data are not public assets.
import crypto from 'node:crypto';
import {isDeepStrictEqual} from 'node:util';
import {projectAgentCatalog} from '../src/engine.mjs';

export const CANDIDATE_IDS=Object.freeze(['REP-WHEEL-001','REP-WHEEL-003','REP-CUT-001','REP-CUT-002','REP-CHARGE-001','REP-CHARGE-002','REP-DOCK-001','REP-POWER-001','REP-POWER-002','REP-POS-001','REP-RTK-001','REP-WIFI-001','REP-BT-001','REP-BUMP-001','REP-LIDAR-001','REP-WATER-001','REP-CABLE-001','REP-PHY-001','REP-FW-001']);
export const PAYLOAD_PATH='docs/troubleshooter/FEISHU_CANDIDATE_PAYLOAD_2026-09-08.md';
const STATES=['VERIFIED_RESOLUTION','STABLE_OPERATIONAL_GUIDANCE','ACTION_PERFORMED_OUTCOME_UNKNOWN','SOURCE_RECOMMENDATION','CONFLICTING_EVIDENCE'];
const VISIBILITY=['AGENT_GUIDED','AGENT_SELF_SERVICE','PIE_ONLY','WITHHELD'];
const text=v=>typeof v==='string'&&v.trim().length>0;
const texts=v=>Array.isArray(v)&&v.every(text);
const normalized=value=>String(value).replace(/^\uFEFF/,'').replace(/\r\n?/g,'\n');
export const payloadDigest=value=>crypto.createHash('sha256').update(normalized(value)).digest('hex');
const unquote=value=>value.replace(/^`(.*)`$/,'$1');

export function parseCandidatePayload(markdown){
 const input=normalized(markdown),candidates=[],frozen=[],seen=new Set();
 const fields={'candidate priority':'priority','candidate scope':'scope','target part/domain':'target','canonical verification candidate':'verification','verification candidate':'verification','fallback candidate':'fallback','Feishu evidence label':'evidence_label','publication':'publication','Error Code':'error_code','status':'status','agent-facing hardware repair publication':'hardware_publication','allowed':'allowed','prohibited':'prohibited'};
 for(const section of input.split(/^### /m).slice(1)){
  const block=section.split(/^## /m)[0],lines=block.trim().split('\n'),id=lines.shift().trim();
  if(!/^REP-[A-Z0-9]+-\d{3}$/.test(id))throw new Error('Invalid candidate heading: '+id);
  if(seen.has(id))throw new Error('Duplicate candidate: '+id);seen.add(id);
  const record={repair_path_id:id,symptom_ids:[],source:{priority:null,scope:null,target:null,action:[],verification:null,fallback:null,evidence_label:null,publication:null,guardrails:[],error_code:null,status:null,hardware_publication:null,allowed:null,prohibited:null}};
  const keys=new Set();let lastKey=null;
  for(const line of lines){
   if(!line.trim())continue;
   const bullet=line.match(/^- ([^:]+):\s*(.*)$/);
   if(bullet){const [,key,value]=bullet;if(keys.has(key))throw new Error('Duplicate field '+key);keys.add(key);lastKey=key;
    if(['symptom','symptoms'].includes(key))record.symptom_ids=[...value.matchAll(/`(SYM-\d{3})`/g)].map(m=>m[1]);
    else if(key==='candidate action'){if(value)record.source.action.push(value);}
    else if(['guardrail','scope guardrail'].includes(key))record.source.guardrails.push(value);
    else if(Object.hasOwn(fields,key))record.source[fields[key]]=unquote(value);
    else throw new Error('Unknown field '+key+' in '+id);
   }else{const numbered=line.match(/^\s+\d+\.\s+(.+)$/);if(lastKey!=='candidate action'||!numbered)throw new Error('Unsupported payload line in '+id);record.source.action.push(numbered[1]);}
  }
  (id==='REP-1202-001'?frozen:candidates).push(record);
 }
 const errorSection=input.split('## Reconciliation-only sync-derived Error candidates')[1]?.split(/^## /m)[0]||'';
 const error_reconciliation=errorSection.split('\n').filter(line=>line.startsWith('- `')).map(line=>({codes:[...new Set([...line.matchAll(/`([-+]?\d+)`/g)].map(m=>m[1]))],statement:line.slice(2),publication:'RECONCILIATION_ONLY'}));
 return {candidates,frozen,error_reconciliation};
}

export function validateCandidates(input,canonical,{payloadText}={}){
 const errors=[],fail=(id,message)=>errors.push(id+': '+message);
 if(input?.schemaVersion!==1||!Array.isArray(input?.candidates)||!Array.isArray(input?.frozen)||!Array.isArray(input?.error_reconciliation))return ['Invalid private candidate catalog'];
 if(input.source?.kind!=='sanitized_supervisor_payload'||input.source?.path!==PAYLOAD_PATH||input.source?.productionRead!==false||input.source?.productionWrite!==false||!/^([a-f0-9]{64})$/.test(input.source?.sha256||''))fail('source','provenance');
 const all=[...input.candidates,...input.frozen];
 if(!isDeepStrictEqual(input.candidates.map(p=>p?.repair_path_id),CANDIDATE_IDS)||input.frozen.length!==1||input.frozen[0]?.repair_path_id!=='REP-1202-001')fail('catalog','expected exact19 candidate IDs plus frozen1202');
 let parsed=null;
 if(typeof payloadText!=='string')fail('source','payload text required for source parity');
 else{try{parsed=parseCandidatePayload(payloadText);if(payloadDigest(payloadText)!==input.source?.sha256)fail('source','hash mismatch');}catch(error){fail('source',error.message);}}
 if(parsed){
  for(const key of ['candidates','frozen','error_reconciliation']){
   const originals=input[key].map(record=>{if(!record||typeof record!=='object')return record;const {review,...source}=record;return source;});
   if(!isDeepStrictEqual(originals,parsed[key]))fail(key,'source content drift');
  }
 }
 const symptoms=Array.isArray(canonical?.symptoms)?canonical.symptoms:[];
 let projected=null;try{projected=projectAgentCatalog(canonical);}catch{fail('canonical','invalid canonical catalog');}
 for(const record of all){
  const id=record?.repair_path_id||'unknown';
  if(!texts(record?.symptom_ids)||!record.symptom_ids.length||record.symptom_ids.some(s=>!symptoms.some(x=>x.symptom_id===s)))fail(id,'invalid symptom references');
  const frozen=id==='REP-1202-001',s=record?.source,r=record?.review;
  if(!s||!texts(s.action)||(!frozen&&(!s.action.length||!text(s.scope)||!text(s.target)||!text(s.verification)||!text(s.fallback)||!STATES.includes(s.evidence_label))))fail(id,'source fields');
  if(!r||!STATES.includes(r.evidence_state)||!VISIBILITY.includes(r.visibility)||!text(r.rationale)||!texts(r.source_refs)||!r.source_refs.length||!/^\d{4}-\d{2}-\d{2}$/.test(r.last_reviewed||'')||!Array.isArray(r.promoted_refs)||!texts(r.known_conflicts_or_reopens)) {fail(id,'review fields');continue;}
  for(const field of ['scope_confirmed','verification_confirmed','fallback_confirmed','active_maintenance'])if(typeof r[field]!=='boolean')fail(id,'review '+field);
  for(const field of ['first_seen','last_material_change','repeated_use_signal','superseded_by'])if(!(r[field]===null||text(r[field])))fail(id,'review '+field);
  if(frozen&&(r.visibility!=='WITHHELD'||r.evidence_state!=='CONFLICTING_EVIDENCE'||r.promoted_refs.length||s?.hardware_publication!=='FROZEN'||s?.action?.length))fail(id,'1202 must remain frozen metadata');
  if(r.visibility==='AGENT_GUIDED'||r.visibility==='AGENT_SELF_SERVICE'){
   if(!['VERIFIED_RESOLUTION','STABLE_OPERATIONAL_GUIDANCE'].includes(r.evidence_state)||r.scope_confirmed!==true||r.verification_confirmed!==true||r.fallback_confirmed!==true||r.known_conflicts_or_reopens.length||r.superseded_by||!r.promoted_refs.length)fail(id,'promotion prerequisites');
   if(r.evidence_state==='STABLE_OPERATIONAL_GUIDANCE'&&(!r.active_maintenance||!text(r.repeated_use_signal)))fail(id,'stable operational evidence required');
   for(const ref of r.promoted_refs){
    const card=canonical?.cards?.find(c=>c.id===ref?.card_id),path=card?.paths?.find(p=>p.id===ref?.repair_path_id),publicPath=projected?.cards.find(c=>c.id===ref?.card_id)?.paths.find(p=>p.id===ref?.repair_path_id);
    if(!path?.candidate_refs?.includes(id)||!publicPath||!['repair','check','information'].includes(publicPath.kind))fail(id,'promotion must resolve to independently approved canonical action');
    if(!record.symptom_ids.some(symptom=>symptoms.find(s=>s.symptom_id===symptom)?.repair_refs.some(r=>r.card_id===ref?.card_id&&r.repair_path_id===ref?.repair_path_id)))fail(id,'promotion symptom applicability');
   }
  }else if(r.promoted_refs.length)fail(id,'private record cannot carry published references');
  if(r.evidence_state==='CONFLICTING_EVIDENCE'&&r.visibility!=='WITHHELD')fail(id,'conflict must be withheld');
  for(const symptom of record.symptom_ids||[])if(!symptoms.find(s=>s.symptom_id===symptom)?.candidate_refs?.includes(id))fail(id,'missing private symptom crosswalk');
 }
 for(const symptom of symptoms){
  if(!texts(symptom.candidate_refs||[])) {fail(symptom.symptom_id,'candidate_refs');continue;}
  if(new Set(symptom.candidate_refs||[]).size!==(symptom.candidate_refs||[]).length)fail(symptom.symptom_id,'duplicate candidate_refs');
  for(const id of symptom.candidate_refs||[])if(!all.some(r=>r?.repair_path_id===id&&r?.symptom_ids?.includes(symptom.symptom_id)))fail(symptom.symptom_id,'dangling private candidate reference');
 }
 for(const card of canonical?.cards||[])for(const path of card.paths||[]){
  if(path.candidate_refs===undefined)continue;
  const key=card.id+'/'+path.id,refs=path.candidate_refs;
  if(!texts(refs)||new Set(refs).size!==refs.length){fail(key,'invalid or duplicate candidate provenance');continue;}
  const publicPath=projected?.cards.find(c=>c.id===card.id)?.paths.find(p=>p.id===path.id);
  for(const id of refs){
   const candidate=all.find(r=>r?.repair_path_id===id);
   if(!candidate){fail(key,'dangling candidate provenance');continue;}
   if(!['repair','check','information'].includes(publicPath?.kind))continue;
   const review=candidate.review;
   if(!['AGENT_GUIDED','AGENT_SELF_SERVICE'].includes(review?.visibility)||!review?.promoted_refs?.some(ref=>ref?.card_id===card.id&&ref?.repair_path_id===path.id))fail(key,'published action requires reciprocal promoted candidate');
   if(!Array.isArray(candidate.symptom_ids)||!candidate.symptom_ids.some(id=>symptoms.find(s=>s.symptom_id===id)?.repair_refs?.some(ref=>ref.card_id===card.id&&ref.repair_path_id===path.id)))fail(key,'candidate provenance symptom applicability');
  }
 }
 for(const item of input.error_reconciliation){
  if(!item?.review||!STATES.includes(item.review.evidence_state)||!['PIE_ONLY','WITHHELD'].includes(item.review.visibility)||!text(item.review.rationale)||item.publication!=='RECONCILIATION_ONLY')fail('sync error','review required; not a repair approval');
 }
 return errors;
}

export function candidateCounts(input){
 const tally=(records,key)=>records.reduce((out,p)=>{const value=p.review[key];out[value]=(out[value]||0)+1;return out;},{});
 return {imported:input.candidates.length,frozen:input.frozen.length,promoted:input.candidates.filter(p=>['AGENT_GUIDED','AGENT_SELF_SERVICE'].includes(p.review.visibility)).length,visibility:tally(input.candidates,'visibility'),evidence:tally(input.candidates,'evidence_state'),frozenVisibility:tally(input.frozen,'visibility')};
}
