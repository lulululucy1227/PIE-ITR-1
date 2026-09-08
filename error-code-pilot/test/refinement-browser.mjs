import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createRequire} from 'node:module';
import {build} from '../scripts/build.mjs';
import {createPreview} from '../scripts/serve.mjs';
const {chromium}=createRequire(import.meta.url)('C:/Users/Reggie/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
await build();
const server=await createPreview({port:0}),base='http://127.0.0.1:'+server.address().port;
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
const results=[],errors=[];
try {
 for(const width of [1366,1920,390]) {
  const page=await browser.newPage({viewport:{width,height:width===390?844:width===1366?768:1080}});
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base);await page.locator('#model:enabled').waitFor();
  assert.equal(await page.locator('#observable-area option[value="Cutting"]').innerText(),'Cutting disc & height');
  assert.equal(await page.locator('#observable-area option[value="Movement"]').innerText(),'Wheels & movement');
  assert.equal(await page.locator('#observable-area option').count(),11);
  await page.locator('#model').selectOption('LUBA 2');await page.locator('#observable-area').selectOption('Cutting');
  await page.screenshot({path:`artifacts/refinement-${width}-home.png`});
  await page.locator('#category-next').click();
  const symptoms=page.locator('#observed-symptom');
  assert.deepEqual(await symptoms.locator('option').evaluateAll(xs=>xs.map(x=>x.value)),['','SYM-004','SYM-005','SYM-006','__other__']);
  await symptoms.selectOption('SYM-005');
  assert.equal(await symptoms.locator('option:checked').innerText(),'Cutting height does not adjust');
  assert.equal(await page.locator('#search').getAttribute('type'),'search');
  // Escape must cancel a tentative keyboard selection, not navigate or resolve.
  await symptoms.focus();await page.keyboard.press('Space');await page.keyboard.press('ArrowDown');await page.keyboard.press('Escape');
  if(width>600)assert.equal(await symptoms.inputValue(),'SYM-005');else await symptoms.selectOption('SYM-005');assert.equal(await page.locator('#solution-page').isVisible(),false);
  await symptoms.press('Tab');assert.equal(await page.locator('#search').evaluate(e=>e===document.activeElement),true);
  await page.locator('#search').fill('1202');assert.equal(await page.locator('#solution-page').isVisible(),false);
  await page.locator('#search').fill('');
  await symptoms.click();await page.screenshot({path:`artifacts/refinement-${width}-open.png`});
  await symptoms.press('Escape');
  await page.screenshot({path:`artifacts/refinement-${width}-details.png`});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  if(width!==390)assert.equal(await page.locator('#search-button').evaluate(e=>e.getBoundingClientRect().bottom<=innerHeight),true);
  // The same IDs still use the approved controlled-symptom routing and preserve Back state.
  await page.locator('#search-button').click();await page.locator('#solution-page:visible').waitFor();
  await page.locator('#edit-issue').click();await page.locator('#symptom-stage:visible').waitFor();
  assert.equal(await symptoms.inputValue(),'SYM-005');
  results.push({width,keyboardCancellation:width>600?'passed':'native mobile behavior',tabToOptionalCode:true,controlledIdsPreserved:true,backPreserved:true,noOverflow:true});
  await page.close();
 }
 assert.deepEqual(errors,[]);
 fs.writeFileSync('artifacts/refinement-verification.json',JSON.stringify({results,errors},null,2)+'\n');
 console.log('REFINEMENT BROWSER GREEN',results.length);
} finally {await browser.close();await new Promise(r=>server.close(r));}
