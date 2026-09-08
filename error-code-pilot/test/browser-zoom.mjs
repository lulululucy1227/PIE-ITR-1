// Actual Chromium browser zoom, not CSS zoom or pinch-scale emulation.
// The test-only extension/profile is isolated under ignored artifacts and is never packaged.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {build} from '../scripts/build.mjs';
import {createPreview} from '../scripts/serve.mjs';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'C:/Users/Reggie/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const artifact=path.join(root,'artifacts');
const extension=path.join(artifact,'zoom-extension');fs.mkdirSync(extension,{recursive:true});
fs.writeFileSync(path.join(extension,'manifest.json'),JSON.stringify({manifest_version:3,name:'Local desktop zoom verification',version:'1.0',permissions:['tabs'],background:{service_worker:'worker.js'}}));
fs.writeFileSync(path.join(extension,'worker.js'),'chrome.runtime.onInstalled.addListener(()=>{});');
await build();
const server=await createPreview({port:0});const base='http://127.0.0.1:'+server.address().port;
const results=[];
try{
 for(const size of [{width:1366,height:768},{width:1920,height:1080}]){
  const profile=path.join(artifact,'zoom-profile-'+Date.now()+'-'+size.width);
  const ctx=await chromium.launchPersistentContext(profile,{headless:true,executablePath:process.env.PILOT_BROWSER||'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',viewport:size,ignoreDefaultArgs:['--disable-extensions'],args:[`--disable-extensions-except=${extension}`,`--load-extension=${extension}`]});
  try{
   const worker=ctx.serviceWorkers()[0]||await ctx.waitForEvent('serviceworker',{timeout:10000});
   const page=await ctx.newPage();const errors=[],external=[];page.setDefaultTimeout(7000);
   const cdp=await ctx.newCDPSession(page);
   const capture=async name=>{const shot=await cdp.send('Page.captureScreenshot',{format:'png',fromSurface:true,captureBeyondViewport:false});fs.writeFileSync(path.join(artifact,name),Buffer.from(shot.data,'base64'));};
   page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(!r.url().startsWith(base)&&!r.url().startsWith('data:'))external.push(r.url());});
   await page.goto(base);await page.locator('#search-button:enabled').waitFor();
   const zoom=await worker.evaluate(async base=>{const tabs=await chrome.tabs.query({});const tab=tabs.find(t=>t.url.startsWith(base));await chrome.tabs.setZoom(tab.id,1.25);return chrome.tabs.getZoom(tab.id);},base);
   assert.equal(zoom,1.25);
   await page.waitForFunction(()=>devicePixelRatio===1.25);
   const dimensions=await page.evaluate(()=>({width:innerWidth,dpr:devicePixelRatio,overflow:document.documentElement.scrollWidth>innerWidth}));
   assert.equal(dimensions.overflow,false);assert.equal(await page.locator('[data-area]').count(),10);
   await capture(`zoom125-${size.width}-home.png`);
   await page.locator('#model').selectOption('LUBA 2 5000X');await page.locator('#firmware').fill('1.30.31.10');await page.locator('#firmware').press('Tab');
   await page.locator('[data-area="Cutting"]').click();await page.locator('[data-symptom="SYM-004"]').click();await page.getByRole('button',{name:'Yes, this matches',exact:true}).click();
   assert.equal(await page.locator('#result').innerText(),'');assert.equal(await page.locator('#solution-page').isVisible(),false);
   await capture(`zoom125-${size.width}-identify-selection.png`);
   await page.locator('#continue').click();
   await page.getByRole('heading',{name:'What to do',exact:true}).waitFor();assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
   await page.evaluate(()=>scrollTo(0,0));
   await capture(`zoom125-${size.width}-repair.png`);
   await page.locator('#verification').scrollIntoViewIfNeeded();
   await capture(`zoom125-${size.width}-verification.png`);
   await page.getByRole('button',{name:'Still not fixed',exact:true}).click();await page.getByRole('heading',{name:'Next step with PIE',exact:true}).waitFor();
   await page.goBack();await page.locator('#identify-page:visible').waitFor();assert.equal(await page.locator('#result').innerText(),'');assert.equal(await page.locator('#model').inputValue(),'LUBA 2 5000X');
   assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
   results.push({viewport:size,zoom,dimensions,homeAndRepairPassed:true,failedRepairPassed:true,pageErrors:errors,externalRequests:0});
   console.log('PASS native 125% zoom '+size.width+'x'+size.height);
  }finally{await ctx.close();}
 }
 fs.writeFileSync(path.join(artifact,'zoom-verification.json'),JSON.stringify({results,isolatedProfiles:true,testExtensionNotPackaged:true,ownedServerClosedInFinally:true},null,2)+'\n');
}finally{await new Promise(r=>server.close(r));}
