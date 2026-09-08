import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {createPreview} from '../scripts/serve.mjs';
import {build} from '../scripts/build.mjs';
import {projectAgentCatalog,OBSERVABLE_AREAS} from '../src/engine.mjs';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'C:/Users/Reggie/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const artifact=path.join(root,'artifacts');fs.mkdirSync(artifact,{recursive:true});
const canonical=JSON.parse(fs.readFileSync(path.join(root,'data/canonical.json'),'utf8'));
const publicData=projectAgentCatalog(canonical);
await build();
const server=await createPreview({port:0});const base='http://127.0.0.1:'+server.address().port;
const browser=await chromium.launch({headless:true,executablePath:process.env.PILOT_BROWSER||'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
const observations=[],errors=[],requests=[];
const run=async(name,fn)=>{await fn();observations.push(name);console.log('PASS '+name);};
async function search(page,q){await page.locator('#search').fill(q);await page.locator('#search').press('Enter');}
async function contains(page,text){await page.getByText(text,{exact:false}).first().waitFor({timeout:5000});}
async function noOverflow(page){assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true,'horizontal overflow');}
async function absentAction(page){assert.equal(await page.getByRole('heading',{name:'What to do',exact:true}).count(),0);}
async function symptom(page,id){const s=publicData.symptoms.find(s=>s.symptom_id===id);await page.locator(`[data-area="${s.observable_area}"]`).click();await page.locator(`[data-symptom="${id}"]`).click();}
async function scope(page){await page.locator('#model').selectOption('LUBA 2 5000X');await page.locator('#firmware').fill('1.30.31.10');}
async function fresh(viewport={width:1366,height:768},fixture){const context=await browser.newContext({viewport,reducedMotion:'reduce'});const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>requests.push(r.url()));if(fixture)await page.route('**/knowledge.json',route=>route.fulfill({json:fixture}));await page.goto(base);return {context,page};}
try {
 for(const [name,viewport] of [['desktop',{width:1366,height:768}],['wide-desktop',{width:1920,height:1080}],['mobile',{width:390,height:844}]]){
  const {context,page}=await fresh(viewport);
  await run(name+' home: persistent model, search and ten areas together',async()=>{
   assert.equal(await page.locator('#model').count(),1,'global model selector must exist');await page.locator('#search-button:enabled').waitFor();
   assert.equal(await page.locator('[data-area]').count(),10);assert.equal(await page.locator('[data-symptom]').count(),0);
   assert.deepEqual(await page.locator('#model option').allTextContents(),['Select model / unknown',...[...new Set(publicData.cards.flatMap(c=>c.scope.models))].sort(),'Other model']);
   if(viewport.width>1000)for(const selector of ['#model','#search','[data-area]'])for(const item of await page.locator(selector).all()){const b=await item.boundingBox();assert.ok(b.y>=0&&b.y+b.height<=viewport.height,selector+' above fold');}
   await noOverflow(page);await page.screenshot({path:path.join(artifact,name+'-home.png'),fullPage:true});
  });
  await run(name+' 25 area-only symptoms and ten safe escapes',async()=>{
   const seen=[];
   for(const area of OBSERVABLE_AREAS){await page.locator(`[data-area="${area}"]`).click();const expected=publicData.symptoms.filter(s=>s.observable_area===area);assert.deepEqual(await page.locator('[data-symptom]').evaluateAll(ns=>ns.map(n=>n.dataset.symptom)),expected.map(s=>s.symptom_id));seen.push(...expected.map(s=>s.symptom_id));await page.getByRole('button',{name:'None of these / Other issue',exact:true}).click();await contains(page,'Next step with PIE');await absentAction(page);}
   assert.equal(new Set(seen).size,25);assert.equal(await page.locator('[data-symptom="SYM-026"],[data-symptom="SYM-027"],[data-symptom="SYM-028"]').count(),0);
  });
  await run(name+' 1202 physical guard and frozen repair survive model change',async()=>{
   await search(page,'1202');await page.getByRole('button',{name:'There is debris or a physical blockage',exact:true}).click();await contains(page,'Power off the mower');
   await page.getByRole('button',{name:'Change symptom',exact:true}).click();await page.getByRole('button',{name:'Both cutting discs are free, but the error remains',exact:true}).click();await contains(page,'Next step with PIE');await scope(page);await absentAction(page);assert.equal((await page.locator('#result').innerText()).includes('Upper Shell Adapter Cable'),false);
  });
  await run(name+' exact message information, ordered card, verification-gated local fixed',async()=>{
   await search(page,'Stereo self-calibration succeeded and the parameters were restored.');await page.getByRole('button',{name:'The mower works normally; no other fault is present',exact:true}).click();await contains(page,'No repair needed for this message');
   assert.deepEqual(await page.locator('#result h3').allTextContents(),['Most likely faulty part / target area','What to do','After repair / verification','Still not fixed']);
   await page.getByRole('button',{name:'Fixed',exact:true}).click();await contains(page,'Complete the after-repair checks first.');await page.locator('#verification').check();await page.getByRole('button',{name:'Fixed',exact:true}).click();await contains(page,'You reported it fixed');await contains(page,'does not close a case');
  });
  await run(name+' signed codes distinct; unsigned 2000303 requests logs',async()=>{
   await search(page,'−552');await contains(page,'ERROR -552');await search(page,'-2000303');await contains(page,'ERROR -2000303');const signed=await page.locator('#result').innerText();await search(page,'2000303');await contains(page,'ERROR 2000303');const unsigned=await page.locator('#result').innerText();assert.notEqual(signed,unsigned);assert.match(unsigned,/fresh log/i);assert.equal(unsigned.includes('No repair needed for this message'),false);
  });
  await run(name+' fuzzy explicit candidates; unsupported injection-safe text; historical withholding',async()=>{
   await search(page,'port disconnected');await contains(page,'Which message matches?');assert.ok(await page.locator('#result button.choice').count()>=2);await absentAction(page);await page.getByRole('button',{name:/1500.*Chassis data/}).click();await contains(page,'Next step with PIE');
   await search(page,'999999');await contains(page,'No guide found');await absentAction(page);await search(page,'<img src=x onerror=alert(1)>');assert.equal(await page.locator('#result img').count(),0);await absentAction(page);
   await search(page,'1000022');await contains(page,'current advice from PIE');assert.equal((await page.locator('#result').innerText()).includes('2.3.30.26'),false);
  });
  await run(name+' safe symptom and code/symptom canonical parity',async()=>{
   await symptom(page,'SYM-007');await contains(page,'Next step with PIE');await absentAction(page);await search(page,'5501');const direct=await page.locator('#result').innerText();await symptom(page,'SYM-021');assert.equal(await page.locator('#result').innerText(),direct);assert.equal(await page.locator('#search').inputValue(),'','symptom entry clears the previous code so it cannot mislabel the new guide');
  });
  await run(name+' real symptom repair needs exact scope and qualifier; model switch clears action',async()=>{
   await page.locator('#model').selectOption('');await symptom(page,'SYM-004');await contains(page,'Confirm the mower details');await absentAction(page);await scope(page);await contains(page,'Yes, this matches');await absentAction(page);
   await page.getByRole('button',{name:'Yes, this matches',exact:true}).click();await contains(page,'Cutting control software');await contains(page,'1.30.29.19');for(const text of ['Communication Check','Auto Map Run','three reports','Connect Checking screenshot'])await contains(page,text);await noOverflow(page);await page.evaluate(()=>window.scrollTo(0,0));const contextBounds=await page.locator('.context-panel').boundingBox();const searchBounds=await page.locator('.search-panel').boundingBox();assert.ok(contextBounds.y+contextBounds.height<=searchBounds.y,'mower context must not overlap search at page top');await page.screenshot({path:path.join(artifact,name+'-repair.png'),fullPage:true});
   await page.locator('#model').selectOption('__other__');await absentAction(page);assert.equal(await page.locator('#firmware').inputValue(),'');await scope(page);await contains(page,'Yes, this matches');await absentAction(page);
   await page.getByRole('button',{name:'No / unsure — contact PIE',exact:true}).click();await contains(page,'Next step with PIE');await absentAction(page);await page.locator('#firmware').fill('9.9');await absentAction(page);
  });
  await run(name+' 1008 avoids speculative keypad; failed/returned persist across searches and models',async()=>{
   await search(page,'1008');await page.getByRole('button',{name:'The workshop cannot reproduce it',exact:true}).click();await contains(page,'Do not replace the keypad board');await contains(page,'Functional Test');await contains(page,'Connect Checking screenshot');
   await page.getByRole('button',{name:'Still not fixed',exact:true}).click();await contains(page,'Next step with PIE');await search(page,'1008');await contains(page,'Next step with PIE');await absentAction(page);
   await page.getByRole('button',{name:'Change symptom',exact:true}).click();await page.getByRole('button',{name:'Something pressed the top STOP button',exact:true}).click();await page.getByRole('button',{name:'The issue returned after repair',exact:true}).click();await contains(page,'issue returned after repair');await search(page,'5510');await search(page,'1008');await page.locator('#model').selectOption('__other__');await contains(page,'issue returned after repair');await absentAction(page);await noOverflow(page);
  });
  await context.close();
 }
 await run('real repair failure persists across symptom and exact message entry',async()=>{
  const {context,page}=await fresh();await page.locator('#search-button:enabled').waitFor();await scope(page);await symptom(page,'SYM-004');await page.getByRole('button',{name:'Yes, this matches',exact:true}).click();await page.getByRole('button',{name:'Still not fixed',exact:true}).click();await contains(page,'Next step with PIE');await search(page,'Cutting disc does not spin in Functional Test');await absentAction(page);await symptom(page,'SYM-004');await absentAction(page);await page.locator('#model').selectOption('__other__');await scope(page);await absentAction(page);await context.close();
 });
 await run('wrong firmware withholds repair; returned real repair persists across both routes',async()=>{
  const {context,page}=await fresh();await page.locator('#search-button:enabled').waitFor();await page.locator('#model').selectOption('LUBA 2 5000X');await page.locator('#firmware').fill('1.30.31.11');await symptom(page,'SYM-004');await contains(page,'Confirm the mower details');await absentAction(page);assert.equal(await page.getByRole('button',{name:'Yes, this matches',exact:true}).count(),0);await page.locator('#firmware').fill('1.30.31.10');await page.getByRole('button',{name:'Yes, this matches',exact:true}).click();await contains(page,'Cutting control software');await page.getByRole('button',{name:'The issue returned after repair',exact:true}).click();await contains(page,'issue returned after repair');await search(page,'Cutting disc does not spin in Functional Test');await contains(page,'issue returned after repair');await symptom(page,'SYM-004');await contains(page,'issue returned after repair');await page.locator('#model').selectOption('__other__');await scope(page);await contains(page,'issue returned after repair');await absentAction(page);await context.close();
 });
 await run('synthetic non-1202 cable → board → PIE without resetting failures',async()=>{
  const fixture=structuredClone(publicData);const card=structuredClone(fixture.cards.find(c=>c.id==='sym-cutting-functional-test'));card.id='fixture-repair';card.code='999001';card.message='Synthetic replacement contract';card.scope={status:'confirmed',models:['TEST MODEL'],firmware:['TEST VERSION']};
  const first={...card.paths[0],id:'cable',symptom:'Cable condition confirmed',part:'Fixture cable',action:['Replace fixture cable.'],qualifier:undefined,ifNotFixed:{kind:'path',pathId:'board',message:'Use the confirmed board step.'}};const second={...first,id:'board',directSelectable:false,part:'Fixture board',action:['Replace fixture board.'],ifNotFixed:{kind:'escalate',message:'Contact PIE. Do not repeat the replacement.'}};card.paths=[first,second];fixture.cards.push(card);
  const {context,page}=await fresh({width:1366,height:768},fixture);await page.locator('#search-button:enabled').waitFor();await search(page,'999001');await contains(page,'Confirm the mower details');await page.locator('#model').selectOption('TEST MODEL');await page.locator('#firmware').fill('TEST VERSION');await contains(page,'Fixture cable');await page.getByRole('button',{name:'Still not fixed',exact:true}).click();await contains(page,'Fixture board');await search(page,'999001');await contains(page,'Fixture board');await page.getByRole('button',{name:'Still not fixed',exact:true}).click();await contains(page,'Next step with PIE');await search(page,'999001');await page.locator('#model').selectOption('__other__');await absentAction(page);await page.locator('#model').selectOption('TEST MODEL');await page.locator('#firmware').fill('TEST VERSION');await absentAction(page);await context.close();
 });
 for(const [name,body,status] of [['unavailable',null,503],['invalid schema',{schemaVersion:88,cards:[],symptoms:[]},200]])await run(name+' catalog disables both entry routes',async()=>{
  const {context,page}=await fresh();await page.route('**/knowledge.json',route=>route.fulfill(body?{json:body}:{status,body:'Unavailable'}));await page.reload();await contains(page,'Guides could not load');assert.equal(await page.locator('#search-button').isDisabled(),true);assert.equal(await page.locator('[data-area]:enabled').count(),0);await search(page,'1202');await absentAction(page);await context.close();
 });
 await run('public payload excludes candidate/internal metadata and raw endpoint',async()=>{
  const {context,page}=await fresh();await page.locator('#search-button:enabled').waitFor();const payload=await (await page.request.get(base+'/knowledge.json')).text();assert.doesNotMatch(payload,/label_cn|evidence_state|sourceRefs|raw_reference|STABLE_OPERATIONAL_GUIDANCE|CONFLICTING_EVIDENCE/);assert.equal(publicData.symptoms.length,25);assert.equal((await page.request.get(base+'/data/canonical.json')).status(),404);await context.close();
 });
 assert.deepEqual(errors,[]);assert.deepEqual(requests.filter(url=>!url.startsWith(base)&&!url.startsWith('data:')),[]);
 fs.writeFileSync(path.join(artifact,'browser-verification.json'),JSON.stringify({passed:observations.length,checks:observations,viewports:['1366x768','1920x1080','390x844'],pageErrors:errors,externalRequests:0,syntheticRepairFixtureNotPublished:true,ownedServerClosedInFinally:true},null,2)+'\n');console.log('BROWSER GREEN '+observations.length+' checks');
} finally {await browser.close();await new Promise(resolve=>server.close(resolve));}
