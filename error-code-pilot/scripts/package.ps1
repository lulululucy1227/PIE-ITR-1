#Requires -Version 7.0
$ErrorActionPreference = 'Stop'
$pilotRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$expectedRoot = 'C:\Users\Reggie\Desktop\PIE-ITR-ErrorCode\error-code-pilot'
if ($pilotRoot -ne $expectedRoot) { throw 'Packaging writes are restricted to the isolated specialist workspace.' }
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$stage = Join-Path $pilotRoot "artifacts\package-$stamp"
$zip = Join-Path $pilotRoot "artifacts\error-code-pilot-$stamp.zip"
$allow = @('dist/index.html','dist/styles.css','dist/app.mjs','dist/engine.mjs','dist/knowledge.json','scripts/serve.mjs','run-pilot.cmd','LOCAL_README.txt')
New-Item -ItemType Directory -Path (Join-Path $stage 'dist'),(Join-Path $stage 'scripts') -Force | Out-Null
foreach ($relative in $allow) {
  if ($relative -eq 'LOCAL_README.txt') { continue }
  Copy-Item -LiteralPath (Join-Path $pilotRoot $relative) -Destination (Join-Path $stage $relative)
}
@'
PIE Troubleshooter — desktop local review
Requires Node.js 22 or later. No npm install.
Double-click run-pilot.cmd, or run: node scripts/serve.mjs
Open http://127.0.0.1:8796 and use Ctrl+C to stop this preview.
If 8796 is occupied, run node scripts/serve.mjs 8797. Never use 8787.

This package is for local service-agent/supervisor review only. No external deployment is authorized.
Use Product / model context, Error Code / Message search, or Choose by symptom.
Only reviewed paths are shown; unconfirmed repairs route to PIE. No repair-success-rate claims.
1202 replacement steps are frozen. A frozen knowledge item does not block the local product.
Fixed is user-reported, not verified ticket closure/NFF. No case data is stored or sent.
Raw references, canonical evidence and tests are intentionally outside this package.

To roll back: keep this ZIP, extract the previous ZIP into a new directory, and run it.
Do not overwrite MAIN or manipulate its runtime, sessions, case state or Git history.
'@ | Set-Content -LiteralPath (Join-Path $stage 'LOCAL_README.txt') -Encoding utf8
$actual = @(Get-ChildItem -LiteralPath $stage -File -Recurse | ForEach-Object { [IO.Path]::GetRelativePath($stage,$_.FullName).Replace('\','/') })
if (Compare-Object ($allow | Sort-Object) ($actual | Sort-Object)) { throw 'Unexpected package entries' }
Add-Type -AssemblyName System.IO.Compression.FileSystem
[IO.Compression.ZipFile]::CreateFromDirectory($stage,$zip)
$archive = [IO.Compression.ZipFile]::OpenRead($zip)
try {
  $entries = @($archive.Entries | ForEach-Object {$_.FullName.Replace('\','/')})
  if (Compare-Object ($allow | Sort-Object) ($entries | Sort-Object)) { throw 'ZIP allowlist mismatch' }
  foreach ($entry in $archive.Entries) {
    $reader = [IO.StreamReader]::new($entry.Open())
    try { $content = $reader.ReadToEnd() } finally { $reader.Dispose() }
    if ($content -match 'PRIVATE-CANARY|TEST MODEL|local-error-reference|[A-Z]:[\\/]Users[\\/]|sk-[A-Za-z0-9]{20}|ghp_[A-Za-z0-9]{20}|@[A-Za-z0-9.-]+\.(com|net|org)') { throw "Package content review failed: $($entry.FullName)" }
  }
} finally { $archive.Dispose() }
$extracted = Join-Path $pilotRoot "artifacts\package-check-$stamp"
Expand-Archive -LiteralPath $zip -DestinationPath $extracted
$stdout = Join-Path $pilotRoot "artifacts\package-check-$stamp.stdout.txt"
$stderr = Join-Path $pilotRoot "artifacts\package-check-$stamp.stderr.txt"
$node = (Get-Command node).Source
$owned = Start-Process -FilePath $node -ArgumentList @('scripts/serve.mjs','8797') -WorkingDirectory $extracted -WindowStyle Hidden -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
try {
  $ready = $false
  for ($attempt=0; $attempt -lt 80; $attempt++) {
    if ($owned.HasExited) { throw 'Extracted pilot failed to start; inspect its local stderr.' }
    if ((Test-Path -LiteralPath $stdout) -and ((Get-Content -Raw -LiteralPath $stdout) -match 'http://127.0.0.1:8797')) { $ready=$true; break }
    Start-Sleep -Milliseconds 50
  }
  if (-not $ready) { throw 'Extracted pilot startup timeout' }
  $page = Invoke-WebRequest -Uri 'http://127.0.0.1:8797/' -UseBasicParsing
  $knowledge = Invoke-WebRequest -Uri 'http://127.0.0.1:8797/knowledge.json' -UseBasicParsing
  if ($page.StatusCode -ne 200 -or $page.Content -notmatch 'Troubleshooter') { throw 'Extracted pilot page failed' }
  $expectedKnowledge = Get-Content -Raw -LiteralPath (Join-Path $pilotRoot 'dist/knowledge.json')
  if ($knowledge.Content -cne $expectedKnowledge) { throw 'Extracted pilot knowledge differs from validated build' }
  $projected = $knowledge.Content | ConvertFrom-Json
  if ($projected.schemaVersion -ne 2 -or $projected.symptoms.Count -ne 25) { throw 'Extracted desktop symptom contract failed' }
  foreach ($relative in $allow) {
    if ((Get-FileHash -LiteralPath (Join-Path $stage $relative)).Hash -ne (Get-FileHash -LiteralPath (Join-Path $extracted $relative)).Hash) { throw "Extracted content mismatch: $relative" }
  }
} finally {
  if (-not $owned.HasExited) { Stop-Process -Id $owned.Id; $owned.WaitForExit() }
}
$report = @{
  zip = [IO.Path]::GetFileName($zip)
  sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $zip).Hash.ToLower()
  entryCount = $allow.Count
  entries = $allow
  sourceAndCaseContentExcluded = $true
  publicDeployment = $false
  extractedStandaloneHttpPassed = $true
  extractedOwnedProcessExited = $true
  cardCount = $projected.cards.Count
  navigationSymptomCount = $projected.symptoms.Count
  extractedAllEntryHashesMatched = $true
}
$report | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $pilotRoot 'artifacts\package-verification.json') -Encoding utf8
$report | ConvertTo-Json -Depth 4
