import assert from 'node:assert/strict';
import fs from 'node:fs';
import http from 'node:http';
import net from 'node:net';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import test from 'node:test';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const workspaceRoot=path.resolve(root,'..');
const launcherPath=path.join(root,'scripts','launch-local.mjs');

test('desktop double-click launcher uses the local Codex runtime before PATH lookup',()=>{
 const command=fs.readFileSync(path.join(workspaceRoot,'启动并修复 PIE Troubleshooter.cmd'),'utf8');
 assert.match(command,/%USERPROFILE%\\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\bin\\node\.exe/);
 assert.match(command,/"%NODE_EXE%" scripts\\launch-local\.mjs/);
});

function unusedPort(){
 return new Promise((resolve,reject)=>{
  const server=net.createServer();
  server.once('error',reject);
  server.listen(0,'127.0.0.1',()=>{
   const {port}=server.address();
   server.close(error=>error?reject(error):resolve(port));
  });
 });
}

function request(port){
 return new Promise((resolve,reject)=>{
  const req=http.get({host:'127.0.0.1',port,path:'/',timeout:1000},res=>{
   let body='';
   res.setEncoding('utf8');
   res.on('data',chunk=>body+=chunk);
   res.on('end',()=>resolve({status:res.statusCode,body}));
  });
  req.once('error',reject);
  req.once('timeout',()=>req.destroy(new Error('request timeout')));
 });
}

async function stopOwned(pid){
 if(!pid)return;
 try{process.kill(pid,'SIGTERM');}catch(error){if(error.code!=='ESRCH')throw error;}
 for(let attempt=0;attempt<40;attempt++){
  try{process.kill(pid,0);}catch(error){if(error.code==='ESRCH')return;throw error;}
  await new Promise(resolve=>setTimeout(resolve,50));
 }
}

test('one-click launcher starts the local pilot then reuses its healthy service',async t=>{
 assert.ok(fs.existsSync(path.join(workspaceRoot,'启动并修复 PIE Troubleshooter.cmd')),'the local desktop double-click file must be included');
 assert.ok(fs.existsSync(launcherPath),'the one-click launcher must be included');
 const {launch}=await import('../scripts/launch-local.mjs');
 const port=await unusedPort();
 const first=await launch({root,preferredPort:port,openBrowser:false});
 t.after(()=>stopOwned(first.pid));
 const {pid,...firstResult}=first;
 assert.equal(typeof pid,'number');
 assert.deepEqual(firstResult,{state:'started',port,url:`http://127.0.0.1:${port}`});
 const page=await request(port);
 assert.equal(page.status,200);
 assert.match(page.body,/PIE Troubleshooter/);
 const second=await launch({root,preferredPort:port,openBrowser:false});
 assert.deepEqual(second,{state:'reused',port,url:`http://127.0.0.1:${port}`});
});

test('one-click launcher avoids an unrelated occupied port and starts on the next safe port',async t=>{
 assert.ok(fs.existsSync(launcherPath),'the one-click launcher must be included');
 const {launch}=await import('../scripts/launch-local.mjs');
 const occupied=await unusedPort();
 const blocker=http.createServer((_req,res)=>{res.writeHead(200);res.end('PIE Troubleshooter — older package');});
 await new Promise((resolve,reject)=>blocker.listen(occupied,'127.0.0.1',error=>error?reject(error):resolve()));
 t.after(()=>new Promise(resolve=>blocker.close(resolve)));
 const result=await launch({root,preferredPort:occupied,openBrowser:false});
 t.after(()=>stopOwned(result.pid));
 assert.equal(result.state,'started');
 assert.equal(result.port,occupied+1);
 assert.equal((await request(result.port)).status,200);
 assert.match((await request(occupied)).body,/older package/);
});

test('a different extracted package starts its own service even with identical public files',async t=>{
 const {launch}=await import('../scripts/launch-local.mjs');
 const copy=fs.mkdtempSync(path.join(root,'artifacts','launcher-copy-'));
 fs.cpSync(path.join(root,'dist'),path.join(copy,'dist'),{recursive:true});
 fs.mkdirSync(path.join(copy,'scripts'));
 for(const name of ['serve.mjs','launch-local.mjs'])fs.copyFileSync(path.join(root,'scripts',name),path.join(copy,'scripts',name));
 const first=await launch({root,preferredPort:await unusedPort(),openBrowser:false});
 let second;
 try{
  second=await launch({root:copy,preferredPort:first.port,openBrowser:false});
  assert.equal(second.state,'started');
  assert.notEqual(second.port,first.port);
  assert.equal((await launch({root:copy,preferredPort:first.port,openBrowser:false})).port,second.port);
 }finally{await stopOwned(second?.pid);await stopOwned(first.pid);}
});
