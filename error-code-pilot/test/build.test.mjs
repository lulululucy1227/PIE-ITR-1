import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {build} from '../scripts/build.mjs';
import {createPreview} from '../scripts/serve.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
test('build emits only agent assets and strips raw provenance and unresolved repair prose',async()=>{
  const result=await build();
  assert.deepEqual(fs.readdirSync(result.outDir).sort(),['app.mjs','engine.mjs','index.html','knowledge.json','styles.css']);
  const data=fs.readFileSync(path.join(result.outDir,'knowledge.json'),'utf8');
  for(const forbidden of ['sourceRefs','"evidence":','"review":','"label_cn":','"evidence_state":','local-error-reference','cohortCount','2.3.30.26','C:/Users/','customer','cookie','INTERNAL-CANARY']) assert.equal(data.includes(forbidden),false,forbidden);
});
test('invalid knowledge fails the build before changing last valid output',async()=>{
  const original=fs.readFileSync(path.join(root,'dist/knowledge.json'),'utf8');
  const bad=JSON.parse(fs.readFileSync(path.join(root,'data/canonical.json'),'utf8'));
  bad.cards[0].paths[0].verification=null;
  await assert.rejects(()=>build({catalog:bad}),/verification/);
  assert.equal(fs.readFileSync(path.join(root,'dist/knowledge.json'),'utf8'),original);
});
test('local preview rejects write methods, raw paths, traversal and foreign origins',async()=>{
  const server=await createPreview({port:0});
  try {
    const base='http://127.0.0.1:'+server.address().port;
    assert.equal((await fetch(base+'/')).status,200);
    assert.equal((await fetch(base+'/knowledge.json')).status,200);
    for(const url of ['/data/canonical.json','/.git/config','/../data/canonical.json','/%2e%2e%2fdata%2fcanonical.json','/artifacts/source-audit.json','/docs/KNOWLEDGE_PROMOTION_AUDIT_2026-09-08.md','/.local/desktop-data.mjs','/candidate.json']) assert.equal((await fetch(base+url)).status,404);
    for(const method of ['POST','PUT','PATCH','DELETE','OPTIONS']) assert.equal((await fetch(base+'/',{method})).status,405);
    assert.equal((await fetch(base+'/',{headers:{Origin:'https://outside.invalid'}})).status,403);
    const res=await fetch(base+'/');
    assert.ok(res.headers.get('content-security-policy').includes("default-src 'self'"));
    assert.equal(res.headers.get('x-content-type-options'),'nosniff');
  } finally { await new Promise(resolve=>server.close(resolve));}
});
test('preview refuses formal Workbench port',async()=>assert.rejects(()=>createPreview({port:8787}),/8787/));
