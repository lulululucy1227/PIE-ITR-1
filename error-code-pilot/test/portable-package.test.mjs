import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';

test('portable package copies its runtime once from the approved source',()=>{
 const script=fs.readFileSync(new URL('../scripts/package.ps1',import.meta.url),'utf8');
 assert.match(script,/if \(\$relative -eq 'LOCAL_README\.txt' -or \$relative -eq 'runtime\/node\.exe'\) \{ continue \}/);
 assert.match(script,/Copy-Item -LiteralPath \$runtimeNode -Destination \(Join-Path \$stage 'runtime\\node\.exe'\)/);
});
