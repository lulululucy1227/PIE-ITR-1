const text = value => typeof value === 'string' && value.trim().length > 0;
const strings = value => Array.isArray(value) && value.length > 0 && value.every(text);
const normalize = value => String(value ?? '').normalize('NFKC').replace(/\u2212/g,'-').trim().toLowerCase().replace(/\s+/g,' ');
const visible = card => card.agentVisible === true && !['RETIRED','SUPERSEDED'].includes(card.lifecycle);
const escalate = message => ({kind:'escalate',part:null,action:[message || 'Contact PIE with the exact model, error message, observed symptom and previous repair results.'],verification:null});
const lifecycle = ['CURRENT','HISTORICAL','REVIEW_REQUIRED','SUPERSEDED','RETIRED'];
const classifications = ['SELF_SERVICE_DIRECT','SELF_SERVICE_SYMPTOM_SPLIT','PIE_ONLY','NOT_YET_STABLE','EXCLUDE_FROM_PILOT'];

export function validateCatalog(catalog) {
  const errors=[];
  const fail=(id,message)=>errors.push(id+': '+message);
  if(catalog?.schemaVersion!==1 || !text(catalog?.knowledgeVersion) || !Array.isArray(catalog?.cards)) return ['Invalid catalog header'];
  const ids=new Set();
  for(const c of catalog.cards) {
    const id=c?.id || 'unknown';
    if(!text(c?.id)||ids.has(id)) fail(id,'duplicate/missing id');
    ids.add(id);
    if(!text(c.code)||!/^([-+]?\d+|[A-Z]+-\d+)$/i.test(c.code)) fail(id,'invalid code string');
    if(!text(c.message)||!Array.isArray(c.aliases)||!c.aliases.every(text)) fail(id,'message/aliases');
    if(!classifications.includes(c.classification)||!lifecycle.includes(c.lifecycle)) fail(id,'classification/lifecycle');
    if(!['pilot','approved','withheld'].includes(c.publication)||typeof c.agentVisible!=='boolean') fail(id,'publication/visibility');
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
  return {schemaVersion:1,knowledgeVersion:catalog.knowledgeVersion,cards:catalog.cards.filter(c=>visible(c)&&c.publication!=='withheld').map(c=>({
    id:c.id,code:c.code,message:c.message,aliases:[...c.aliases],
    lifecycle:c.lifecycle,scope:{status:c.scope.status,models:[...c.scope.models],firmware:[...c.scope.firmware]},
    paths:c.paths.map(p=> {
      // Unresolved/historical replacement prose never enters the public bundle.
      // It remains in canonical knowledge for the supervisor's scope decision.
      if(p.kind==='repair'&&(c.scope.status==='unknown'||c.lifecycle!=='CURRENT')) return {
        id:p.id,symptom:p.symptom,directSelectable:p.directSelectable??true,kind:'escalate',part:null,
        action:[scopeProblem(c,{})||'This historical repair needs current guidance from PIE.'],
        verification:{steps:['Confirm the next action with PIE.'],canonical:['Confirm the next action with PIE.']},
        ifNotFixed:{kind:'escalate',message:'Contact PIE; do not repeat an unconfirmed replacement.'}
      };
      return {id:p.id,symptom:p.symptom,directSelectable:p.directSelectable??true,kind:p.kind,part:p.part,
        action:[...p.action],verification:{steps:[...p.verification.steps]},ifNotFixed:{
          kind:p.ifNotFixed.kind,message:p.ifNotFixed.message,
          ...(p.ifNotFixed.kind==='path'?{pathId:p.ifNotFixed.pathId}:{})
        }};
    })
  }))};
}

export function searchCards(cards,query) {
  const q=normalize(query).slice(0,500);
  const result=(kind,matches)=>({kind,matches,autoOpen:false});
  if(!q) return result('empty',[]);
  const exact=cards.filter(c=>normalize(c.code)===q);
  if(exact.length) return result('exact_code',exact);
  const exactMessage=cards.filter(c=>[c.message,...c.aliases].some(m=>normalize(m)===q));
  if(exactMessage.length) return result('exact_message',exactMessage);
  // A numeric typo cannot become a different error by fuzzy matching.
  if(/^[-+]?\d+$/.test(q)||/^[a-z]+-\d+$/.test(q)) return result('unsupported',[]);
  const tokens=q.match(/(?<![a-z0-9.])(?:[a-z]+-\d+|[-+]?\d+)(?![a-z0-9.])/g)||[];
  const codeMatches=cards.filter(c=>tokens.includes(normalize(c.code)));
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
  }).filter(x=>x.score>=Math.min(2,words.length*2)).sort((a,b)=>b.score-a.score||a.c.code.localeCompare(b.c.code));
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
  if(context.returned) return escalate('The issue returned after repair. Contact PIE with the repair result and fresh evidence; do not repeat the same replacement.');
  const completed=Array.isArray(context.completedRepairs)?context.completedRepairs:[];
  const choices=card.paths.filter(p=>p.directSelectable!==false);
  let path=context.pathId?card.paths.find(p=>p.id===context.pathId):null;
  if(context.pathId&&!path) return escalate('That repair path is unavailable. Start a new search or contact PIE.');
  if(!path&&choices.length>1) return {kind:'choose_symptom',part:null,choices:choices.map(p=>({id:p.id,symptom:p.symptom}))};
  path=path||choices[0];
  if(!path) return escalate();
  if(path.directSelectable===false&&!card.paths.some(p=>completed.includes(p.id)&&p.ifNotFixed.kind==='path'&&p.ifNotFixed.pathId===path.id)) return escalate('Confirm the previous repair result with PIE before using this next step.');
  const visited=new Set();
  while(completed.includes(path.id)) {
    if(visited.has(path.id)||path.ifNotFixed.kind!=='path') return escalate(path.ifNotFixed.message);
    visited.add(path.id);path=card.paths.find(p=>p.id===path.ifNotFixed.pathId);
    if(!path) return escalate();
  }
  if(path.kind==='repair') {
    const problem=scopeProblem(card,context);
    if(problem) return card.scope.status==='unknown'?escalate(problem):{kind:'scope_required',part:null,action:[problem]};
  }
  return {kind:path.kind,pathId:path.id,part:path.part,symptom:path.symptom,action:[...path.action],
    verification:structuredClone(path.verification),ifNotFixed:structuredClone(path.ifNotFixed),completedRepairs:[...completed]};
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
  return resolveCard(card,{...context,pathId:current.ifNotFixed.pathId,completedRepairs:done,verificationComplete:false});
}

export function exportWorkbench(catalog,context={}) {
  const errors=validateCatalog(catalog);if(errors.length) throw new Error(errors.join('\n'));
  return {contract:'pie.error-code.readonly.v1',knowledgeVersion:catalog.knowledgeVersion,readOnly:true,
    entries:catalog.cards.filter(c=>c.publication==='approved'&&visible(c)&&c.lifecycle==='CURRENT').map(c=>({
      id:c.id,code:c.code,sourceRefs:[...c.evidence.refs],scope:structuredClone(c.scope),
      applicable:!scopeProblem(c,context),decisive:false,
      result:resolveCard(c,context)
    }))};
}
