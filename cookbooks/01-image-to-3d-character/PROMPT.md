# Adapt one image into a character or prop GLB

Read [AGENTS.md](../../AGENTS.md), this recipe's [README](README.md), the entry point for
my project's language, and its `shared/` API and run helpers before editing.
Adapt the existing implementation to my project and the asset I describe.

## Requirements

- Accept one PNG or JPEG via `--input`. Preserve `image-to-3d`, `should_texture: true`, `enable_pbr: true`, and `target_formats: ["glb"]`. Produce `character.glb` and `character-thumbnail.png`.
- Match the existing project's language and conventions. Keep API keys in the environment
  and API calls on the server when building a browser interface.
- Preserve sample defaults, custom output directories, offline dry runs, saved task IDs,
  payload checks, resumable downloads, and structured results. Reuse the shared helpers.
- If copying into another project, update imports and sample paths and include the dependencies.
- The recipe's recorded full-run estimate is ~30 credits. Explain the estimate before a
  live generation and execute only within my authorized scope. Offline checks need no key.
- Follow [RUNNING.md](../../RUNNING.md) on interruptions. Do not automatically create a
  replacement for a saved or uncertain task. A two-stage run may still need its unsubmitted stage.

## Acceptance criteria

- The setup and custom-input command work in the destination project.
- `--dry-run` builds the requested pipeline without API calls or run-file writes.
- TypeScript passes its type check, or Python passes the relevant offline checks.
- If a live run is requested, report output paths and available task-reported credits from
  `result.json`. An interrupted run can continue using its saved IDs.
- Report offline validation, live generation, GLB header validation, and visual inspection
  separately. Do not claim visual quality from a header check.

My requested asset or integration: **[describe it here]**.
