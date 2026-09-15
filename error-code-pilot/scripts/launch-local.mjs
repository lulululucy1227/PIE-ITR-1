import http from 'node:http';
import net from 'node:net';
import path from 'node:path';
import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {previewIdentity} from './serve.mjs';

const defaultRoot=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const healthyMarker='PIE Troubleshooter';

function delay(milliseconds){return new Promise(resolve=>setTimeout(resolve,milliseconds));}

function validPort(value){
 const port=Number(value);
 return Number.isInteger(port)&&port>=1024&&port<=65526&&port!==8787?port:8796;
}

function probe(port,identity){
 return new Promise(resolve=>{
  const request=http.get({host:'127.0.0.1',port,path:'/',timeout:350},response=>{
   let body='';
   response.setEncoding('utf8');
   response.on('data',chunk=>body+=chunk);
   response.on('end',()=>resolve(response.statusCode===200&&response.headers['x-pie-instance']===identity&&body.includes(healthyMarker)));
  });
  request.once('error',()=>resolve(false));
  request.once('timeout',()=>{request.destroy();resolve(false);});
 });
}

function canBind(port){
 return new Promise(resolve=>{
  const server=net.createServer();
  server.once('error',()=>resolve(false));
  server.listen(port,'127.0.0.1',()=>server.close(()=>resolve(true)));
 });
}

async function waitForHealthy(port,child,identity){
 for(let attempt=0;attempt<40;attempt++){
  if(await probe(port,identity))return true;
  if(child.exitCode!==null)return false;
  await delay(100);
 }
 return false;
}

function open(url){
 if(process.platform==='win32'){
  const browser=spawn('cmd.exe',['/d','/c','start','',url],{detached:true,stdio:'ignore',windowsHide:true});
  browser.unref();
  return;
 }
 const browser=spawn(process.platform==='darwin'?'open':'xdg-open',[url],{detached:true,stdio:'ignore'});
 browser.unref();
}

function stopOwned(child){
 if(child.exitCode===null)child.kill('SIGTERM');
}

export async function launch({root=defaultRoot,preferredPort=8796,openBrowser=true}={}){
 const identity=previewIdentity(path.join(root,'dist'));
 const startPort=validPort(preferredPort);
 const candidates=Array.from({length:10},(_value,index)=>startPort+index).filter(port=>port<=65535&&port!==8787);
 for(const port of candidates){
  if(await probe(port,identity)){
   const url=`http://127.0.0.1:${port}`;
   if(openBrowser)open(url);
   return {state:'reused',port,url};
  }
  if(!await canBind(port))continue;
  const child=spawn(process.execPath,['scripts/serve.mjs',String(port)],{
   cwd:root,
   detached:true,
   stdio:'ignore',
   windowsHide:true
  });
  child.unref();
  if(await waitForHealthy(port,child,identity)){
   const url=`http://127.0.0.1:${port}`;
   if(openBrowser)open(url);
   return {state:'started',port,url,pid:child.pid};
  }
  stopOwned(child);
 }
 throw new Error('Could not start PIE Troubleshooter. Close the program using ports 8796–8805, then double-click this file again.');
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 try{
  const result=await launch({preferredPort:process.env.PIE_LAUNCH_PORT||8796});
  console.log(`PIE Troubleshooter is ready: ${result.url}`);
 }catch(error){
  console.error(error.message);
  process.exitCode=1;
 }
}
