# PIE Troubleshooter — Controlled Selection UI Correction

Status: ACTIVE UX CORRECTION
Owner: Troubleshooter｜主管
Date: 2026-09-08

## Problem
The latest identification page incorrectly converted the main diagnostic inputs into free-text fields. This violates the controlled-symptom architecture.

## Required Page 1 behavior
Page 1 is identification-only and must use controlled selections for all structured fields.

### 1. Mower model
- Required controlled selection.
- Use a dropdown / searchable select populated from the supported model list.
- Do not allow arbitrary free-text model names as the normal path.

### 2. Observable area
- Required controlled selection when using symptom navigation.
- Use a compact select or controlled option list from the approved areas.
- Do not use free text.

### 3. Observed symptom
- Required controlled selection from the approved Controlled Symptom library.
- Filter available symptoms by selected Observable Area and model when applicable.
- Do not allow arbitrary free-text symptom descriptions to drive diagnosis or repair.

### 4. Error Code / Error Message
- Optional text/search input is allowed because agents may paste an exact code or message.
- Exact/fuzzy matching returns candidate mappings only; it must not bypass scope checks.
- When an exact code uniquely maps to a controlled symptom, the UI may preselect/suggest that symptom, but the user should still see the controlled selection before continuing.

### 5. Firmware version
- Optional and collapsed by default.
- Text entry is acceptable unless a reliable scoped version list exists.

## Recommended simple layout
Keep the page visually simple. Do not reintroduce a large dashboard.

Suggested order:
1. Mower model — select
2. Error Code / Error Message — optional search input
3. Observable Area — select or compact option row
4. Observed Symptom — filtered select/options
5. Firmware version — optional collapsed
6. Continue

Alternative compact interaction:
- Model select
- Optional Error Code search
- Area cards/select
- Symptom buttons/select filtered by area

Either is acceptable if it remains controlled and fast.

## Free-text boundary
`Other / None of these` may open an optional free-text field only for taxonomy feedback / PIE escalation.
That text must never directly generate a part, repair action or replacement recommendation.

## Two-page contract remains unchanged
- Page 1 = identify only.
- Page 2 = approved repair / verification or safe PIE next step.
- No part/repair/verification content may leak onto Page 1.

## State rules
- Changing model, area, symptom, error code or relevant scope invalidates any previous Page 2 result.
- Browser Back restores the prior controlled selections.
- Invalid/deep links cannot expose stale repair content.

## Acceptance
- Model input is no longer plain free text.
- Observed symptom is no longer plain free text.
- Controlled selection remains the only path that can lead to a Repair Card.
- Error Code / Message remains optional text search.
- `Other` free text routes to PIE/taxonomy review only.
- Existing stable-guidance knowledge, 1202 freeze and two-page separation remain unchanged.

