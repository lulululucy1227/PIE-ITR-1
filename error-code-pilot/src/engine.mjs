const text = value => typeof value === 'string' && value.trim().length > 0;
const strings = value => Array.isArray(value) && value.length > 0 && value.every(text);
const normalize = value => String(value ?? '').normalize('NFKC').replace(/\u2212/g,'-').trim().toLowerCase().replace(/\s+/g,' ');
const visible = card => card.agentVisible === true && !['RETIRED','SUPERSEDED'].includes(card.lifecycle);
const escalate = message => ({kind:'escalate',part:null,action:[message || 'Contact PIE with the exact model, error message, observed symptom and previous repair results.'],verification:null});
const lifecycle = ['CURRENT','HISTORICAL','REVIEW_REQUIRED','SUPERSEDED','RETIRED'];
const classifications = ['SELF_SERVICE_DIRECT','SELF_SERVICE_SYMPTOM_SPLIT','PIE_ONLY','NOT_YET_STABLE','EXCLUDE_FROM_PILOT'];
export const OBSERVABLE_AREAS=Object.freeze(['Movement','Cutting','Charging','Docking','Power','Positioning','Connectivity','Sensors','Physical','Software']);
const evidenceStates=['VERIFIED_RESOLUTION','STABLE_OPERATIONAL_GUIDANCE','ACTION_PERFORMED_OUTCOME_UNKNOWN','SOURCE_RECOMMENDATION','CONFLICTING_EVIDENCE'];
const publicVisibility=['P0_DESKTOP_SELF_SERVICE','P1_DESKTOP_GUIDED'];
const canonicalCard=c=>Object.hasOwn(c,'publication')||Object.hasOwn(c,'evidence');
const v2Card=c=>c.paths.some(p=>Object.hasOwn(p,'evidence_state')||Object.hasOwn(p,'review'));
const approvedCard=c=>visible(c)&&c.publication==='approved'&&!c.supersededBy;
const reservedSymptom=s=>/^SYM-02[678]$/.test(s.symptom_id);
const navigable=s=>!reservedSymptom(s)&&(!Object.hasOwn(s,'agent_visibility')||s.agent_visibility==='NAVIGATION');
const validReview=review=>review&&['scopeConfirmed','repeatedUse','activeMaintenance','noContradiction'].every(k=>typeof review[k]==='boolean')&&text(review.rationale);

function pathEligible(card,path) {
  if(!path||!strings(path.action)||!strings(path.verification?.steps)||!text(path.ifNotFixed?.message)||!['path','escalate'].includes(path.ifNotFixed.kind)) return false;
  if(path.kind==='repair'&&(normalize(card.code)==='1202'||card.scope?.status!=='confirmed'||card.lifecycle!=='CURRENT'||card.supersededBy)) return false;
  if(!canonicalCard(card)) return true;
  if(!approvedCard(card)||!strings(path.verification.canonical)) return false;
  if(!v2Card(card)) return true;
  const allowedVisibility=publicVisibility.includes(path.agent_visibility)||(path.kind==='escalate'&&path.agent_visibility==='PIE_ONLY');
  if(path.publication!=='approved'||!allowedVisibility||path.conflict!==false||path.supersededBy!==null||!evidenceStates.includes(path.evidence_state)||path.evidence_state==='CONFLICTING_EVIDENCE'||!validReview(path.review)) return false;
  if(path.kind!=='repair') return true;
  if(!['VERIFIED_RESOLUTION','STABLE_OPERATIONAL_GUIDANCE'].includes(path.evidence_state)||path.review?.scopeConfirmed!==true||path.review?.noContradiction!==true) return false;
  return path.evidence_state!=='STABLE_OPERATIONAL_GUIDANCE'||(path.review.repeatedUse===true&&path.review.activeMaintenance===true);
}

