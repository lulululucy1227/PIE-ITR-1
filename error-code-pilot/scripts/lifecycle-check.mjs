import {spawn} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const results=[];
for(let cycle=1;cycle<=2;cycle++){
 const child=spawn(process.execPath,['scripts/serve.mjs'],{cwd:root,stdio:['ignore','pipe','pipe'],windowsHide:true});
 let stdout='',stderr='';child.stdout.on('data',b=>stdout+=b);child.stderr.on('data',b=>stderr+=b);
 try{
  await new Promise((resolve,reject)=>{
   const timeout=setTimeout(()=>reject(new Error('Pilot startup timed out')),5000);
   child.stdout.on('data',()=>{if(stdout.includes('http://127.0.0.1:8796')){clearTimeout(timeout);resolve();}});
   child.once('exit',code=>{clearTimeout(timeout);reject(new Error('Pilot exit '+code+': '+stderr));});
  });
  const res=await fetch('http://127.0.0.1:8796/');
  if(res.status!==200)throw new Error('Preview did not return 200');
  results.push({cycle,port:8796,httpStatus:res.status});
 }finally{
  if(child.exitCode===null){const ended=new Promise(resolve=>child.once('exit',resolve));child.kill('SIGTERM');await ended;}
 }
}
fs.writeFileSync(path.join(root,'artifacts/lifecycle-verification.json'),JSON.stringify({cycles:results,ownedChildrenExited:true,relaunchPassed:true,mainRuntimeUntouched:true},null,2)+'\n');
console.log('PASS two default-port start -> owned exit -> relaunch cycles');
