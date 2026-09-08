import fs from 'node:fs';
import {searchCards} from '../src/engine.mjs';
const data=()=>JSON.parse(fs.readFileSync(new URL('../dist/knowledge.json',import.meta.url),'utf8'));
export async function enterSymptom(page,id){
 const symptom=data().symptoms.find(s=>s.symptom_id===id);
 await page.locator('#search').fill('');
 await page.locator('#observed-symptom').fill(symptom.label_en);
 await page.locator('#observed-symptom').press('Enter');
}
export async function enterFirmware(page,value){
 if(!await page.locator('#firmware').isVisible())await page.locator('#more-details summary').click();
 await page.locator('#firmware').fill(value);
}
export async function enterSearch(page,q){
 const catalog=data(),card=searchCards(catalog.cards,q).matches[0];
 const observation=catalog.symptoms.find(s=>s.repair_refs.some(r=>r.card_id===card?.id));
 await page.locator('#observed-symptom').fill(observation?.label_en||'Observed issue with this message');
 await page.locator('#search').fill(q);await page.locator('#search').press('Enter');
}
