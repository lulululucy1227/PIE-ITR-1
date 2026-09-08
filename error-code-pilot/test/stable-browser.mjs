import fs from 'node:fs';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {build} from '../scripts/build.mjs';
import {createPreview} from '../scripts/serve.mjs';
import {enterSymptom,enterSearch,category,confirm,solve,identify,data} from './input-helpers.mjs';
const {chromium}=createRequire(import.meta.url)('C:/Users/Reggie/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
await build();const catalog=data(),cards=catalog.cards.filter(c=>c.id.startsWith('guide-'));
const server=await createPreview({port:0}),base='http://127.0.0.1:'+server.address().port;
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'}),checks=[],errors=[],external=[];
try{
 for(const width of [1366,1920]){
  const context=await browser.newContext({viewport:{width,height:width===1366?768:1080}}),page=await context.newPage();page.setDefaultTimeout(5000);page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(!r.url().startsWith(base)&&!r.url().startsWith('data:'))external.push(r.url());});
  for(const card of cards){
   await page.goto(base);await page.locator('#model:enabled').waitFor();const s=catalog.symptoms.find(s=>s.repair_refs.some(r=>r.card_id===card.id));
   await enterSymptom(page,s.symptom_id,card.scope.models[0]);await identify(page);assert.doesNotMatch(await page.locator('#identify-page').innerText(),/Most likely faulty part|What to do|After repair|STABLE_OPERATIONAL_GUIDANCE|REP-[A-Z]+/);
   for(const action of card.paths[0].action)assert.ok(!(await page.locator('#identify-page').textContent()).includes(action));await confirm(page);await solve(page);
   assert.equal(await page.locator('#result article').getAttribute('data-card'),card.id);for(const action of card.paths[0].action)assert.ok((await page.locator('#result').innerText()).includes(action));
   assert.equal(await page.locator('#result .part-box').count(),card.paths[0].part?1:0);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
   await page.screenshot({path:`artifacts/stable-${width}-${card.id}.png`,fullPage:true});
   await page.goBack();await identify(page);assert.equal(await page.locator('#model').inputValue(),card.scope.models[0]);assert.equal(await page.locator('#observed-symptom').inputValue(),s.symptom_id);
   await enterSearch(page,card.message,s.symptom_id,card.scope.models[0]);await confirm(page);await solve(page);assert.equal(await page.locator('#result article').getAttribute('data-card'),card.id);
   await page.getByRole('button',{name:'Still not fixed',exact:true}).click();await page.getByRole('heading',{name:'Next step with PIE',exact:true}).waitFor();await page.goBack();await solve(page);assert.equal(await page.locator('#result .answer-grid').count(),0);
   checks.push(width+' '+card.id+' controlled scope/identify/action/message/parity/failure');console.log('PASS '+checks.at(-1));
  }
  await context.close();
 }
 const page=await browser.newPage();await page.goto(base);await page.locator('#model:enabled').waitFor();await enterSymptom(page,'SYM-004','LUBA 2');await page.getByRole('button',{name:'No / unsure — contact PIE',exact:true}).click();await solve(page);await page.getByRole('heading',{name:'Next step with PIE',exact:true}).waitFor();assert.equal(await page.locator('#result .answer-grid').count(),0);checks.push('non1202 operation qualifier rejection remains PIE');await page.close();
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);fs.writeFileSync('artifacts/stable-browser-verification.json',JSON.stringify({passed:checks.length,checks,pageErrors:errors,externalRequests:0},null,2));console.log('STABLE BROWSER GREEN '+checks.length);
}finally{await browser.close();await new Promise(r=>server.close(r));}
