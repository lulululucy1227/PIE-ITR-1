# Agent Repair Assistant — Error Code local Pilot

Task: EC-MT-20260907-PILOT-001. Local review only; no external deployment or production integration.

## Run

Requires Node.js 22 or later. No npm install is needed.

From this directory:

    node scripts/build.mjs
    node scripts/serve.mjs

Open http://127.0.0.1:8796. Stop the owned preview with Ctrl+C. If the port is already occupied, choose another unused local port with node scripts/serve.mjs 8797. Port 8787 is explicitly refused. Do not stop an unrelated process to free a port.

On this machine, if node is not on PATH, the launcher also checks the bundled Codex Node runtime. Double-click run-pilot.cmd after building. The portable ZIP contains a ready build and the launcher; rebuilding requires the full specialist source folder.

## What is available

Eight selected code entries: 1202, 1008, 5510, 1000022, 1500, 5501, 6401 and DT-041. Exact code, exact message and candidate-only fuzzy search work offline after local startup. Observed symptoms lead to a concise safe action or PIE. Fixed is a user-reported result after checks, not verified closure or automatic NFF. Nothing is saved or sent.

The 1202 cable/mainboard sequence remains withheld from the agent data until its exact model scope is confirmed. Its canonical recommendation is not a measured success cohort. Historical firmware targets and single-case replacement outcomes are not current universal advice.

## Verify

    node --test test/core.test.mjs test/data.test.mjs test/build.test.mjs
    node test/browser.mjs
    node scripts/lifecycle-check.mjs

Browser tests use the bundled Playwright module and installed Edge; optionally set PLAYWRIGHT_MODULE and PILOT_BROWSER to your local installations. These are test-only dependencies, not portal dependencies. Synthetic replacement examples exist only inside tests.

Evidence, candidate ranking and scope gaps: docs/EVIDENCE_AUDIT.md.
Schema, projection and future read-only adapter: docs/DATA_CONTRACT.md.
Latest local handoff: docs/HANDOFF.md.
Generated evidence/screenshots/build manifest: artifacts/.

## Update and rollback

1. Preserve the previous ZIP and canonical knowledge revision.
2. Edit data/canonical.json with minimal source-backed facts. Do not add raw cases, identities, credentials or whole reference rows.
3. Confirm model/version applicability and failure/verification behavior. Keep unconfirmed knowledge pilot-only or withheld; formal approval is a separate PIE gate.
4. Run all checks, build, inspect the public projection and package using scripts/package.ps1.
5. Stop this Pilot's server before replacing a build. Start and verify the replacement. To roll back, extract a previous ZIP into a new directory and run that version; do not reset MAIN or delete history.

## Boundaries

This is the Error Code Specialist workspace, with its own Git objects and branch. It does not import MAIN code, access MAIN case state, change analyzer settings, use Nextop/Feishu sessions, write production records, send messages or provide public hosting. Only the five allowlisted files in dist are web-served. Internal canonical knowledge, source audit, tests and Git files are outside the served directory.

For later production, use a private HTTPS host behind the organization's existing identity provider, versioned reviewed knowledge releases and rollback. Do not expose this localhost preview server to the internet. Hosting/auth, external rollout and MAIN integration require a separate supervisor decision after the pilot gate.
