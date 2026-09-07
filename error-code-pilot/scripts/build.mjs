import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {projectAgentCatalog} from '../src/engine.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
export async function build({catalog}={}) {
  const input=catalog||JSON.parse(fs.readFileSync(path.join(root,'data/canonical.json'),'utf8'));
  const agent=projectAgentCatalog(input); // Validate before any output mutation.
  const files=new Map();
  for(const name of ['index.html','styles.css','app.mjs','engine.mjs']) files.set(name,fs.readFileSync(path.join(root,'src',name)));
  files.set('knowledge.json',Buffer.from(JSON.stringify(agent,null,2)+'\n'));
  const outDir=path.join(root,'dist');
  if(fs.existsSync(outDir)) {
    const unknown=fs.readdirSync(outDir).filter(n=>!files.has(n));
    if(unknown.length)throw new Error('Unexpected files in dist; preserve and investigate before build: '+unknown.join(', '));
  }
  fs.mkdirSync(outDir,{recursive:true});
  for(const [name,content] of files)fs.writeFileSync(path.join(outDir,name),content);
  const manifest={knowledgeVersion:agent.knowledgeVersion,cards:agent.cards.length,files:[...files].map(([name,content])=>({name,bytes:content.length,sha256:crypto.createHash('sha256').update(content).digest('hex')}))};
  fs.mkdirSync(path.join(root,'artifacts'),{recursive:true});
  fs.writeFileSync(path.join(root,'artifacts/build-manifest.json'),JSON.stringify(manifest,null,2)+'\n');
  return {outDir,...manifest};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) console.log(JSON.stringify(await build(),null,2));
