import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {build} from '../scripts/build.mjs';
import {createPreview} from '../scripts/serve.mjs';
const {chromium}=createRequire(import.meta.url)('C:/Users/Reggie/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

await build();
const server=await createPreview({port:0});
const base='http://127.0.0.1:'+server.address().port;
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
try{
 const page=await browser.newPage({viewport:{width:1366,height:768}});
 await page.goto(base);await page.locator('#model:enabled').waitFor();
 assert.equal(await page.locator('#symptom-stage').isVisible(),false);
 await page.locator('#model').selectOption('LUBA 2');
 await page.locator('#observable-area').selectOption('Cutting');
 await page.locator('#observed-symptom:visible').waitFor();
 assert.equal(await page.locator('#category-stage').isVisible(),true);
 assert.equal(await page.locator('#category-next').count(),0);
 assert.match(await page.locator('#context-summary').innerText(),/LUBA 2/);
 await page.locator('#observed-symptom').selectOption('SYM-005');
 assert.match(await page.locator('#selection-summary').innerText(),/LUBA 2/);
 assert.match(await page.locator('#selection-summary').innerText(),/Cutting disc & height/);
 assert.match(await page.locator('#selection-summary').innerText(),/Cutting height does not adjust/);
 assert.equal(await page.locator('#solution-page').isVisible(),false);
 console.log('SINGLE PANEL FLOW GREEN');
}finally{await browser.close();await new Promise(r=>server.close(r));}
