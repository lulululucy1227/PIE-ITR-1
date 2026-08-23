# Persistent Project Handoff Protocol

Status: Active

## Purpose
Long-running PIE ITR work must be resumable across GPT chats and Codex sessions without treating conversation history as the sole project state.

## Handoff content
A compact handoff should capture, as applicable:
- current architecture and durable business boundaries;
- stable baseline / relevant commit or branch;
- current phase and authorization state;
- completed work;
- tests/build status;
- unresolved risks/issues;
- next authorized priority;
- important safety/write constraints.

Do not put secrets, credentials, raw customer data or unnecessary production evidence in the handoff.

## Update rule
At stable engineering milestones, update the handoff/status before or with the Git checkpoint. Keep it compact; do not turn it into a transcript.

## Recovery rule
A new GPT/Codex session should recover from Git + handoff/status first. Do not overwrite newer local work with an older remote baseline. Inspect repository status, branch, remote and relevant diffs before synchronization when local/remote divergence is possible.
