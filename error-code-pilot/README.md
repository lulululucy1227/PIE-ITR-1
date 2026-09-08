# PIE Troubleshooter — local desktop review

Task: EC-MT-20260908-STABLE-GUIDANCE-PROMOTION-006. Workspace: `C:\Users\Reggie\Desktop\PIE-ITR-ErrorCode`. Task/report channels: Issue #5 / Issue #6.

Open `run-pilot.cmd`, or run `node scripts/serve.mjs` inside this folder, then visit http://127.0.0.1:8796. Requires Node 22+; no npm install, account, database or cloud service. If that port is occupied, use `node scripts/serve.mjs 8797`. Stop your own preview with Ctrl+C. Port 8787 is refused.

The [2026-09-08 user-requested homepage refinement](docs/UI_SIMPLIFICATION_2026-09-08.md) replaces the tile navigation with a centered text form. Observed symptom is required; Error Code / Message is optional. Model is a text input and firmware is folded away until needed. Open the local HTTP address, not the source HTML file directly.

Page 1 identifies the problem using the description and optional context. Exact symptom labels/aliases use existing guides; other wording offers explicit candidate choices or a PIE exit, without diagnosing arbitrary text. Code alone cannot bypass the required observation. It contains no repair recommendation or verification steps. Continue opens Page 2 for the approved action and verification, or a safe PIE next step. Browser Back restores inputs; edits invalidate old solutions. Refresh/direct solution links return safely to identification. Fixed is a local self-report; the app does not write tickets, close cases or assign NFF.

See [candidate ingestion decisions](docs/KNOWLEDGE_INGEST_AUDIT_2026-09-08.md), [existing knowledge decisions](docs/KNOWLEDGE_PROMOTION_AUDIT_2026-09-08.md), [data contract](docs/DATA_CONTRACT.md) and [current gate evidence](docs/HANDOFF.md). The original pilot evidence remains in [EVIDENCE_AUDIT.md](docs/EVIDENCE_AUDIT.md). The current task permits local completion with conflicting 1202 hardware paths frozen.

The newer [stable-guidance audit](docs/STABLE_GUIDANCE_AUDIT_2026-09-08.md) records nine supervisor-approved candidate portions now available through ten scoped Page2 cards. No-charge and station-recognition retain separate model scopes. The remaining ten candidates stay PIE-only;1202 is separately frozen. Historical zero-promotion reports describe the earlier evidence stage.

## Verify and package

Run from this folder:

```powershell
node scripts/ingest-candidates.mjs --check
node --test test/*.test.mjs
node test/browser.mjs
node test/simple-home.mjs
node test/stable-browser.mjs
node test/browser-zoom.mjs
node scripts/lifecycle-check.mjs
node scripts/build.mjs
pwsh -NoProfile -File scripts/package.ps1
```

Browser tests use locally installed Edge and the bundled Playwright runtime; `PILOT_BROWSER` and `PLAYWRIGHT_MODULE` can override their paths. Packaging is restricted to the isolated specialist directory and verifies an extracted standalone copy on port 8797. Generated `dist/` and `artifacts/` stay local and ignored by Git.

If8796 is occupied, preserve the existing process and test an unused specialist port with `node scripts/lifecycle-check.mjs 8806`. The two-page browser suite is `test/two-page.mjs`, called by the standard browser entry above. It includes a synthetic multi-step fixture solely to verify fallback behavior; that fixture is never packaged.

## Update and rollback

Edit internal `data/canonical.json`, verify scope and evidence under the current promotion policy, run the full checks, rebuild, inspect the generated projection and create a new ZIP. Never hand-edit dist or assume P0/P1 is approval. Keep prior ZIPs. To roll back, stop only this preview, extract a prior ZIP into a separate local directory and run its launcher. Do not overwrite MAIN or reset its Git/runtime/case state.

The actual 19 sanitized Feishu candidates and separate frozen1202 are retained in private `data/feishu-candidates.json`. Each source field stays separate from its reviewed decision. `--check` verifies source parity, hash, IDs, review gates and internal symptom links; `--write` reproduces the same reviewed import from the pinned payload. A changed payload deliberately requires a fresh per-record review and matching crosswalk updates before it can be written or built. The command does not invent review decisions or bootstrap approval. The JSON, source payload, importer and review audit are outside both the HTTP allowlist and standalone ZIP.

This is a local review product. External rollout, hosting/authentication and integration into MAIN need a separate task. No default/main push or merge is part of this release.
