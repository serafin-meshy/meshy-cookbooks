# Prepare the included hero-prop example

Read [AGENTS.md](../../AGENTS.md), this recipe's [README](README.md), the selected
language's entry point, and its `shared/` API and run helpers before proceeding.
Use my preferred language; if I have not specified one and there is no existing
project to match, use Python.

## Default request

Unless I request a custom asset or integration, prepare the included Marrow’s sea chest example using the entry point’s default `PROMPT` description.
Use the bundled implementation and its default settings. Set up dependencies and
run the offline checks first; no API key is needed for those checks. Explain the
expected Meshy credit cost and wait for my approval before generating.

## Optional customization

- **My own asset:** When I describe a different prop, pass my description with `--prompt`. Use CLI flags instead of changing the sample defaults.
- **My existing project:** When I provide a project path and describe an integration,
  adapt the matching implementation to that project. Otherwise, use this cookbook in place.

## Requirements

- Accept a nonempty description via `--prompt`. Preserve text-to-image followed by image-to-3d, with the concept task ID passed as `input_task_id`. Keep the current model and Ultra/4K settings unless the user requests a change. Produce `hero-prop-concept.png`, `hero-prop.glb`, and `hero-prop-thumbnail.png`.
- For an integration, match the existing project's language and conventions. Keep API keys in the environment
  and API calls on the server when building a browser interface.
- Preserve sample defaults, custom output directories, offline dry runs, saved task IDs,
  payload checks, resumable downloads, and structured results. Reuse the shared helpers.
- If copying into another project, update imports and sample paths and include the dependencies.
- The recipe's recorded full-run estimate is ~44 credits. Explain the estimate before a
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
