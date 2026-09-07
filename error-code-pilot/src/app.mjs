import {searchCards,resolveCard,recordOutcome} from './engine.mjs';
const $=id=>document.getElementById(id);
let cards=[],selected=null,context={},current=null,lastSearch=null;
function el(tag,text,className) {const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(className)node.className=className;return node;}
function button(text,action,className='choice'){const n=el('button',text,className);n.type='button';n.addEventListener('click',action);return n;}
function status(text){$('status').textContent=text;}
function focusResult(){$('result').focus({preventScroll:true});$('result').scrollIntoView({block:'nearest',behavior:'instant'});}
function clearResult(){$('result').replaceChildren();$('welcome').hidden=true;document.body.classList.add('has-result');}
function note(title,lines){const box=el('div',undefined,'alert');box.append(el('h3',title));const list=el('ul');for(const s of lines)list.append(el('li',s));box.append(list);return box;}
function showSearch() {
  selected=null;context={};current=null;
  const result=searchCards(cards,$('search').value);lastSearch=result;clearResult();
  if(result.kind==='empty'){status('Enter an error code or message.');return;}
  if(result.kind==='unsupported'){
    status('No guide found for that code or message.');
    $('result').append(note('Ask PIE for the next step',['Keep the exact error code, mower model and what happened. Include any repair already tried.','Do not choose a similar code as a replacement instruction.']));
    focusResult();return;
  }
  if(result.matches.length===1&&result.kind.startsWith('exact')) {openCard(result.matches[0]);return;}
  status('Possible matches — select the exact message you see.');
  const box=el('div',undefined,'card');box.append(el('h2','Which message matches?'));
  const choices=el('div',undefined,'choices');
  for(const c of result.matches){const n=button('',()=>openCard(c));n.append(el('strong',c.code),el('span',c.message));choices.append(n);}
  box.append(choices);$('result').append(box);focusResult();
}
function openCard(card) {
  selected=card;context={};current=null;renderCard();
  status('Guide found. Check the symptom before taking action.');focusResult();
}
function renderCard(resultOverride) {
  clearResult();
  const box=el('article',undefined,'card');
  const top=el('div',undefined,'card-top');top.append(el('span','ERROR '+selected.code,'code-label'),button('New search',()=>{$('result').replaceChildren();selected=null;context={};current=null;$('welcome').hidden=false;document.body.classList.remove('has-result');status('Ready to find a guide.');$('search').focus();},'text-button'));
  box.append(top,el('h2',selected.message));
  const scoped=selected.scope.status==='confirmed';
  if(scoped&&selected.lifecycle==='CURRENT'&&selected.paths.some(p=>p.kind==='repair')){
    const row=el('div',undefined,'scope-row');
    const addSelect=(label,key,values)=>{
      const wrap=el('label',label),input=el('select');input.id='scope-'+key;input.append(new Option('Select '+label.toLowerCase(),''));
      values.forEach(v=>input.append(new Option(v,v)));input.value=context[key]||'';
      input.addEventListener('change',()=>{context={...context,[key]:input.value,verificationComplete:false};renderCard();});
      wrap.append(input);row.append(wrap);
    };
    addSelect('Mower model','model',selected.scope.models);
    if(selected.scope.firmware.length)addSelect('Firmware version','firmware',selected.scope.firmware);
    box.append(row);
  } else if(scoped) box.append(el('p','Documented model: '+selected.scope.models.join(', '),'hint'));
  current=resultOverride||resolveCard(selected,context);
  if(current.kind==='choose_symptom'){
    box.append(el('h3','What problem do you see?','choices-title'));
    const list=el('div',undefined,'choices');
    current.choices.forEach(c=>list.append(button(c.symptom,()=>{context={...context,pathId:c.id,verificationComplete:false};renderCard();})));
    box.append(list);
  } else if(current.kind==='reported_fixed') {
    const success=el('div',undefined,'success');success.append(el('h3','You reported it fixed'),el('p',current.message));box.append(success);
  } else if(['escalate','scope_required'].includes(current.kind)) {
    box.append(note(current.kind==='scope_required'?'Confirm the mower details':'Next step with PIE',current.action||['Contact PIE for the current next step.']));
    if(selected.paths.filter(p=>p.directSelectable!==false).length>1)box.append(button('Change symptom',()=>{context={...context,pathId:undefined,verificationComplete:false};renderCard();},'text-button'));
  } else {
    if(selected.paths.filter(p=>p.directSelectable!==false).length>1)box.append(button('Change symptom',()=>{context={...context,pathId:undefined,verificationComplete:false};renderCard();},'text-button'));
    const grid=el('div',undefined,'answer-grid'),part=el('div',undefined,'part-box');
    part.append(el('h3',current.kind==='repair'?'Most likely faulty part':'Repair guidance'),el('strong',current.part||(current.kind==='information'?'No repair needed for this message':'Start with the observed condition')));
    grid.append(part);
    for(const [heading,items] of [['What to do',current.action],['After repair',current.verification.steps]]){
      const block=el('section',undefined,'answer-block');block.append(el('h3',heading));
      const list=el('ol');items.forEach(s=>list.append(el('li',s)));block.append(list);grid.append(block);
    }
    box.append(grid);
    const outcome=el('div',undefined,'outcome'),label=el('label',undefined,'check-label'),check=el('input');check.type='checkbox';check.id='verification';check.checked=false;
    label.append(check,el('span','I completed the checks above and confirmed the result.'));
    const buttons=el('div',undefined,'buttons');
    const act=choice=>{
      const pathId=current.pathId;
      const next=recordOutcome(selected,pathId,choice,{...context,verificationComplete:check.checked});
      if(next.kind==='verification_required'){status(next.message);$('status').classList.add('error');check.focus();return;}
      $('status').classList.remove('error');
      const failed=choice==='not_fixed'?[...new Set([...(context.completedRepairs||[]),pathId])]:context.completedRepairs||[];
      context={...context,completedRepairs:failed,returned:context.returned||choice==='returned',pathId:next.pathId||context.pathId,verificationComplete:false};
      renderCard(next);status(choice==='fixed'?'Result shown for this visit only. No case record was changed.':'Use the next step shown below.');focusResult();
    };
    buttons.append(button('Fixed',()=>act('fixed'),'primary'),button('Still not fixed',()=>act('not_fixed'),'secondary'));
    if(current.kind!=='information')buttons.append(button('The issue returned after repair',()=>act('returned'),'text-button'));
    outcome.append(label,buttons);box.append(outcome);
  }
  $('result').append(box);
}
$('search-form').addEventListener('submit',e=>{e.preventDefault();$('status').classList.remove('error');showSearch();});
document.querySelectorAll('[data-code]').forEach(b=>{b.disabled=true;b.addEventListener('click',()=>{$('search').value=b.dataset.code;showSearch();});});
try {
  const response=await fetch('./knowledge.json',{cache:'no-store'});
  if(!response.ok)throw new Error('Guide load failed');
  const data=await response.json();
  if(data.schemaVersion!==1||!Array.isArray(data.cards)||!data.cards.every(c=>typeof c.message==='string'&&Array.isArray(c.paths)))throw new Error('Invalid guide data');
  cards=data.cards;$('search-button').disabled=false;document.querySelectorAll('[data-code]').forEach(b=>b.disabled=false);
  status('Ready · '+cards.length+' selected guides');
} catch {
  status('Guides could not load. Restart the local pilot, or contact PIE for help.');$('status').classList.add('error');
}
