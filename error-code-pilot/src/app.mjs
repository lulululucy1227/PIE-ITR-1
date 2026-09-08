import {searchCards,resolveCard,recordOutcome,OBSERVABLE_AREAS,controlledModels,controlledSymptoms,controlledReferences,controlledRepairAllowed,validControlledSelection} from './engine.mjs';
const $=id=>document.getElementById(id);
let catalog=null,selected=null,current=null,pendingPIE=null,issueTitle='',selectedSymptom=null,stage='category',resolutionKey='';
const mower={model:'',firmware:''},visits=new Map();
const visit=card=>{if(!visits.has(card.id))visits.set(card.id,{completedRepairs:[]});return visits.get(card.id);};
const fields=()=>({model:$('model').value,area:$('observable-area').value,symptomId:$('observed-symptom').value});
const context=()=>({...visit(selected),...mower});
const inputsKey=()=>JSON.stringify({...fields(),error:$('search').value,firmware:$('firmware').value,other:$('other-description').value});
const valid=()=>catalog&&validControlledSelection(catalog,fields());
const navigationSession=crypto.randomUUID();let revision=0,pageName='identify';
const marker=page=>({session:navigationSession,page,revision,stage});
function el(tag,text,className){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(className)n.className=className;return n;}
function button(text,action,className='choice'){const n=el('button',text,className);const key=inputsKey();n.type='button';n.addEventListener('click',()=>{if(className==='choice'&&(!valid()||key!==inputsKey())){invalidate();clearSelection();setStage('symptom');return;}action();});return n;}
function status(text,error=false){$('status').textContent=error?text:'';$('status').classList.toggle('error',error);}
function clearResult(){$('result').replaceChildren();}
function focusResult(){const n=pageName==='solution'?$('solution-page'):$(stage+'-stage');n.focus({preventScroll:true});n.scrollIntoView({block:'start',behavior:'instant'});}
function note(title,lines){const box=el('div',undefined,'alert');box.append(el('h3',title));const list=el('ul');for(const line of lines)list.append(el('li',line));box.append(list);return box;}
function setStage(next){stage=next;for(const id of ['category','symptom','confirm'])$(id+'-stage').hidden=id!==next;
 if(next==='symptom')$('search-form').insertBefore($('more-details'),$('detail-buttons'));
 $('context-summary').textContent=[fields().model,fields().area].filter(Boolean).join(' · ');
 $('confirmation-summary').textContent=[fields().model,catalog?.symptoms.find(s=>s.symptom_id===fields().symptomId)?.label_en||'Other / None of these'].join(' · ');
}
function showIdentify(){pageName='identify';$('identify-page').hidden=false;$('solution-page').hidden=true;clearResult();$('solution-summary').replaceChildren();setStage(stage);status('');}
function invalidate(){revision++;current=null;resolutionKey='';showIdentify();history.replaceState(marker('identify'),'','#identify');}
function clearSelection(){selected=null;pendingPIE=null;selectedSymptom=null;issueTitle='';$('selection').replaceChildren();}
function editIssue(){if(pageName==='solution'&&history.state?.session===navigationSession)history.back();else{showIdentify();history.replaceState(marker('identify'),'','#identify');}}
function resetQualifiers(){for(const state of visits.values()){state.qualifierConfirmed=false;state.qualifierRejected=false;}}
function refreshSymptoms(){const select=$('observed-symptom');select.replaceChildren(new Option('Select a symptom',''));for(const s of controlledSymptoms(catalog,fields()))select.append(new Option(s.label_en,s.symptom_id));select.append(new Option('Other / None of these','__other__'));$('other-field').hidden=true;$('other-description').value='';}
function categoryChanged(modelChanged){invalidate();clearSelection();mower.model=controlledModels(catalog).includes(fields().model)?fields().model:'';if(modelChanged){$('firmware').value='';mower.firmware='';}resetQualifiers();refreshSymptoms();setStage('category');history.replaceState(marker('identify'),'','#identify');}
function nextCategory(){if(!catalog||!controlledModels(catalog).includes(fields().model)||!OBSERVABLE_AREAS.includes(fields().area)){status('Choose a model and a problem from the list.',true);return;}setStage('symptom');history.replaceState(marker('identify'),'','#identify');focusResult();}
function detailsEdited(){invalidate();clearSelection();resetQualifiers();$('other-field').hidden=fields().symptomId!=='__other__';if(stage==='confirm')setStage('symptom');history.replaceState(marker('identify'),'','#identify');}
function safePIE(title='Your selected issue',result){if(!valid())return;selected=null;selectedSymptom=fields().symptomId;issueTitle=title;pendingPIE=result||{action:['Contact PIE with the selected model, observed symptom, exact message and any checks or repairs already tried.']};resolutionKey=inputsKey();renderIdentification();}
function prepareIdentification(){if(!valid()){invalidate();clearSelection();setStage('symptom');status('Choose a symptom from the list.',true);return;}
 invalidate();clearSelection();mower.model=fields().model;mower.firmware=$('firmware').value.trim();
 if(fields().symptomId==='__other__'){safePIE('Other / None of these',{action:['Contact PIE with your model, the observed problem and any checks already tried. The additional description can help PIE review a missing symptom; it does not identify a faulty part.']});return;}
 if($('search').value.trim()){showCandidates();return;}openSymptom();
}
function beginIdentification(){prepareIdentification();const result=resolved();if(result&&!['scope_required','choose_symptom','qualifier_required','choose_path'].includes(result.kind)){setStage('symptom');viewSolution();}}
function openSymptom(){if(!valid()||fields().symptomId==='__other__')return;selectedSymptom=fields().symptomId;const s=catalog.symptoms.find(s=>s.symptom_id===selectedSymptom);issueTitle=s.label_en;const refs=controlledReferences(catalog,fields());
 if(!refs.length){safePIE(issueTitle);return;}
 if(refs.length===1){const r=refs[0];openCard(catalog.cards.find(c=>c.id===r.card_id),r.repair_path_id,true);return;}
 const box=el('article',undefined,'card');box.append(el('h3','Which condition matches?'));for(const r of refs){const card=catalog.cards.find(c=>c.id===r.card_id),path=card.paths.find(p=>p.id===r.repair_path_id);box.append(button(path.symptom,()=>openCard(card,path.id,true)));}showConfirmation(box);
}
function showConfirmation(box){setStage('confirm');$('selection').replaceChildren(box);$('scope-details').hidden=true;history.replaceState(marker('identify'),'','#identify');focusResult();}
function showCandidates(){const result=searchCards(catalog.cards,$('search').value);if(!result.matches.length){safePIE('No matching code or message',{action:['Contact PIE with the exact code or message and selected symptom. Do not substitute a similar code or assume a repair from the description.']});return;}
 const box=el('article',undefined,'card');box.append(el('h3','Confirm the message shown'));
 for(const card of result.matches)box.append(button((card.code?card.code+' · ':'')+card.message,()=>openCard(card)));
 box.append(button('None of these',()=>safePIE('Message not confirmed'),'text-button'));showConfirmation(box);
}
function openCard(card,pathId,fromSymptom=false){if(!valid()||fields().symptomId==='__other__'||!catalog.cards.includes(card))return;
 const refs=controlledReferences(catalog,fields());
 if(card.code===null&&!refs.some(r=>r.card_id===card.id&&(!pathId||r.repair_path_id===pathId))){safePIE('The selected symptom and message need review');return;}
 // Code-specific nonrepair conditions remain explicit. An unrelated code never authorizes a repair.
 if(card.code==='1202'&&fields().area!=='Cutting'){safePIE('The selected symptom and message need review');return;}
 if(card.code==='5510'){safePIE('Confirm the remaining fault with PIE',{action:['This message reports successful self-calibration. A selected fault still needs separate assessment; contact PIE with what remains abnormal.']});return;}
 selected=card;pendingPIE=null;selectedSymptom=fields().symptomId;issueTitle=card.message;
 const state=visit(card);state.qualifierConfirmed=false;state.qualifierRejected=false;
 if(pathId)state.pathId=pathId;else if(!state.completedRepairs.length&&!state.returned)state.pathId=undefined;
 resolutionKey=inputsKey();renderIdentification();
}
function resolved(){
 if(!valid()||resolutionKey!==inputsKey())return null;
 if(!selected)return pendingPIE?{kind:'escalate',...pendingPIE}:null;
 const state=visit(selected);
 if(state.qualifierRejected)return {kind:'escalate',action:['The observed condition does not match this guide. Contact PIE with the model, firmware and exact behavior.']};
 const result=resolveCard(selected,context());
 if(result.kind==='repair'&&!controlledRepairAllowed(catalog,fields(),selected.id,result.pathId,state.completedRepairs))return {kind:'escalate',action:['Contact PIE to confirm the connection between this message and the selected symptom.']};
 return result;
}
function renderIdentification(){const result=resolved();if(!result){clearSelection();setStage('symptom');return;}setStage('confirm');const box=el('article',undefined,'card');const state=selected&&visit(selected);
 if(result.kind==='choose_symptom'){box.append(el('h3','Which condition matches?'));for(const c of result.choices)box.append(button(c.symptom,()=>{if(!valid()||resolutionKey!==inputsKey())return;Object.assign(state,{pathId:c.id,qualifierConfirmed:false,qualifierRejected:false});renderIdentification();}));}
 else if(result.kind==='qualifier_required'){box.append(note('Does this match what you see?',[result.prompt]));for(const c of result.choices)box.append(button(c.label,()=>{if(!valid()||resolutionKey!==inputsKey())return;Object.assign(state,{qualifierConfirmed:c.id==='yes',qualifierRejected:c.id!=='yes'});renderIdentification();}));}
 else{if(result.kind==='scope_required')box.append(el('h3','Confirm the guide details'),el('p',selected.scope.firmware.length?'This guide needs the current firmware version.':'The selected model needs further confirmation.'));
 else box.append(el('p',selected?.paths.find(p=>p.id===state.pathId)?.symptom||catalog.symptoms.find(s=>s.symptom_id===fields().symptomId)?.label_en||'Other / None of these'));
 const next=button('Continue',viewSolution,'primary');next.id='continue';box.append(next);
 if(selected&&selected.paths.filter(p=>p.directSelectable!==false).length>1)box.append(button('Change condition',()=>{Object.assign(state,{pathId:undefined,qualifierConfirmed:false,qualifierRejected:false});renderIdentification();},'text-button'));
 }
 const needsFirmware=!!selected?.scope.firmware.length;$('scope-details').hidden=!needsFirmware;if(needsFirmware){$('scope-details').append($('more-details'));$('more-details').open=true;}
 $('selection').replaceChildren(box);history.replaceState(marker('identify'),'','#identify');focusResult();
}
function displaySolution(){const result=resolved();if(!result||['choose_symptom','qualifier_required','choose_path'].includes(result.kind)){showIdentify();if(result)renderIdentification();else{clearSelection();setStage('category');}history.replaceState(marker('identify'),'','#identify');return;}
 pageName='solution';$('identify-page').hidden=true;$('solution-page').hidden=false;
 const symptom=catalog.symptoms.find(s=>s.symptom_id===fields().symptomId);$('solution-summary').replaceChildren(el('p',symptom?.label_en||'Other / None of these','issue-summary'),el('p',[mower.model,fields().area,mower.firmware].filter(Boolean).join(' · '),'hint'));
 if(fields().symptomId==='__other__'&&$('other-description').value.trim())$('solution-summary').append(el('p',$('other-description').value.trim(),'other-description'));
 if(selected)renderCard(result);else{clearResult();const box=el('article',undefined,'card');box.append(el('h2',issueTitle),note('Next step with PIE',result.action));$('result').append(box);}status('');focusResult();
}
function viewSolution(){const result=resolved();if(!result){invalidate();clearSelection();setStage('category');return;}if(['choose_symptom','qualifier_required','choose_path'].includes(result.kind)){renderIdentification();return;}history.replaceState(marker('identify'),'','#identify');history.pushState(marker('solution'),'','#solution');displaySolution();}
function restoreNavigation(){const entry=history.state;if(entry?.session===navigationSession&&entry.revision===revision&&entry.page==='solution'&&location.hash==='#solution')displaySolution();else{showIdentify();if(!valid()){clearSelection();setStage('category');}history.replaceState(marker('identify'),'','#identify');}}
window.addEventListener('popstate',restoreNavigation);window.addEventListener('hashchange',()=>{if((pageName==='solution')!==(location.hash==='#solution'))restoreNavigation();});
history.replaceState(marker('identify'),'','#identify');showIdentify();
function renderCard(override){if(!valid()||resolutionKey!==inputsKey()){invalidate();clearSelection();setStage('category');return;}clearResult();const box=el('article',undefined,'card');box.dataset.card=selected.id;const top=el('div',undefined,'card-top');top.append(el('span',selected.code?'ERROR '+selected.code:'SYMPTOM GUIDE','code-label'),button('Edit issue',editIssue,'text-button'));box.append(top,el('h2',selected.message));
 const state=visit(selected);current=override||(state.qualifierRejected?{kind:'escalate',action:['The observed condition does not match this guide. Contact PIE with the exact model, firmware and what happens during mowing and Functional Test.']}:resolveCard(selected,context()));
 if(current.kind==='repair'&&!controlledRepairAllowed(catalog,fields(),selected.id,current.pathId,state.completedRepairs))current={kind:'escalate',action:['Contact PIE to confirm this message and selected symptom.']};
 if(current.kind==='choose_symptom'){box.append(el('h3','What problem do you see?','choices-title'));const choices=el('div',undefined,'choices');for(const c of current.choices)choices.append(button(c.symptom,()=>{Object.assign(state,{pathId:c.id,qualifierConfirmed:false,qualifierRejected:false});renderCard();}));box.append(choices);
 }else if(current.kind==='reported_fixed'){const success=el('div',undefined,'success');success.append(el('h3','You reported it fixed'),el('p',current.message));box.append(success);
 }else if(current.kind==='qualifier_required'){box.append(note('Confirm the observed condition',[current.prompt]));const choices=el('div',undefined,'choices');for(const c of current.choices)choices.append(button(c.label,()=>{Object.assign(state,{qualifierConfirmed:c.id==='yes',qualifierRejected:c.id!=='yes'});renderCard();}));box.append(choices);
 }else if(['escalate','scope_required'].includes(current.kind)){box.append(note(current.kind==='scope_required'?'Confirm the mower details':'Next step with PIE',current.action||['Contact PIE for the current next step.']));if(current.kind==='scope_required'){const details=[];if(selected.scope.models.length)details.push('Guide model: '+selected.scope.models.join(', '));if(selected.scope.firmware.length)details.push('Guide firmware: '+selected.scope.firmware.join(', '));box.append(el('p',details.join(' · '),'hint'));}
 }else if(['repair','check','information'].includes(current.kind)){const grid=el('div',undefined,'answer-grid');const part=el('section',undefined,'part-box');part.append(el('h3','Most likely faulty part / target area'),el('strong',current.part||(current.kind==='information'?'No repair needed for this message':'Start with the observed condition')));if(current.part||current.kind==='information')grid.append(part);for(const [heading,items] of [['What to do',current.action],['After repair / verification',current.verification.steps]]){const block=el('section',undefined,'answer-block');block.append(el('h3',heading));const list=el('ol');for(const text of items)list.append(el('li',text));block.append(list);grid.append(block);}const fallback=el('section',undefined,'fallback');fallback.append(el('h3','Still not fixed'),el('p',current.ifNotFixed.message));grid.append(fallback);box.append(grid);
 const outcome=el('div',undefined,'outcome'),label=el('label',undefined,'check-label'),check=el('input');check.type='checkbox';check.id='verification';label.append(check,el('span','I completed the checks above and confirmed the result.'));const buttons=el('div',undefined,'buttons');const outcomeKey=inputsKey(),outcomeCard=selected,outcomePath=current.pathId;const act=choice=>{if(!valid()||outcomeKey!==inputsKey()||selected!==outcomeCard||current?.pathId!==outcomePath){invalidate();clearSelection();setStage('symptom');return;}const pathId=current.pathId;const next=recordOutcome(selected,pathId,choice,{...context(),verificationComplete:check.checked});if(next.kind==='verification_required'){status(next.message,true);check.focus();return;}if(choice==='not_fixed')state.completedRepairs=[...new Set([...state.completedRepairs,pathId])];if(choice==='returned')state.returned=true;if(next.pathId)state.pathId=next.pathId;else if(!state.pathId)state.pathId=pathId;if(choice!=='fixed')state.qualifierConfirmed=false;renderCard(next);status(choice==='fixed'?'Result shown for this visit only. No case record was changed.':'Use the next step shown below.');focusResult();};buttons.append(button('Fixed',()=>act('fixed'),'primary'),button('Still not fixed',()=>act('not_fixed'),'secondary'));if(current.kind!=='information')buttons.append(button('The issue returned after repair',()=>act('returned'),'text-button'));outcome.append(label,buttons);box.append(outcome);
 }else box.append(note('Next step with PIE',['Contact PIE to confirm the next action.']));
 if(!['choose_symptom','reported_fixed'].includes(current.kind)&&selected.paths.filter(p=>p.directSelectable!==false).length>1)box.append(button('Change symptom',()=>{Object.assign(state,{pathId:undefined,qualifierConfirmed:false,qualifierRejected:false});editIssue();invalidate();renderIdentification();},'text-button change-symptom'));
 $('result').append(box);
}

