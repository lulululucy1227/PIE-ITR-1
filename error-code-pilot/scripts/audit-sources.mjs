import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source='C:/Users/Reggie/Desktop/PIE-ITR-1/knowledge/desktop_reference_20260907_p0_additions/data/tables/error-codes.json';
const bytes=fs.readFileSync(source),data=JSON.parse(bytes);
const sheet=data.sheets.find(s=>s.name==='ErrorCode');
const rows=sheet.rows.filter(r=>/^[-+]?\d+$/.test(String(r.cells[0]?.value??'')));
const countAt=i=>Object.fromEntries([...new Set(rows.map(r=>r.cells[i]?.value))].map(v=>[v,rows.filter(r=>r.cells[i]?.value===v).length]));
const summary={
  source:'Existing parsed ErrorCode table; original stays read-only in MAIN',
  sourceWorkbookSha256:data.source_sha256,parsedTableSha256:crypto.createHash('sha256').update(bytes).digest('hex'),
  sheet:sheet.name,dimensions:sheet.dimensions,parsedRows:sheet.rows.length,headerRowsExcluded:sheet.rows.length-rows.length,
  validCodeRows:rows.length,uniqueCodes:new Set(rows.map(r=>String(r.cells[0].value))).size,
  legitimateZeroPreserved:rows.some(r=>String(r.cells[0].value)==='0'),types:countAt(1),severity:countAt(4),
  fieldClassification:{
    internal:['C module','D engineering location','E source severity; not repair classification','cell formats/comments/links'],
    candidateFacts:['A signed code','B user/debug type for screening','F/G Chinese meaning/handling','I/J English meaning/handling'],
    excludedFromAgentBuild:['button labels','unused translations','raw rows','source paths','engineering module/location','administrative references']
  },
  selectedCoordinates:rows.filter(r=>['1202','1008','5510','1000022','1500','5501','6401'].includes(String(r.cells[0].value))).map(r=>({code:String(r.cells[0].value),row:r.row})),
  rawReviewStatus:data.review_status,rawDirectReplyEligible:data.direct_reply_eligible,
  caveats:['Severity 提示 includes faults and successes.','No model/version or actual repair-outcome/cohort fields.','Existing parsed table reused; XLSX not reparsed.','Raw sources preserved in place; no raw-row copy.'],
  productionWrites:0,sourceMutations:0
};
fs.mkdirSync(path.join(root,'artifacts'),{recursive:true});
fs.writeFileSync(path.join(root,'artifacts/source-audit.json'),JSON.stringify(summary,null,2)+'\n');
console.log(JSON.stringify(summary,null,2));