function safePath(path) {
  return {id:path.id,symptom:'The issue remains after the available checks',directSelectable:path.directSelectable??true,kind:'escalate',part:null,
    action:['Contact PIE to confirm the next action for this symptom and model.'],
    verification:{steps:['Confirm the next action with PIE.']},
    ifNotFixed:{kind:'escalate',message:'Contact PIE; do not repeat an unconfirmed replacement.'}};
}

function publicPath(card,path) {
  if(!pathEligible(card,path)) return safePath(path);
  const next=path.ifNotFixed.kind==='path'?card.paths.find(p=>p.id===path.ifNotFixed.pathId):null;
  const fallback=path.ifNotFixed.kind==='path'&&!pathEligible(card,next)?{kind:'escalate',message:'Contact PIE to confirm the next action.'}:{
    kind:path.ifNotFixed.kind,message:path.ifNotFixed.message,...(next?{pathId:next.id}:{})};
  return {id:path.id,symptom:path.symptom,directSelectable:path.directSelectable??true,kind:path.kind,part:path.part,
    action:[...path.action],verification:{steps:[...path.verification.steps]},ifNotFixed:fallback,...(text(path.qualifier)?{qualifier:path.qualifier}:{})};
}

export function validateCatalog(catalog) {
  const errors=[];
  const fail=(id,message)=>errors.push(id+': '+message);
  if(![1,2].includes(catalog?.schemaVersion) || !text(catalog?.knowledgeVersion) || !Array.isArray(catalog?.cards)) return ['Invalid catalog header'];
  const ids=new Set();
  for(const c of catalog.cards) {
    const id=c?.id || 'unknown';
    if(!text(c?.id)||ids.has(id)) fail(id,'duplicate/missing id');
    ids.add(id);
    if(!(catalog.schemaVersion===2&&c.code===null)&&(!text(c.code)||!/^([-+]?\d+|[A-Z]+-\d+)$/i.test(c.code))) fail(id,'invalid code string');
    if(!text(c.message)||!Array.isArray(c.aliases)||!c.aliases.every(text)) fail(id,'message/aliases');
    if(!classifications.includes(c.classification)||!lifecycle.includes(c.lifecycle)) fail(id,'classification/lifecycle');
    if(!['pilot','candidate','approved','withheld'].includes(c.publication)||typeof c.agentVisible!=='boolean') fail(id,'publication/visibility');
    if(!/^\d{4}-\d{2}-\d{2}$/.test(c.lastReviewed||'')) fail(id,'lastReviewed');
    if(c.lifecycle==='SUPERSEDED'&&!text(c.supersededBy)) fail(id,'supersededBy');
    const s=c.scope;
    if(!s||!['confirmed','unknown','not_required'].includes(s.status)||!Array.isArray(s.models)||!Array.isArray(s.firmware)||!s.models.every(text)||!s.firmware.every(text)) fail(id,'scope');
    else if(s.status==='confirmed'&&!s.models.length) fail(id,'confirmed model scope empty');
    const e=c.evidence;
    if(!e||!['promoted_service_rule','promoted_case_outcome','promoted_diagnostic_pattern','raw_reference'].includes(e.kind)||!strings(e.refs)||!['recommended','resolved','not_resolved','mixed','not_evaluable','informational'].includes(e.outcome)) fail(id,'evidence');
    if(e?.cohortCount!==null && (!Number.isInteger(e?.cohortCount)||e.cohortCount<1)) fail(id,'cohortCount must be known positive integer or null');
    if(!Array.isArray(c.paths)||!c.paths.length) {fail(id,'paths');continue;}
    const pathIds=new Set(c.paths.map(p=>p.id));
    if(pathIds.size!==c.paths.length) fail(id,'duplicate path id');
    for(const p of c.paths) {
      if(catalog.schemaVersion===2) {
        if(!evidenceStates.includes(p.evidence_state)) fail(id,'path evidence_state');
        if(!['approved','candidate','withheld'].includes(p.publication)||![...publicVisibility,'PIE_ONLY'].includes(p.agent_visibility)) fail(id,'path publication/visibility');
        if(typeof p.conflict!=='boolean'||!(p.supersededBy===null||text(p.supersededBy))) fail(id,'path conflict/supersession');
        if(!validReview(p.review)) fail(id,'path review');
        if(p.qualifier!==undefined&&!text(p.qualifier)) fail(id,'path qualifier');
      }
      if(!text(p.id)||!text(p.symptom)||!['repair','check','information','escalate'].includes(p.kind)||!strings(p.action)) fail(id,'path fields');
      if(p.kind==='repair'&&(!text(p.part)||e?.kind==='raw_reference'||s?.status==='not_required')) fail(id,'repair requires promoted evidence, part and explicit scope');
      if(p.kind!=='repair'&&p.part!==null) fail(id,'non-repair part must be null');
      if(!strings(p.verification?.steps)||!strings(p.verification?.canonical)) fail(id,'verification');
      const fallback=p.ifNotFixed;
      if(!fallback||!text(fallback.message)||!['path','escalate'].includes(fallback.kind)) fail(id,'ifNotFixed');
      else if(fallback.kind==='path'&&!pathIds.has(fallback.pathId)) fail(id,'dangling ifNotFixed path');
      const seen=new Set();let current=p;
      while(current?.ifNotFixed?.kind==='path') {
        if(seen.has(current.id)) {fail(id,'cyclic ifNotFixed transition');break;}
        seen.add(current.id);current=c.paths.find(x=>x.id===current.ifNotFixed.pathId);
      }
    }
  }
  if(catalog.schemaVersion===2) {
    if(!Array.isArray(catalog.symptoms)) fail('symptoms','missing symptoms');
    const symptoms=new Set();
    for(const s of catalog.symptoms||[]) {
      const id=s?.symptom_id||'unknown symptom';
      if(!/^SYM-\d{3}$/.test(id)||symptoms.has(id)) fail(id,'duplicate/invalid symptom_id');
      symptoms.add(id);
      if(!OBSERVABLE_AREAS.includes(s.observable_area)) fail(id,'observable_area');
      if(!text(s.label_en)||!text(s.label_cn)||!Array.isArray(s.aliases)||!s.aliases.every(text)) fail(id,'symptom labels/aliases');
      if(!['NAVIGATION','PIE_ONLY'].includes(s.agent_visibility)||(reservedSymptom(s)&&s.agent_visibility!=='PIE_ONLY')) fail(id,'symptom visibility');
      if(!Array.isArray(s.repair_refs)) {fail(id,'repair_refs');continue;}
      const refs=new Set();
      for(const ref of s.repair_refs) {
        const key=ref.card_id+':'+ref.repair_path_id;
        if(refs.has(key)) fail(id,'duplicate repair reference');refs.add(key);
        const c=catalog.cards.find(c=>c.id===ref.card_id);
        if(!c?.paths?.some(p=>p.id===ref.repair_path_id)) fail(id,'dangling repair reference');
      }
    }
  }
  return errors;
}

