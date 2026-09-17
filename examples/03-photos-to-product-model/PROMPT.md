# Prepare the included product example

Read [AGENTS.md](../../AGENTS.md), this recipe's [README](README.md), the selected
language's entry point, and its `shared/` API and run helpers before proceeding.
Use my preferred language; if I have not specified one and there is no existing
project to match, use Python.

## Default request

Unless I request a custom asset or integration, prepare the included armchair example from `input/armchair-001/1-front.jpg`,
`input/armchair-001/2-back.jpg`, and `input/armchair-001/3-side.jpg`, in that order.
Use the bundled implementation and its default settings. Set up dependencies and
run the offline checks first; no API key is needed for those checks. Explain the
expected Meshy credit cost and wait for my approval before generating.

## Optional customization

- **My own asset:** When I provide one to four PNG or JPEG paths, repeat `--input` for each view, front first. Use CLI flags instead of changing the sample defaults.
- **My existing project:** When I provide a project path and describe an integration,
  adapt the matching implementation to that project. Otherwise, use this cookbook in place.

## Requirements

- Accept 1–4 PNG/JPEG files by repeating `--input`; the front view comes first. Preserve multi-image-to-3d, Ultra/4K settings, estimated real-world scale, bottom origin, and multiview thumbnails. Produce `armchair.glb`, `armchair.usdz`, and front/right/back/left PNG previews. Explain that estimated scale needs checking and the model may need optimization for the web.
- For an integration, match the existing project's language and conventions. Keep API keys in the environment
  and API calls on the server when building a browser interface.
- Preserve sample defaults, custom output directories, offline dry runs, saved task IDs,
  payload checks, resumable downloads, and structured results. Reuse the shared helpers.
- If copying into another project, update imports and sample paths and include the dependencies.
- The recipe's recorded full-run estimate is ~35 credits. Explain the estimate before a
  live generation and wait for my approval before making paid requests. If I have already
  explicitly approved that run, proceed within that scope. Offline checks need no key.
- Follow [RUNNING.md](../../RUNNING.md) on interruptions. Do not automatically create a
  replacement for a saved or uncertain task. A two-stage run may still need its unsubmitted stage.

## Acceptance criteria

- The setup and sample dry-run command work in the selected language folder.
- For a custom asset or integration, the requested command works in the destination.
- `--dry-run` builds the requested pipeline without API calls or run-file writes.
- TypeScript passes its type check, or Python passes the relevant offline checks.
- If a live run is requested, report output paths and available task-reported credits from
  `result.json`. An interrupted run can continue using its saved IDs.
- Report offline validation, live generation, GLB header validation, and visual inspection
  separately. Do not claim visual quality from a header check.