function firmwareChanged(){mower.firmware=$('firmware').value.trim();resetQualifiers();if(selected||pendingPIE){invalidate();resolutionKey=inputsKey();renderIdentification();}else detailsEdited();}
$('category-form').addEventListener('submit',e=>{e.preventDefault();nextCategory();});
$('model').addEventListener('change',()=>categoryChanged(true));$('observable-area').addEventListener('change',()=>categoryChanged(false));
$('observed-symptom').addEventListener('change',detailsEdited);$('search').addEventListener('input',detailsEdited);$('other-description').addEventListener('input',detailsEdited);$('firmware').addEventListener('input',firmwareChanged);
$('search-form').addEventListener('submit',e=>{e.preventDefault();beginIdentification();});
$('category-back').addEventListener('click',()=>{setStage('category');history.replaceState(marker('identify'),'','#identify');focusResult();});
$('details-back').addEventListener('click',()=>{setStage('symptom');history.replaceState(marker('identify'),'','#identify');focusResult();});$('edit-issue').addEventListener('click',editIssue);
const strings=value=>Array.isArray(value)&&value.every(v=>typeof v==='string');
function validCatalog(data){if(data?.schemaVersion!==2||typeof data.knowledgeVersion!=='string'||!Array.isArray(data.cards)||!Array.isArray(data.symptoms))return false;return data.cards.every(c=>typeof c.id==='string'&&(c.code===null||typeof c.code==='string')&&typeof c.message==='string'&&strings(c.aliases)&&strings(c.scope?.models)&&strings(c.scope?.firmware)&&Array.isArray(c.paths)&&c.paths.length&&c.paths.every(p=>typeof p.id==='string'&&typeof p.symptom==='string'&&['repair','check','information','escalate'].includes(p.kind)&&strings(p.action)&&p.action.length&&strings(p.verification?.steps)&&p.verification.steps.length&&typeof p.ifNotFixed?.message==='string'))&&data.symptoms.every(s=>typeof s.symptom_id==='string'&&/^SYM-0(0[1-9]|1[0-9]|2[0-5])$/.test(s.symptom_id)&&OBSERVABLE_AREAS.includes(s.observable_area)&&typeof s.label_en==='string'&&strings(s.aliases)&&Array.isArray(s.repair_refs)&&s.repair_refs.every(r=>data.cards.some(c=>c.id===r.card_id&&c.paths.some(p=>p.id===r.repair_path_id))));}

try{const response=await fetch('./knowledge.json',{cache:'no-store'});if(!response.ok)throw new Error('Guide load failed');const data=await response.json();if(!validCatalog(data))throw new Error('Invalid guide data');catalog=data;
 for(const model of controlledModels(catalog))$('model').append(new Option(model,model));for(const area of OBSERVABLE_AREAS)$('observable-area').append(new Option(area,area));
 for(const id of ['model','observable-area','observed-symptom','firmware','category-next','search-button','search'])$(id).disabled=false;status('');
}catch{catalog=null;status('Guides could not load. Restart the local pilot, or contact PIE for help.',true);}