function scopeProblem(card,context) {
  const s=card.scope;
  if(s.status==='unknown') return 'The repair scope for this model needs PIE confirmation. Contact PIE before replacing a part.';
  if(s.status==='confirmed'&&!s.models.some(m=>normalize(m)===normalize(context.model))) return 'Select the exact model listed for this guide. If your model is not listed, contact PIE.';
  if(s.firmware.length&&!s.firmware.some(v=>normalize(v)===normalize(context.firmware))) return 'This guide needs a matching firmware version. Confirm the version with PIE if it is not listed.';
  return null;
}

export function projectAgentCatalog(catalog) {
  const errors=validateCatalog(catalog);
  if(errors.length) throw new Error(errors.join('\n'));
  const cards=catalog.cards.filter(approvedCard).map(c=>({
    id:c.id,code:c.code,message:c.message,aliases:[...c.aliases],
    lifecycle:c.lifecycle,scope:{status:c.scope.status,models:[...c.scope.models],firmware:[...c.scope.firmware]},
    paths:c.paths.map(p=>publicPath(c,p))
  }));
  const result={schemaVersion:catalog.schemaVersion,knowledgeVersion:catalog.knowledgeVersion,cards};
  if(catalog.schemaVersion===2) result.symptoms=catalog.symptoms.filter(navigable).map(s=>({
    symptom_id:s.symptom_id,observable_area:s.observable_area,label_en:s.label_en,aliases:[...s.aliases],
    repair_refs:s.repair_refs.filter(r=>cards.some(c=>c.id===r.card_id&&c.paths.some(p=>p.id===r.repair_path_id))).map(r=>({card_id:r.card_id,repair_path_id:r.repair_path_id}))
  }));
  return result;
}

