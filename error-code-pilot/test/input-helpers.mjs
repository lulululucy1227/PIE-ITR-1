import fs from 'node:fs';
import {searchCards,controlledSymptoms,controlledModels,controlledReferences} from '../src/engine.mjs';
export const data=()=>JSON.parse(fs.readFileSync(new URL('../dist/knowledge.json',import.meta.url),'utf8'));
export async function category(page){
 if(await page.locator('#solution-page').isVisible())await page.locator('#edit-issue').click();
 if(await page.locator('#confirm-stage').isVisible())await page.locator('#details-back').click();
 if(await page.locator('#symptom-stage').isVisible())await page.locator('#category-back').click();
}
export async function choose(page,id,model){
 const catalog=data(),s=catalog.symptoms.find(s=>s.symptom_id===id);
 await category(page);
 const previous=await page.locator('#model').inputValue();
 const fits=m=>controlledSymptoms(catalog,{model:m,area:s.observable_area}).some(x=>x.symptom_id===id);
 const target=model||(fits(previous)?previous:controlledModels(catalog).find(fits));
 if(previous!==target)await page.locator('#model').selectOption(target);
 await page.locator('#observable-area').selectOption(s.observable_area);await page.locator('#category-next').click();await page.locator('#observed-symptom').selectOption(id);
}
export async function enterSymptom(page,id,model){await choose(page,id,model);await page.locator('#search').fill('');const catalog=data(),symptom=catalog.symptoms.find(s=>s.symptom_id===id),m=await page.locator('#model').inputValue();const refs=controlledReferences(catalog,{model:m,area:symptom.observable_area,symptomId:id});if(refs.some(r=>{const c=catalog.cards.find(c=>c.id===r.card_id);return c.scope.firmware.length||c.paths.find(p=>p.id===r.repair_path_id).qualifier;}))await page.locator('#search-button').click();}
export async function enterFirmware(page,value){if(!await page.locator('#firmware').isVisible())await page.locator('#more-details summary').click();await page.locator('#firmware').fill(value);}
export async function enterSearch(page,q,id,model){
 const catalog=data(),card=searchCards(catalog.cards,q).matches[0];
 const symptom=id||catalog.symptoms.find(s=>s.repair_refs.some(r=>r.card_id===card?.id))?.symptom_id||(card?.code==='1202'?'SYM-004':'SYM-021');
 await choose(page,symptom,model);await page.locator('#search').fill(q);await page.locator('#search-button').click();
 const exact=searchCards(catalog.cards,q);if(exact.matches.length===1&&exact.kind.startsWith('exact'))await page.getByRole('button',{name:(card.code?card.code+' · ':'')+card.message,exact:true}).click();
}
export async function confirm(page){const yes=page.getByRole('button',{name:'Yes, this matches',exact:true});if(await yes.count())await yes.click();}
export async function solve(page){if(await page.locator('#symptom-stage').isVisible())await page.locator('#search-button').click();if(!await page.locator('#solution-page').isVisible())await page.locator('#continue').click();await page.locator('#solution-page:visible').waitFor();}
export async function identify(page){await page.locator('#identify-page:visible').waitFor();if(await page.locator('#result').innerText())throw Error('Solution content present during identification');}
