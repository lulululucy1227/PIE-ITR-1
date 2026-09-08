import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../dist');
const mime={'index.html':'text/html; charset=utf-8','styles.css':'text/css; charset=utf-8','app.mjs':'text/javascript; charset=utf-8','engine.mjs':'text/javascript; charset=utf-8','service-plan.mjs':'text/javascript; charset=utf-8','knowledge.json':'application/json; charset=utf-8'};
export async function createPreview({port=8796}={}) {
  if(!Number.isInteger(port)||port<0||port>65535||port===8787)throw new Error('Invalid pilot port; 8787 belongs to MAIN.');
  if(!fs.existsSync(path.join(root,'index.html')))throw new Error('Build first: node scripts/build.mjs');
  const server=http.createServer((req,res)=>{
    const host=req.headers.host||'';
    if(!/^127\.0\.0\.1:\d+$/.test(host)&&!/^localhost:\d+$/.test(host)) {res.writeHead(403);res.end('Local preview only');return;}
    const allowedOrigin='http://'+host;
    if(req.headers.origin&&req.headers.origin!==allowedOrigin) {res.writeHead(403);res.end('Foreign origin refused');return;}
    if(!['GET','HEAD'].includes(req.method)) {res.writeHead(405,{Allow:'GET, HEAD'});res.end('Read-only preview');return;}
    let pathname;
    try {pathname=new URL(req.url,'http://127.0.0.1').pathname;}catch{res.writeHead(400);res.end();return;}
    const file=pathname==='/'?'index.html':pathname.slice(1);
    if(!Object.hasOwn(mime,file)) {res.writeHead(404);res.end('Not found');return;}
    const headers={'Content-Type':mime[file],'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"};
    try {const content=fs.readFileSync(path.join(root,file));res.writeHead(200,headers);res.end(req.method==='HEAD'?undefined:content);}
    catch{res.writeHead(503);res.end('Local build unavailable');}
  });
  await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(port,'127.0.0.1',resolve);});
  return server;
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const port=process.argv[2]===undefined?8796:Number(process.argv[2]);
  const server=await createPreview({port});
  console.log('Error Code local pilot: http://127.0.0.1:'+server.address().port);
  console.log('Close with Ctrl+C. Only this owned pilot server will exit.');
  for(const signal of ['SIGINT','SIGTERM'])process.once(signal,()=>server.close(()=>process.exit(0)));
}