export function searchCards(cards,query) {
  const q=normalize(query).slice(0,500);
  const result=(kind,matches)=>({kind,matches,autoOpen:false});
  if(!q) return result('empty',[]);
  const exact=cards.filter(c=>text(c.code)&&normalize(c.code)===q);
  if(exact.length) return result('exact_code',exact);
  const exactMessage=cards.filter(c=>[c.message,...c.aliases].some(m=>normalize(m)===q));
  if(exactMessage.length) return result('exact_message',exactMessage);
  // A numeric typo cannot become a different error by fuzzy matching.
  if(/^[-+]?\d+$/.test(q)||/^[a-z]+-\d+$/.test(q)) return result('unsupported',[]);
  const tokens=q.match(/(?<![a-z0-9.])(?:[a-z]+-\d+|[-+]?\d+)(?![a-z0-9.])/g)||[];
  const codeMatches=cards.filter(c=>text(c.code)&&tokens.includes(normalize(c.code)));
  if(codeMatches.length) return result(codeMatches.length===1&&tokens.length===1?'exact_code':'candidates',codeMatches);
  const words=q.match(/[a-z]{3,}/g)||[];
  if(!words.length) return result('unsupported',[]);
  const ranked=cards.map(c=>{
    const hay=normalize([c.message,...c.aliases].join(' '));
    const terms=new Set(hay.match(/[a-z]{3,}/g)||[]);
    let score=0;
    for(const word of new Set(words)) {
      if(terms.has(word)) score+=2;
      else if(word.length>=5 && [...terms].some(term=>editDistance(word,term)===1)) score+=1;
    }
    return {c,score};
  }).filter(x=>x.score>=Math.min(2,words.length*2)).sort((a,b)=>b.score-a.score||String(a.c.code??a.c.id).localeCompare(String(b.c.code??b.c.id)));
  return result(ranked.length?'candidates':'unsupported',ranked.slice(0,8).map(x=>x.c));
}
function editDistance(a,b) {
  if(Math.abs(a.length-b.length)>1) return 2;
  let prev=Array.from({length:b.length+1},(_,i)=>i);
  for(let i=1;i<=a.length;i++) {
    const next=[i];
    for(let j=1;j<=b.length;j++) next[j]=Math.min(next[j-1]+1,prev[j]+1,prev[j-1]+(a[i-1]===b[j-1]?0:1));
    prev=next;
  }
  return prev[b.length];
}

