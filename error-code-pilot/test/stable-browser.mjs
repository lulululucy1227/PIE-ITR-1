import {enterSymptom,enterFirmware,enterSearch} from './input-helpers.mjs';
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {build} from '../scripts/build.mjs';
import {createPreview} from '../scripts/serve.mjs';
const require=createRequire(import.meta.url),{chromium}=require(process.env.PLAYWRIGHT_MODULE||'C:/Users/Reggie/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');await build();
const server=await createPreview({port:0}),base='http://127.0.0.1:'+server.address().port;
const data=JSON.parse(fs.readFileSync(path.join(root,'dist/knowledge.json'))),cards=data.cards.filter(c=>c.id.startsWith('guide-'));
assert.equal(cards.length,10);
const browser=await chromium.launch({headless:true,executablePath:process.env.PILOT_BROWSER||'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'}),checks=[],errors=[],external=[];
async function identify(page,card){await page.locator('#identify-page:visible').waitFor();assert.equal(await page.locator('#result').innerText(),'');const text=await page.locator('#identify-page').innerText();assert.doesNotMatch(text,/Most likely faulty part|What to do|After repair|STABLE_OPERATIONAL_GUIDANCE|REP-[A-Z]+/);if(card)for(const action of card.paths[0].action)assert.ok(!text.includes(action),card.id);}
async function selectSymptom(page,card){const s=data.symptoms.find(s=>s.repair_refs.some(r=>r.card_id===card.id));await enterSymptom(page,s.symptom_id);if(s.repair_refs.length>1)await page.getByRole('button',{name:card.paths[0].symptom,exact:true}).click();}
async function confirm(page,card){if(card.paths[0].qualifier)await page.getByRole('button',{name:'Yes, this matches',exact:true}).click();}
async function continueToSolution(page,card){await identify(page,card);await page.locator('#continue').click();await page.locator('#solution-page:visible').waitFor();}
try{
 for(const width of [1366,1920]){
  const context=await browser.newContext({viewport:{width,height:width===1366?768:1080}}),page=await context.newPage();page.setDefaultTimeout(5000);page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(!r.url().startsWith(base)&&!r.url().startsWith('data:'))external.push(r.url());});
  for(const card of cards){
   await page.goto(base);await page.locator('#search-button:enabled').waitFor();await selectSymptom(page,card);await identify(page,card);
   await page.locator('#model').fill('__other__');await continueToSolution(page,card);assert.equal(await page.locator('#result .answer-grid').count(),0,'unknown model');
   await page.locator('#edit-issue').click();await page.locator('#model').fill(card.scope.models[0]);await confirm(page,card);await continueToSolution(page,card);
   assert.equal(await page.locator('#result article').getAttribute('data-card'),card.id);for(const action of card.paths[0].action)assert.ok((await page.locator('#result').innerText()).includes(action));
   assert.equal(await page.locator('#result .part-box').count(),card.paths[0].part?1:0,'checks must not manufacture a faulty-part conclusion');
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
   await page.screenshot({path:path.join(root,'artifacts',`stable-${width}-${card.id}.png`),fullPage:true});
   await page.goBack();await identify(page,card);assert.equal(await page.locator('#model').inputValue(),card.scope.models[0]);
   await page.locator('#search').fill(card.message);await page.locator('#search').press('Enter');await confirm(page,card);await continueToSolution(page,card);assert.equal(await page.locator('#result article').getAttribute('data-card'),card.id,'exact message and symptom converge');
   await page.getByRole('button',{name:'Still not fixed',exact:true}).click();await page.getByRole('heading',{name:'Next step with PIE',exact:true}).waitFor();await page.goBack();await identify(page,card);await continueToSolution(page,card);assert.equal(await page.locator('#result .answer-grid').count(),0,'failed step cannot repeat');
   checks.push(width+' '+card.id+' scope/identify/action/verification/message/parity/failure');console.log('PASS '+checks.at(-1));
  }
  await context.close();
 }
 // The new second SYM004 branch must survive a model edit before branch selection.
 const context=await browser.newContext(),page=await context.newPage();page.setDefaultTimeout(5000);await page.goto(base);await page.locator('#search-button:enabled').waitFor();await enterSymptom(page,'SYM-004');await page.locator('#model').fill('LUBA 2');await page.getByRole('button',{name:'The cutting problem occurs during actual mowing or manual operation',exact:true}).waitFor();await page.getByRole('button',{name:'The cutting problem occurs during actual mowing or manual operation',exact:true}).click();await page.getByRole('button',{name:'No / unsure — contact PIE',exact:true}).click();await continueToSolution(page);await page.getByRole('heading',{name:'Next step with PIE',exact:true}).waitFor();assert.equal(await page.locator('#result .answer-grid').count(),0);await context.close();checks.push('multi-path selection survives model edits; non1202 qualifier rejection remains PIE');
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
 fs.writeFileSync(path.join(root,'artifacts/stable-browser-verification.json'),JSON.stringify({passed:checks.length,checks,viewports:['1366x768','1920x1080'],pageErrors:errors,externalRequests:0,ownedServerClosedInFinally:true},null,2));console.log('STABLE BROWSER GREEN '+checks.length);
}finally{await browser.close();await new Promise(r=>server.close(r));}
