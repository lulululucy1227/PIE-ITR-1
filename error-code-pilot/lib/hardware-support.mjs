const text=x=>typeof x==='string'&&x.trim().length>0;
const strings=x=>Array.isArray(x)&&x.length>0&&x.every(text);
const sha=x=>typeof x==='string'&&/^[a-f0-9]{64}$/.test(x);
const kinds=new Set(['parts','tools','reasoning','disassembly','verification','safety']);
const facts=new Set(['part-fitment-confirmed','replacement-target-confirmed','safe-to-open-confirmed','service-procedure-scope-confirmed']);
const privateText=/PRIVATE-CANARY|password|api[_ -]?key|bearer\s|https?:\/\/|[A-Z]:[\\/]|@[a-z0-9.-]+\.(com|net|org)/i;

// Build-time only. Input is locally reviewed evidence; output is the small agent
// resource contract. Never copy provenance, review flags, or withheld records.
export function projectHardwareSupport(input,catalog){
 if(input?.schemaVersion!==1||!Array.isArray(input.sources)||!Array.isArray(input.records))throw new Error('Invalid hardware support header');
 const sources=new Map();
 for(const s of input.sources){if(!text(s.id)||sources.has(s.id)||!sha(s.sha256))throw new Error('Invalid hardware source');sources.set(s.id,s);}
 const seen=new Set();
 return input.records.map(r=>{
  const fail=message=>{throw new Error(`${r?.id||'hardware support'}: ${message}`);};
  if(!r||!text(r.id)||!/^[a-z][a-z0-9-]{2,99}$/.test(r.id)||seen.has(r.id)||!kinds.has(r.kind))fail('invalid resource');
  seen.add(r.id);
  if(r.status!=='APPROVED'||!['scopeConfirmed','safetyReviewed','current'].every(k=>r.review?.[k]===true))fail('review required');
  if(!Array.isArray(r.sourceRefs)||!r.sourceRefs.length||r.sourceRefs.some(s=>sources.get(s.sourceId)?.sha256!==s.sha256||!text(s.section)))fail('source mismatch');
  const b=r.binding,c=catalog.cards.find(c=>c.id===b?.cardId),p=c?.paths.find(p=>p.id===b?.pathId);
  if(!b||!c||c.scope.status!=='confirmed'||!c.scope.models.includes(b.model)||!p||!['repair','check','information'].includes(p.kind)||b.knowledgeVersion!==catalog.knowledgeVersion||!Number.isInteger(b.actionIndex)||p.action[b.actionIndex]!==b.instruction||!text(b.instruction))fail('unavailable target or stale scope');
  if(c.scope.firmware.length?!c.scope.firmware.includes(b.firmware):b.firmware!=='')fail('firmware scope');
  if(!text(r.title)||!strings(r.lines)||r.lines.length>4||r.lines.some(line=>line.length>400)||privateText.test([r.title,...r.lines].join(' ')))fail('invalid public detail');
  const requirements=r.requires??[];
  if(!Array.isArray(requirements)||!requirements.every(x=>facts.has(x)))fail('invalid requirements');
  if(r.kind==='parts'&&(p.kind!=='repair'||!text(r.partNumber)||!/^[A-Z0-9][A-Z0-9._/-]{0,79}$/.test(r.partNumber)||!Number.isInteger(r.quantity)||r.quantity<1||!['part-fitment-confirmed','replacement-target-confirmed'].every(x=>requirements.includes(x))))fail('part fitment/quantity required');
  if(r.kind==='disassembly'&&!['safe-to-open-confirmed','service-procedure-scope-confirmed'].every(x=>requirements.includes(x)))fail('safe procedure confirmation required');
  return {id:r.id,kind:r.kind,binding:{cardId:b.cardId,pathId:b.pathId,model:b.model,firmware:b.firmware,knowledgeVersion:b.knowledgeVersion,actionIndex:b.actionIndex,instruction:b.instruction},title:r.title,lines:[...r.lines],requires:[...requirements],...(r.kind==='parts'?{partNumber:r.partNumber,quantity:r.quantity}:{})};
 });
}
