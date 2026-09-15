import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createRequire} from 'node:module';
import {build} from '../scripts/build.mjs';
import {createPreview} from '../scripts/serve.mjs';
const {chromium}=createRequire(import.meta.url)('C:/Users/Reggie/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
await build();
const server=await createPreview({port:0});
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
const results=[];
try{
 for(const width of [1366,1920,390]){
  const page=await browser.newPage({viewport:{width,height:width===1920?1080:768}});
  await page.goto('http://127.0.0.1:'+server.address().port);await page.locator('#model:enabled').waitFor();
  assert.equal(await page.locator('#observable-area:visible').count(),0,'Area must not cost an extra input');
  await page.locator('#model').selectOption('LUBA 2');
  assert.equal(await page.locator('#identify-page select:visible').count(),2);
  assert.ok(await page.locator('#observed-symptom optgroup').count()>1);
  assert.equal(await page.locator('#more-details').isVisible(),false);
  await page.locator('#search').fill('1202');await page.locator('#search-button').click();
  assert.equal(await page.locator('#solution-page').isVisible(),false);
  await page.locator('#search').fill('');await page.locator('#observed-symptom').selectOption('SYM-001');
  await page.locator('#search-button').click();await page.locator('#solution-page:visible').waitFor();
  assert.equal(await page.locator('.service-actions h3').innerText(),'What should I do now?');
  assert.equal(await page.locator('.service-plan').evaluate(e=>e.firstElementChild.classList.contains('service-actions')),true);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  await page.screenshot({path:`artifacts/simple-${width}-repair.png`,fullPage:true});
  await page.locator('#edit-issue').click();
  assert.equal(await page.locator('#observed-symptom').inputValue(),'SYM-001');
  await page.locator('#model').selectOption('LUBA 1');await page.goForward();
  assert.equal(await page.locator('#solution-page').isVisible(),false);
  await page.locator('#observed-symptom').selectOption('__other__');
  await page.locator('#other-description').fill('Replace the battery');await page.locator('#search-button').click();
  assert.equal(await page.locator('.service-plan').count(),0);
  assert.match(await page.locator('#result').innerText(),/Contact PIE/);
  results.push({width,requiredSelections:2,normalSubmitClicks:1,otherSafe:true});await page.close();
 }
 fs.writeFileSync('artifacts/simple-knowledge-browser.json',JSON.stringify(results,null,2));console.log('SIMPLE KNOWLEDGE BROWSER GREEN',results.length);
}finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
