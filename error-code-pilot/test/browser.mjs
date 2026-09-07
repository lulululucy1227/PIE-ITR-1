import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {createPreview} from '../scripts/serve.mjs';
import {build} from '../scripts/build.mjs';
import {projectAgentCatalog} from '../src/engine.mjs';
const require=createRequire(import.meta.url);
const playwrightPath=process.env.PLAYWRIGHT_MODULE||'C:/Users/Reggie/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright';
const {chromium}=require(playwrightPath);
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const artifact=path.join(root,'artifacts');fs.mkdirSync(artifact,{recursive:true});
await build();
const server=await createPreview({port:0});
const base='http://127.0.0.1:'+server.address().port;
const browser=await chromium.launch({headless:true,executablePath:process.env.PILOT_BROWSER||'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
const observations=[],errors=[],requests=[];
const run=async(name,fn)=>{await fn();observations.push(name);console.log('PASS '+name);};
async function search(page,q){await page.locator('#search').fill(q);await page.locator('#search').press('Enter');}
async function contains(page,text){await page.getByText(text,{exact:false}).first().waitFor();}
async function noOverflow(page){assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true,'horizontal overflow');}
try {
 for(const [name,viewport] of [['desktop',{width:1366,height:1000}],['mobile',{width:390,height:844}],['small-mobile',{width:320,height:740}]]){
  const context=await browser.newContext({viewport,reducedMotion:'reduce'});
  const page=await context.newPage();
  page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>requests.push(r.url()));
  await page.goto(base);await page.locator('#search-button:enabled').waitFor();
  await run(name+' landing and layout',async()=>{await noOverflow(page);await page.screenshot({path:path.join(artifact,name+'-home.png'),fullPage:true});});
  await run(name+' exact code → symptom → safe scope fallback',async()=>{
   await search(page,'1202');await page.getByRole('button',{name:'Both cutting discs are free, but the error remains',exact:true}).click();
   await contains(page,'Next step with PIE');assert.equal(await page.getByRole('heading',{name:'Most likely faulty part'}).count(),0);await noOverflow(page);
  });
  await run(name+' exact message → information → verification-gated outcome',async()=>{
   await search(page,'Stereo self-calibration succeeded and the parameters were restored.');
   await page.getByRole('button',{name:'The mower works normally; no other fault is present',exact:true}).click();
   await contains(page,'No repair needed for this message');
   await page.getByRole('button',{name:'Fixed',exact:true}).click();await contains(page,'Complete the after-repair checks first.');
   await page.locator('#verification').check();await page.getByRole('button',{name:'Fixed',exact:true}).click();
   await contains(page,'You reported it fixed');await contains(page,'does not close a case');
  });
  await run(name+' symptom switch, failed and returned branches',async()=>{
   await search(page,'1008');await page.getByRole('button',{name:'The workshop cannot reproduce it',exact:true}).click();
   await contains(page,'Do not replace the keypad board');await page.screenshot({path:path.join(artifact,name+'-checks.png'),fullPage:true});
   await page.getByRole('button',{name:'Still not fixed',exact:true}).click();await contains(page,'Next step with PIE');
   await search(page,'1008');await page.getByRole('button',{name:'Something pressed the top STOP button',exact:true}).click();
   await page.getByRole('button',{name:'The issue returned after repair',exact:true}).click();await contains(page,'issue returned after repair');
  });
  await run(name+' fuzzy candidates require explicit selection',async()=>{
   await search(page,'port disconnected');await contains(page,'Which message matches?');
   assert.ok(await page.locator('#result button.choice').count()>=2);assert.equal(await page.getByRole('heading',{name:'What to do',exact:true}).count(),0);
   await page.getByRole('button',{name:/1500.*Chassis data/}).click();await contains(page,'Next step with PIE');await noOverflow(page);
  });
  await run(name+' unsupported input clears old card and injects no HTML',async()=>{
   await search(page,'999999');await contains(page,'No guide found');assert.equal(await page.getByRole('heading',{name:'What to do',exact:true}).count(),0);
   await search(page,'<img src=x onerror=alert(1)>');assert.equal(await page.locator('#result img').count(),0);
   await search(page,'1000022');await contains(page,'current advice from PIE');
   assert.equal((await page.locator('#result').innerText()).includes('2.3.30.26'),false);
  });
  await context.close();
 }
 await run('synthetic scoped repair contract: correct model, cable → board → PIE; no loop',async()=>{
  // Contract fixture only. Never written into real data or dist.
  const catalog=JSON.parse(fs.readFileSync(path.join(root,'data/canonical.json'),'utf8'));
  const card=catalog.cards.find(c=>c.code==='1202');
  card.scope={status:'confirmed',models:['TEST MODEL — synthetic fixture'],firmware:['TEST VERSION']};
  card.classification='SELF_SERVICE_SYMPTOM_SPLIT';
  const fixture=projectAgentCatalog({...catalog,cards:[card]});
  const context=await browser.newContext({viewport:{width:390,height:844}});
  const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/knowledge.json',route=>route.fulfill({json:fixture}));
  await page.goto(base);await page.locator('#search-button:enabled').waitFor();await search(page,'1202');
  await page.getByRole('button',{name:'Both cutting discs are free, but the error remains',exact:true}).click();
  await contains(page,'Confirm the mower details');assert.equal(await page.getByRole('heading',{name:'Most likely faulty part'}).count(),0);
  await page.locator('#scope-model').selectOption('TEST MODEL — synthetic fixture');
  await page.locator('#scope-firmware').selectOption('TEST VERSION');
  await contains(page,'Upper Shell Adapter Cable');await contains(page,'Most likely faulty part');
  await page.getByRole('button',{name:'Still not fixed',exact:true}).click();await contains(page,'Mainboard');
  await page.getByRole('button',{name:'Still not fixed',exact:true}).click();await contains(page,'Next step with PIE');
  assert.equal(await page.getByRole('heading',{name:'Most likely faulty part'}).count(),0);
  await page.locator('#scope-model').selectOption('TEST MODEL — synthetic fixture');
  await contains(page,'Next step with PIE');
  assert.equal(await page.getByRole('heading',{name:'Most likely faulty part'}).count(),0,'scope re-render must retain failed board');
  await page.getByRole('button',{name:'Change symptom',exact:true}).click();
  if(await page.getByRole('button',{name:'Both cutting discs are free, but the error remains',exact:true}).count()) await page.getByRole('button',{name:'Both cutting discs are free, but the error remains',exact:true}).click();
  assert.equal(await page.getByRole('heading',{name:'Most likely faulty part'}).count(),0,'changing symptom must retain repair failures');
  await search(page,'1202');
  await page.locator('#scope-model').selectOption('TEST MODEL — synthetic fixture');
  await page.locator('#scope-firmware').selectOption('TEST VERSION');
  await page.getByRole('button',{name:'Both cutting discs are free, but the error remains',exact:true}).click();
  await page.getByRole('button',{name:'The issue returned after repair',exact:true}).click();
  await page.locator('#scope-firmware').selectOption('TEST VERSION');
  await contains(page,'issue returned after repair');
  assert.equal(await page.getByRole('heading',{name:'Most likely faulty part'}).count(),0,'scope change must retain returned state');
  await context.close();
 });
 await run('data-load failure disables search and shows a recoverable error',async()=>{
  const context=await browser.newContext();const page=await context.newPage();
  await page.route('**/knowledge.json',route=>route.fulfill({status:503,body:'Unavailable'}));
  await page.goto(base);await contains(page,'Guides could not load');
  assert.equal(await page.locator('#search-button').isDisabled(),true);await context.close();
 });
 assert.deepEqual(errors,[]);
 assert.deepEqual(requests.filter(url=>!url.startsWith(base)&&!url.startsWith('data:')),[]);
 fs.writeFileSync(path.join(artifact,'browser-verification.json'),JSON.stringify({passed:observations.length,checks:observations,viewports:['1366x1000','390x844','320x740'],pageErrors:errors,externalRequests:0,syntheticRepairFixtureNotPublished:true,ownedServerClosedInFinally:true},null,2)+'\n');
 console.log('BROWSER GREEN '+observations.length+' checks');
} finally {await browser.close();await new Promise(resolve=>server.close(resolve));}
