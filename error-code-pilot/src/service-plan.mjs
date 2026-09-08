/**
 * Presentation adapter, called only after the existing resolver and exact-path guard.
 * It cannot resolve a symptom or authorize a repair. No resource source is connected.
 *
 * Future support records are curated supplements to an existing action, not routes.
 * Before supplying real records, the publishing pipeline must review and project
 * them. Matching review flags here is validation, not proof of external approval.
 * @typedef {'parts'|'tools'|'reasoning'|'disassembly'|'verification'} SupportKind
 * @typedef {{cardId:string,pathId:string,model:string,firmware:string,
 *   knowledgeVersion:string,actionIndex:number,instruction:string}} StepBinding
 * @typedef {{id:string,kind:SupportKind,status:'APPROVED',
 *   review:{scopeConfirmed:boolean,safetyReviewed:boolean},binding:StepBinding,
 *   title:string,lines:string[],requires?:string[],partNumber?:string,quantity?:number}} StepSupport
 */
const text=value=>typeof value==='string'&&value.trim().length>0;
const lines=value=>Array.isArray(value)&&value.length>0&&value.every(text);
const kinds=new Set(['parts','tools','reasoning','disassembly','verification']);

function stepSupport(records,binding,resultKind,confirmedFacts){
 const output=[],seen=new Set();
 for(const record of records){
  if(!record||!text(record.id)||seen.has(record.id)||!kinds.has(record.kind)||record.status!=='APPROVED')continue;
  if(record.review?.scopeConfirmed!==true||record.review?.safetyReviewed!==true)continue;
  if(!text(record.title)||!lines(record.lines)||!record.binding)continue;
  if(!text(binding.model)||!text(binding.cardId)||!text(binding.knowledgeVersion))continue;
  if(Object.keys(binding).some(key=>record.binding[key]!==binding[key]))continue;
  const requirements=record.requires??[];
  if(!Array.isArray(requirements)||!requirements.every(text)||requirements.some(fact=>!confirmedFacts.includes(fact)))continue;
  if(record.kind==='parts'&&!['part-fitment-confirmed','replacement-target-confirmed'].every(fact=>requirements.includes(fact)))continue;
  if(record.kind==='disassembly'&&!['safe-to-open-confirmed','service-procedure-scope-confirmed'].every(fact=>requirements.includes(fact)))continue;
  if(record.kind==='parts'&&(resultKind!=='repair'||!text(record.partNumber)||!Number.isInteger(record.quantity)||record.quantity<1))continue;
  seen.add(record.id);
  output.push({id:record.id,kind:record.kind,title:record.title,lines:[...record.lines],
   ...(record.kind==='parts'?{partNumber:record.partNumber,quantity:record.quantity}:{})});
 }
 return output;
}

/**
 * Preserve every approved instruction and its order. Empty support means no UI.
 * Binding includes the full instruction and knowledge version to invalidate stale
 * attachments after an edit or reorder. It deliberately assumes no family scope.
 * @param {object} result Current authorized resolver result
 * @param {{cardId:string,model:string,firmware:string,knowledgeVersion:string,confirmedFacts?:string[]}} context
 * @param {StepSupport[]} support Future curated records; empty in this release
 */
export function buildServicePlan(result,context,support=[]){
 if(!result||!['repair','check','information'].includes(result.kind)||!text(result.pathId)||!lines(result.action)||!lines(result.verification?.steps)||!text(result.ifNotFixed?.message))return null;
 const records=Array.isArray(support)?support:[];
 return {
  pathId:result.pathId,
  steps:result.action.map((instruction,actionIndex)=>{
   const binding={cardId:context.cardId,pathId:result.pathId,model:context.model,firmware:context.firmware||'',knowledgeVersion:context.knowledgeVersion,actionIndex,instruction};
   return {id:result.pathId+':action:'+actionIndex,number:actionIndex+1,instruction,support:stepSupport(records,binding,result.kind,Array.isArray(context.confirmedFacts)?context.confirmedFacts:[])};
  }),
  verification:[...result.verification.steps],
  fallback:result.ifNotFixed.message
 };
}
