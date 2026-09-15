import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createRequire} from 'node:module';
import {build} from '../scripts/build.mjs';
import {createPreview} from '../scripts/serve.mjs';
import {enterSearch} from './input-helpers.mjs';
const {chromium}=createRequire(import.meta.url)('C:/Users/Reggie/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
await build();
const server=await createPreview({port:0}),base='http://127.0.0.1:'+server.address().port;
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
const catalog=JSON.parse(fs.readFileSync('dist/knowledge.json'));
const cards=catalog.cards.filter(c=>catalog.stepSupport.some(r=>r.binding.cardId===c.id));
const checks=[],errors=[];
try{
 for(const width of [1366,1920,390]){
  const page=await browser.newPage({viewport:{width,height:width===1920?1080:width===1366?768:844}});
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base);await page.locator('#model:enabled').waitFor();
  assert.equal(await page.locator('select').count(),2);
  for(const card of cards){
   const model=card.scope.models[0];
   await enterSearch(page,card.message,undefined,model);
   if(card.paths[0].qualifier)await page.getByRole('button',{name:'Yes, this matches',exact:true}).click();
   assert.equal(await page.locator('.support-disclosure,.service-caution').count(),0);
   await page.locator('#continue').click();await page.locator('.service-plan').waitFor();
   const records=catalog.stepSupport.filter(r=>r.binding.cardId===card.id&&r.binding.model===model);
   assert.equal(await page.locator('.support-disclosure').count(),records.filter(r=>r.kind!=='safety').length);
   assert.equal(await page.locator('.support-disclosure[open]').count(),0);
   for(const r of records.filter(r=>r.kind==='safety')){
    assert.ok((await page.locator('.service-caution').allTextContents()).includes(r.lines[0]));
    assert.equal(await page.locator('.service-caution').first().evaluate(e=>Boolean(e.compareDocumentPosition(document.querySelector('.step-instruction'))&Node.DOCUMENT_POSITION_FOLLOWING)),true);
   }
   await page.locator('.support-disclosure summary').first().click();
   for(const line of records.find(r=>r.kind!=='safety').lines)assert.ok((await page.locator('#result').innerText()).includes(line));
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
   assert.doesNotMatch(await page.locator('#result').innerText(),/sourceRefs|PRIVATE_ONLY|Top 10|C\.P\.SH\.000184000/);
   await page.screenshot({path:`artifacts/hardware-${width}-${card.id}.png`,fullPage:true});
   await page.locator('#edit-issue').click();await page.locator('#identify-page:visible').waitFor();
   await page.locator('#search').fill('unrecognized changed message');
   assert.equal(await page.locator('.support-disclosure,.service-caution').count(),0);
   await page.goForward();assert.equal(await page.locator('#solution-page').isVisible(),false);
   checks.push({width,card:card.id,collapsedByDefault:true,exactDetail:true,staleResourceCleared:true});
  }
  await page.close();
 }
 assert.deepEqual(errors,[]);fs.writeFileSync('artifacts/hardware-browser-verification.json',JSON.stringify({checks,errors},null,2)+'\n');console.log('HARDWARE BROWSER GREEN',checks.length);
}finally{await browser.close();await new Promise(r=>server.close(r));}
