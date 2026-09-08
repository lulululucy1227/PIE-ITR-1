import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createRequire} from 'node:module';
import {build} from '../scripts/build.mjs';
import {createPreview} from '../scripts/serve.mjs';
import {enterSymptom,solve,choose} from './input-helpers.mjs';
const {chromium}=createRequire(import.meta.url)('C:/Users/Reggie/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
await build();const server=await createPreview({port:0}),base='http://127.0.0.1:'+server.address().port;
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
const checks=[],errors=[];
try{
 for(const width of [1366,1920,390]){
  const page=await browser.newPage({viewport:{width,height:width===1920?1080:width===390?844:768}});
  page.on('pageerror',e=>errors.push(e.message));await page.goto(base);await page.locator('#model:enabled').waitFor();
  await page.screenshot({path:`artifacts/service-${width}-identify.png`});
  await enterSymptom(page,'SYM-001','LUBA 2');
  assert.equal(await page.locator('.service-plan').count(),0);
  await solve(page);await page.locator('.service-plan').waitFor();
  const catalog=await(await page.request.get(base+'/knowledge.json')).json();const path=catalog.cards.find(c=>c.id==='guide-wheel-movement').paths[0];
  assert.deepEqual(await page.locator('.step-instruction').allTextContents(),path.action);
  assert.deepEqual(await page.locator('.service-verification li').allTextContents(),path.verification.steps);
  assert.equal(await page.locator('.step-support,.support-disclosure').count(),0);
  assert.doesNotMatch(await page.locator('#result').innerText(),/Parts for this step|Tools and how to use them|Why this check matters|How to access and remove|Coming soon|FIXTURE-PART/);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
  if(width>1000){const actions=await page.locator('.service-actions').boundingBox(),verification=await page.locator('.service-verification').boundingBox();assert.ok(verification.x>actions.x+actions.width);}
  await page.screenshot({path:`artifacts/service-${width}-guide.png`,fullPage:true});
  const contrast=await page.locator('button.primary').filter({hasText:'Fixed'}).evaluate(e=>{
   const luminance=color=>{const rgb=color.match(/[\d.]+/g).slice(0,3).map(Number).map(c=>{c/=255;return c<=.04045?c/12.92:((c+.055)/1.055)**2.4;});return .2126*rgb[0]+.7152*rgb[1]+.0722*rgb[2];};
   const style=getComputedStyle(e),a=luminance(style.color),b=luminance(style.backgroundColor);return (Math.max(a,b)+.05)/(Math.min(a,b)+.05);
  });assert.ok(contrast>=4.5);
  await page.getByRole('button',{name:'Fixed',exact:true}).click();assert.equal(await page.getByRole('heading',{name:'You reported it fixed',exact:true}).count(),0);
  await page.locator('#verification').check();await page.getByRole('button',{name:'Fixed',exact:true}).click();await page.getByRole('heading',{name:'You reported it fixed',exact:true}).waitFor();
  await page.locator('#edit-issue').click();assert.equal(await page.locator('.service-plan').count(),0);assert.equal(await page.locator('#observed-symptom').inputValue(),'SYM-001');
  await choose(page,'SYM-003','LUBA 2');await page.locator('#observed-symptom').selectOption('__other__');await page.locator('#search').fill('');await solve(page);await page.getByRole('heading',{name:'Next step with PIE',exact:true}).waitFor();assert.equal(await page.locator('.service-plan,.step-support').count(),0);
  checks.push({width,allApprovedActionsPreserved:true,noEmptyResources:true,verificationGate:true,backPreserved:true,otherSafe:true,contrast});await page.close();
 }
 assert.deepEqual(errors,[]);fs.writeFileSync('artifacts/service-browser-verification.json',JSON.stringify({checks,errors},null,2)+'\n');console.log('SERVICE BROWSER GREEN',checks.length);
}finally{await browser.close();await new Promise(r=>server.close(r));}
