# PIE Troubleshooter — local desktop review

Task: EC-MT-20260908-DESKTOP-LONGRUN-003. Workspace: `C:\Users\Reggie\Desktop\PIE-ITR-ErrorCode`. Task/report channels: Issue #5 / Issue #6.

Open `run-pilot.cmd`, or run `node scripts/serve.mjs` inside this folder, then visit http://127.0.0.1:8796. Requires Node 22+; no npm install, account, database or cloud service. If that port is occupied, use `node scripts/serve.mjs 8797`. Stop your own preview with Ctrl+C. Port 8787 is refused.

The desktop home combines persistent product/model context, exact Error Code / Message search, and controlled symptom navigation. Both routes use the same repair card. Model/version/observable-condition checks protect narrowly applicable guidance. A PIE result means the next action needs case-specific review. This page does not diagnose from arbitrary free text, write tickets, close cases or assign NFF. Fixed is a local self-report.

See [knowledge decisions](docs/KNOWLEDGE_PROMOTION_AUDIT_2026-09-08.md), [data contract](docs/DATA_CONTRACT.md) and [current gate evidence](docs/HANDOFF.md). The original pilot evidence remains in [EVIDENCE_AUDIT.md](docs/EVIDENCE_AUDIT.md). The current desktop task supersedes the original project-wide 1202 blocker: its conflicting hardware paths stay frozen.

## Verify and package

Run from this folder:

```powershell
node --test test/*.test.mjs
node test/browser.mjs
node test/browser-zoom.mjs
node scripts/lifecycle-check.mjs
node scripts/build.mjs
pwsh -NoProfile -File scripts/package.ps1
```

Browser tests use locally installed Edge and the bundled Playwright runtime; `PILOT_BROWSER` and `PLAYWRIGHT_MODULE` can override their paths. Packaging is restricted to the isolated specialist directory and verifies an extracted standalone copy on port 8797. Generated `dist/` and `artifacts/` stay local and ignored by Git.

## Update and rollback

Edit internal `data/canonical.json`, verify scope and evidence under the current promotion policy, run the full checks, rebuild, inspect the generated projection and create a new ZIP. Never hand-edit dist or assume P0/P1 is approval. Keep prior ZIPs. To roll back, stop only this preview, extract a prior ZIP into a separate local directory and run its launcher. Do not overwrite MAIN or reset its Git/runtime/case state.

This is a local review product. External rollout, hosting/authentication and integration into MAIN need a separate task. No default/main push or merge is part of this release.
