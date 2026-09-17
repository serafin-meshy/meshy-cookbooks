# Run, adapt, and resume a cookbook

Each recipe has matching Python and TypeScript commands. Choose one language.
Commands below start at the repository root unless a different directory is shown.

## Setup

For Python 3.10+, in the recipe's `python/` folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

On Windows, activate with `.venv\Scripts\activate` instead. Put the key in that local
`.env` file, or supply `MESHY_API_KEY` through your environment. Do not overwrite an existing `.env`.

For Node 22+, in the recipe's `typescript/` folder:

```sh
npm install
cp .env.example .env
npm run check
```

Both helpers load `.env` next to the entry point. An existing environment variable takes
precedence. The default input and output paths are anchored to the entry point, so launching
from another directory works. Custom relative paths resolve from the current working directory.

## Inputs and offline checks

From the selected language folder:

```sh
# Validate the bundled sample and print the planned requests and outputs.
python main.py --dry-run
npm run dry-run

# Recipe 01: one image. Use an actual local path.
python main.py --input /path/to/character.png --output /path/to/character-run --dry-run
npm start -- --input /path/to/character.png --output /path/to/character-run --dry-run

# Recipe 02: a description.
python main.py --prompt "A weathered pirate chest" --output /path/to/chest-run --dry-run
npm start -- --prompt "A weathered pirate chest" --output /path/to/chest-run --dry-run

# Recipe 03: repeat --input for each view, front first (1–4 PNG/JPEG files).
python main.py --input /path/to/front.jpg --input /path/to/back.jpg --output /path/to/chair-run --dry-run
npm start -- --input /path/to/front.jpg --input /path/to/back.jpg --output /path/to/chair-run --dry-run
```

Run only the command matching your recipe and language. Remove `--dry-run` to make
the paid API requests. The README lists historical cost and time estimates, not guarantees.
`--help` lists supported flags. Dry runs check file readability, image signatures, input
count, and nonempty prompts, then construct the actual payloads. Base64 contents are
omitted from the printed plan. They do not verify credentials, server-side acceptance,
image decodability, or model quality, and do not create the output folder.

## Resume

Each output directory is one run. The default is `output/` inside the language folder.
Use a new directory for a different asset. A directory containing `result.json` requires
`--resume`; the scripts never silently replace its paid generation. A folder containing older outputs without a manifest also requires a new directory.

```sh
# Repeat any original --input or --prompt flags as well.
python main.py --resume --output /path/to/chair-run
npm start -- --resume --output /path/to/chair-run
```

The saved run is bound to the recipe, input contents/order, and prompt. Each submitted
stage is also bound to its payload. Changing those values requires a new output folder.
Keep your original input files available. A fully complete run with matching artifact
checksums returns locally without contacting Meshy. An incomplete run polls saved task IDs
to obtain fresh download URLs and skips downloads whose local checksums still match.
For the text recipe, both stage IDs are saved separately; resuming may submit its second
stage if the first finished before the interruption. That remaining stage still costs credits.

The API client retries explicit HTTP 429 responses up to three times. Network failures and
other HTTP responses do not automatically retry a create request. If a POST may have succeeded
but no ID was saved, the stage remains `SUBMITTING` and resume stops. Reconcile the request
with Meshy task history/support before proceeding. If the matching task ID is confirmed,
record it in that stage's `id` field in `result.json`, preserving the endpoint and payload hash,
then resume. Only start a new run after establishing the earlier request did not create a task,
or when intentionally requesting a separate generation.

Polling timeouts leave the saved ID available for another resume; they do not cancel the
remote task. Failed/canceled/expired tasks are not automatically regenerated. If API results
are no longer available, recovery may require a deliberate new generation.

An exclusive `.run.lock` prevents simultaneous writers. Normal completion and handled errors
remove it. A killed process may leave it behind: confirm no process is using that output
folder before deleting **only** `.run.lock` and resuming. Do not delete `result.json` to recover.

## Results and validation

`result.json` is atomically updated before submission, after receipt of each task ID,
after polling, and after each successful download. It contains:

| Field | Meaning |
|---|---|
| `schema_version`, `recipe` | Saved-run format and recipe identity |
| `configuration` | Prompt and ordered input-content hashes |
| `status` | `RUNNING`, `SUCCEEDED`, `ERROR`, or `INTERRUPTED` |
| `tasks` | Stage → endpoint, payload hash, ID, status, requested model, reported credits; reported model if available |
| `artifacts` | Filename → absolute local path, byte size, SHA-256, validation performed |
| `consumed_credits` | Sum of available task-reported credit values, counted once per stage |

A hard termination can leave status `RUNNING`; it does not establish whether the remote
task failed. This file contains your prompt but no API key, input base64, or signed result URLs.
Treat it as local project data. Custom output directories should be added to your project's
ignore rules when they are inside a repository.

Downloads use temporary `.part` files and rename only after success. GLBs are checked for
the version-2 header and declared file length; other artifacts are checked for nonzero size.
This is a basic file check, not a full glTF validator or visual review. Inspect the preview
and open the model in Blender or your target viewer before using it.
