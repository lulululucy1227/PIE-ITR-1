import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

// Run with the extracted package's bundled Node; only terminate processes this check starts.
const root=path.resolve(process.argv[2]);
const {launch}=await import(pathToFileURL(path.join(root,'scripts/launch-local.mjs')));
let owned;
try{
 owned=await launch({root,preferredPort:8840,openBrowser:false});
 assert.equal(owned.state,'started','verification needs a newly owned extracted service');
 const repeated=await launch({root,preferredPort:8840,openBrowser:false});
 assert.equal(repeated.state,'reused');
 assert.equal(repeated.port,owned.port);
 for(const name of ['index.html','styles.css','app.mjs','engine.mjs','service-plan.mjs','i18n.mjs','knowledge.json']){
  const response=await fetch(`${owned.url}/${name}`);
  assert.equal(response.status,200);
  assert.deepEqual(Buffer.from(await response.arrayBuffer()),fs.readFileSync(path.join(root,'dist',name)));
 }
 console.log(JSON.stringify({extractedLauncherStarted:true,extractedLauncherReused:true,allPublicHttpFilesMatched:true,httpFileCount:7,port:owned.port}));
}finally{
 if(owned?.pid){
  process.kill(owned.pid,'SIGTERM');
  let stopped=false;
  for(let attempt=0;attempt<50;attempt++){
   try{process.kill(owned.pid,0);}catch(error){if(error.code==='ESRCH'){stopped=true;break;}throw error;}
   await new Promise(resolve=>setTimeout(resolve,50));
  }
  assert.ok(stopped,'owned extracted service must stop');
 }
}
