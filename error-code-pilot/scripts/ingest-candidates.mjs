import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {parseCandidatePayload,payloadDigest,validateCandidates,candidateCounts,PAYLOAD_PATH} from '../lib/candidates.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const payload=fs.readFileSync(path.join(root,'..',PAYLOAD_PATH),'utf8');
const target=path.join(root,'data/feishu-candidates.json');
const canonical=JSON.parse(fs.readFileSync(path.join(root,'data/canonical.json'),'utf8'));
const args=process.argv.slice(2);
if(args.length!==1||!['--check','--write'].includes(args[0]))throw new Error('Use --check to verify an import, or --write to refresh identical source fields while retaining reviewed decisions.');
if(!fs.existsSync(target))throw new Error('Create and review the private candidate catalog before using this command. Missing facts must remain null; this command never invents review decisions.');
const existing=JSON.parse(fs.readFileSync(target,'utf8'));
const errors=validateCandidates(existing,canonical,{payloadText:payload});
if(errors.length)throw new Error(errors.join('\n'));
if(args[0]==='--write'){
 const parsed=parseCandidatePayload(payload);
 const result={...existing,source:{...existing.source,sha256:payloadDigest(payload)}};
 for(const kind of ['candidates','frozen','error_reconciliation'])result[kind]=parsed[kind].map((source,i)=>({...source,review:existing[kind][i].review}));
 // Source parity validation above deliberately refuses silent changes to a reviewed batch.
 fs.writeFileSync(target,JSON.stringify(result,null,2)+'\n');
}
console.log(JSON.stringify({status:'CANDIDATE_IMPORT_VALID',...candidateCounts(existing),sourceSha256:existing.source.sha256,productionRead:false,productionWrite:false},null,2));
