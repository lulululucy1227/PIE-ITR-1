import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {projectAgentCatalog} from '../src/engine.mjs';
import {enrichKnowledge} from '../lib/reuse.mjs';
import {projectHardwareSupport} from '../lib/hardware-support.mjs';
import {translate,zh,catalogTexts,validateTranslations} from '../src/i18n.mjs';
const read=name=>JSON.parse(fs.readFileSync(new URL('../data/'+name,import.meta.url)));
const catalog=projectAgentCatalog(enrichKnowledge(read('canonical.json'),read('reuse-manifest.json'),read('reuse-snapshot.json')));
catalog.knowledgeVersion='2026-09-16-hardware-top10.1';
catalog.stepSupport=projectHardwareSupport(read('hardware-step-support.json'),catalog);
test('all public guidance, safety, verification, qualifiers and symptoms translate without changing routing data',()=>{
 const before=JSON.stringify(catalog);
 validateTranslations(catalog);
 assert.equal(catalogTexts(catalog).length,196);
 for(const text of catalogTexts(catalog)){
  assert.match(translate(text,'zh-CN'),/\p{Script=Han}/u,text);
  assert.equal(translate(text,'en'),text);
  // Keep error codes, version numbers, model numbers and thresholds intact.
  assert.deepEqual(translate(text,'zh-CN').match(/\d+(?:\.\d+)*/g),text.match(/\d+(?:\.\d+)*/g),text);
 }
 assert.equal(JSON.stringify(catalog),before);
});
test('English labels never include translated Chinese; compound summaries preserve model and code identities',()=>{
 for(const english of Object.keys(zh))assert.doesNotMatch(translate(english,'en'),/\p{Script=Han}/u);
 assert.equal(translate('LUBA 2 · Power & battery','zh-CN'),'LUBA 2 · 电源与电池');
 assert.equal(translate('1202 · Cutting disc blocked','zh-CN'),'1202 · 刀盘卡阻');
 assert.equal(translate('ERROR 1202','zh-CN'),'错误码 1202');
 assert.equal(translate('Guide firmware: 1.30.31.10','zh-CN'),'指导适用固件：1.30.31.10');
 assert.equal(translate(' unknown user input ','zh-CN'),' unknown user input ');
});
