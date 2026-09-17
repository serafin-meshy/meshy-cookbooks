# Using the Meshy cookbooks

Start with the user's outcome, choose one recipe, and read its README, PROMPT.md,
selected language's main file, and shared helpers. Keep context limited to those files.

| Input / outcome | Recipe | Notes |
|---|---|---|
| One image → character or prop GLB | `cookbooks/01-image-to-3d-character` | One PNG or JPEG |
| Description → textured prop GLB | `cookbooks/02-text-to-hero-prop` | Text → concept image → 3D; preserve `input_task_id` chaining |
| Product views → GLB and USDZ | `cookbooks/03-photos-to-product-model` | 1–4 images; front first |

## Adapt to a project

- Choose the language matching the existing project. Both versions implement the same recipe.
- Read `shared/python/meshy.py` and `run.py`, or `shared/typescript/meshy.ts` and `run.ts`.
  Copy both when retaining the CLI/resume behavior. Update imports to match the destination project.
- Keep API requests on the server in browser applications. Read `MESHY_API_KEY` from the
  environment or local `.env`; never embed it in client code or ask for it in a chat message.
- Preserve explicit `target_formats`, texturing settings, and literal API payloads.
- Use the CLI arguments for custom inputs. Built-in samples work without arguments.
- Read [RUNNING.md](RUNNING.md) for exact setup, execution, recovery, and result semantics.
- A live run spends credits. State the recipe's approximate cost before execution;
  run when the user's instructions authorize it. Otherwise prepare the command and run offline checks.

## Validate and report

- First run `python main.py --dry-run` or `npm run dry-run` in the selected language folder.
  This makes no network calls, requires no API key, and writes no run artifacts.
- TypeScript: run `npm run check` in the recipe's `typescript/` directory.
- Repository tests: see [tests/README.md](tests/README.md). They use fake responses and no credits.
- Report separately: offline checks passed, live API generation succeeded, GLB header validated,
  and visual quality reviewed. Header validation is not a geometry or visual-quality review.
- Read `output/result.json` for task IDs, status, actual reported credits, and artifact paths.
  A credit total includes only values reported by fetched tasks; it is not a billing ledger.
- Resume an interrupted run with the original input flags and `--resume --output <same-folder>`.
  Never delete a saved run or resubmit an uncertain POST just to make a retry pass.

## Maintain this repository

- Keep Python and TypeScript payloads, stages, flags, and filenames aligned.
- Keep examples short; lifecycle handling belongs in `shared/*/run.*`.
- Update README code excerpts from the actual Python entry point when changing it.
- Keep author notes and credentials private. Do not publish `COOKBOOK_STANDARDS.md` or `.env`.
- Do not change model defaults or credit estimates without evidence. Existing measurements are
  historical; `latest` can change. Save the requested model and an API-reported model when available.