export function resolveCard(card,context={}) {
  if(!card||['RETIRED','SUPERSEDED','HISTORICAL','REVIEW_REQUIRED'].includes(card.lifecycle)) return escalate('This guide needs current advice from PIE. Confirm the model and current firmware before using a historical fix.');
  if(canonicalCard(card)&&!approvedCard(card)) return escalate();
  if(!Array.isArray(card.paths)||!card.scope) return escalate();
  if(canonicalCard(card)) card={...card,paths:card.paths.map(p=>publicPath(card,p))};
  if(context.returned) return escalate('The issue returned after repair. Contact PIE with the repair result and fresh evidence; do not repeat the same replacement.');
  const completed=Array.isArray(context.completedRepairs)?context.completedRepairs:[];
  const choices=card.paths.filter(p=>p.directSelectable!==false);
  let path=context.pathId?card.paths.find(p=>p.id===context.pathId):null;
  if(context.pathId&&!path) return escalate('That repair path is unavailable. Start a new search or contact PIE.');
  if(!path&&choices.length>1) return {kind:'choose_symptom',part:null,choices:choices.map(p=>({id:p.id,symptom:p.symptom}))};
  path=path||choices[0];
  if(!path) return escalate();
  if(path.directSelectable===false&&!card.paths.some(p=>completed.includes(p.id)&&p.ifNotFixed.kind==='path'&&p.ifNotFixed.pathId===path.id)) return escalate('Confirm the previous repair result with PIE before using this next step.');
  const visited=new Set();let qualifierConfirmed=context.qualifierConfirmed===true;
  while(completed.includes(path.id)) {
    if(visited.has(path.id)||path.ifNotFixed.kind!=='path') return escalate(path.ifNotFixed.message);
    visited.add(path.id);path=card.paths.find(p=>p.id===path.ifNotFixed.pathId);qualifierConfirmed=false;
    if(!path) return escalate();
  }
  if(!pathEligible(card,path)&&!canonicalCard(card)) return escalate();
  if(path.kind==='repair'&&normalize(card.code)==='1202') return escalate();
  if(path.kind==='repair'||(['check','information'].includes(path.kind)&&card.scope.status==='confirmed')) {
    const problem=scopeProblem(card,context);
    if(problem) return card.scope.status==='unknown'?escalate(problem):{kind:'scope_required',part:null,action:[problem]};
  }
  if(path.kind!=='escalate'&&text(path.qualifier)&&!qualifierConfirmed) return {
    kind:'qualifier_required',part:null,pathId:path.id,prompt:path.qualifier,
    choices:[{id:'yes',label:'Yes, this matches'},{id:'no',label:'No / unsure — contact PIE'}]
  };
  return {kind:path.kind,pathId:path.id,part:path.part,symptom:path.symptom,action:[...path.action],
    verification:{steps:[...path.verification.steps]},ifNotFixed:structuredClone(path.ifNotFixed),completedRepairs:[...completed]};
}

export function searchSymptoms(symptoms,query) {
  const q=normalize(query).slice(0,500);
  const matches=q?symptoms.filter(s=>navigable(s)&&[s.label_en,...s.aliases].some(label=>normalize(label)===q)):[];
  return {kind:!q?'empty':matches.length?'exact_symptom':'unsupported',matches,autoOpen:false};
}

export function resolveSymptom(catalog,symptomId,context={}) {
  const symptom=catalog?.symptoms?.find(s=>s.symptom_id===symptomId);
  if(!symptom||!navigable(symptom)) return escalate();
  const refs=symptom.repair_refs.filter(ref=>catalog.cards.some(c=>c.id===ref.card_id&&(!canonicalCard(c)||approvedCard(c))&&c.paths.some(p=>p.id===ref.repair_path_id)));
  if(!refs.length) return escalate();
  if(refs.length>1) return {kind:'choose_path',part:null,choices:refs.map(ref=>{
    const card=catalog.cards.find(c=>c.id===ref.card_id);
    const path=card.paths.find(p=>p.id===ref.repair_path_id);
    return {cardId:ref.card_id,pathId:ref.repair_path_id,label:(canonicalCard(card)?publicPath(card,path):path).symptom};
  })};
  const ref=refs[0];
  return resolveCard(catalog.cards.find(c=>c.id===ref.card_id),{...context,pathId:ref.repair_path_id});
}

export function recordOutcome(card,pathId,choice,context={}) {
  const current=resolveCard(card,{...context,pathId});
  if(!['repair','check','information'].includes(current.kind)) return current;
  if(choice==='fixed') {
    if(context.verificationComplete!==true) return {kind:'verification_required',part:null,message:'Complete the after-repair checks first.'};
    return {kind:'reported_fixed',part:null,caseClosed:false,message:'You reported that the checks passed and the issue is gone. Keep the results with your service record. This page does not close a case.'};
  }
  if(choice==='returned') return resolveCard(card,{...context,returned:true});
  if(choice!=='not_fixed') return escalate('Choose a valid result.');
  const done=[...new Set([...(context.completedRepairs||[]),pathId])];
  if(current.ifNotFixed.kind==='escalate') return escalate(current.ifNotFixed.message);
  return resolveCard(card,{...context,pathId:current.ifNotFixed.pathId,completedRepairs:done,verificationComplete:false,qualifierConfirmed:false});
}

export function exportWorkbench(catalog,context={}) {
  const errors=validateCatalog(catalog);if(errors.length) throw new Error(errors.join('\n'));
  return {contract:'pie.error-code.readonly.v1',knowledgeVersion:catalog.knowledgeVersion,readOnly:true,
    entries:catalog.cards.filter(c=>approvedCard(c)&&c.lifecycle==='CURRENT').map(c=>({
      id:c.id,code:c.code,sourceRefs:[...c.evidence.refs],scope:structuredClone(c.scope),
      applicable:!scopeProblem(c,context),decisive:false,
      result:resolveCard(c,context)
    }))};
}

// Selection controls use catalog identities, never free text or inferred model families.
export function controlledModels(catalog) {
  return [...new Set(catalog.cards.flatMap(c=>c.scope.models))].sort();
}
const selectionRefFits=(catalog,ref,model)=>{
 const card=catalog.cards.find(c=>c.id===ref.card_id),path=card?.paths.find(p=>p.id===ref.repair_path_id);
 if(!card||!path||path.directSelectable===false)return false;
 if(card.scope.status==='confirmed')return card.scope.models.includes(model);
 return path.kind!=='repair'&&(!card.scope.models.length||card.scope.models.includes(model));
};
export function controlledSymptoms(catalog,{model,area}) {
  if(!controlledModels(catalog).includes(model)||!OBSERVABLE_AREAS.includes(area))return [];
  return catalog.symptoms.filter(s=>navigable(s)&&s.observable_area===area&&(
    !s.repair_refs.length||s.repair_refs.some(r=>selectionRefFits(catalog,r,model))));
}
export function validControlledSelection(catalog,selection) {
  return controlledModels(catalog).includes(selection.model)&&OBSERVABLE_AREAS.includes(selection.area)&&(
    selection.symptomId==='__other__'||controlledSymptoms(catalog,selection).some(s=>s.symptom_id===selection.symptomId));
}
export function controlledReferences(catalog,selection) {
  const symptom=controlledSymptoms(catalog,selection).find(s=>s.symptom_id===selection.symptomId);
  return symptom? symptom.repair_refs.filter(r=>selectionRefFits(catalog,r,selection.model)):[];
}
export function controlledRepairAllowed(catalog,selection,cardId,pathId,completed=[]) {
 const card=catalog.cards.find(c=>c.id===cardId),target=card?.paths.find(p=>p.id===pathId);
 if(!target)return false;
 const refs=controlledReferences(catalog,selection).filter(r=>r.card_id===cardId);
 if(refs.some(r=>r.repair_path_id===pathId))return true;
 if(target.directSelectable!==false)return false;
 return refs.some(ref=>{
  let cursor=ref.repair_path_id;const seen=new Set();
  while(!seen.has(cursor)&&completed.includes(cursor)){
   seen.add(cursor);const predecessor=card.paths.find(p=>p.id===cursor);
   if(predecessor?.ifNotFixed?.kind!=='path')return false;
   cursor=predecessor.ifNotFixed.pathId;if(cursor===pathId)return true;
  }
  return false;
 });
}
