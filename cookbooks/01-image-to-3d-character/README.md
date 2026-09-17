# Concept art to game character

Turn one piece of character concept art into a textured GLB in 5 to 9 minutes.

**Endpoints:** `POST /openapi/v1/image-to-3d` → `GET /openapi/v1/image-to-3d/:id`  
**Credits:** ~30 per run  
**Time:** ~5 to 9 minutes  
**Languages:** Python 3.10+ · TypeScript (Node 22+)

## Run it

Live runs need a Meshy plan with API access (Pro, Premium, Ultra, Studio, or Enterprise) and about 30 credits. Create an API key at https://www.meshy.ai/settings/api and check your credit balance at https://www.meshy.ai/settings/subscription. Current rates are at https://docs.meshy.ai/en/api/pricing. Then:

**Python**

    cd cookbooks/01-image-to-3d-character/python
    python3 -m venv .venv && source .venv/bin/activate
    cp .env.example .env          # paste your key
    pip install -r requirements.txt
    python main.py

**TypeScript**

    cd cookbooks/01-image-to-3d-character/typescript
    cp .env.example .env          # paste your key
    npm install
    npm start

You get `output/character.glb` and a 512 px preview at `output/character-thumbnail.png`. Open the GLB in Blender with File > Import > glTF 2.0.

## Use with a coding agent

**Try the included example:** Open this repository in your coding agent and paste:

> Follow `cookbooks/01-image-to-3d-character/PROMPT.md` to prepare
> the included armored-character example from `input/concept-art.png`.
> Keep the default settings and run the offline checks. Explain the expected Meshy
> credit cost and wait for my approval before generating.

The agent reads [PROMPT.md](PROMPT.md) for the detailed instructions; you do not need
to paste a second prompt or fill in any placeholders to try this example.

**Use your own asset:** Provide the path to your own PNG or JPEG and ask the agent to use it with `--input`.

**Integrate into a project:** Also provide your project path and describe how the
feature should work. The agent will adapt the matching Python or TypeScript implementation.

## Custom inputs and resume

From the selected language folder, validate the sample with `python main.py --dry-run`
or `npm run dry-run`. No API key, network request, or output files are needed.
For your own asset:

```sh
python main.py --input /path/to/character.png --output /path/to/new-run --dry-run
npm start -- --input /path/to/character.png --output /path/to/new-run --dry-run
```

Choose one language and remove `--dry-run` for a paid generation. Defaults still work
with `python main.py` / `npm start`. Bundled paths are relative to the entry point;
custom paths are relative to your working directory. The output folder also contains
`result.json` with saved task IDs, status, artifact paths/checksums, and reported credits.

To continue, repeat the original command and input flags with `--resume` and the same
`--output`, without `--dry-run`. A new asset needs a new output directory. See
[run and recovery details](../../RUNNING.md) for uncertain submissions, stale locks,
and the limits of offline and GLB checks. TypeScript validation: `npm run check`.

## How it works

1. **Encode the art and create the task.** `Meshy.data_uri` reads `input/concept-art.png` into a base64 data URI, and `run.task` creates or resumes a task and polls it; new tasks POST the payload to `/openapi/v1/image-to-3d` and `run.task` returns the completed task after polling.

```python
        task = run.task(
            "model",
            "image-to-3d",
            {
                "image_url": Meshy.data_uri(args.input[0]),
                "should_texture": True,
                "enable_pbr": True,
                "target_formats": ["glb"],
            },
        )
```

   A data URI means you never have to host the image anywhere. The sample is the armored character from the Meshy quick start guide; swap in your own PNG or JPG at the same path.

2. **Resume and poll until the task finishes.** `run.task` saves the task ID before polling, then GETs `/openapi/v1/image-to-3d/:id` every 5 seconds, prints each status change, and returns the task object once the status is `SUCCEEDED`.

   On `FAILED` or `CANCELED` it raises with `task_error.message` and the script exits non-zero, and Meshy refunds the credits of a `FAILED` task. The three runs behind this README took between 4 min 44 s and 9 min 16 s end to end, almost all of it generation rather than queue time, so expect to wait.

3. **Download the GLB and the thumbnail.** `run.download` streams the signed `model_urls.glb` URL to `output/character.glb` and `thumbnail_url` to `output/character-thumbnail.png`, then the run records paths and `consumed_credits` in `result.json`.

```python
        run.download(task["model_urls"]["glb"], "character.glb")
        run.download(task["thumbnail_url"], "character-thumbnail.png")
```

   The mesh comes back dense: 731,336 to 898,428 triangles and 27.4 to 32.2 MB across the three runs behind this README, far heavier than a game-ready asset, so plan on a decimation pass in Blender before it goes into a scene.

## Parameters worth changing

| Parameter | We use | Why |
|---|---|---|
| [`image_url`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | data URI of `input/concept-art.png` | Works from a local file with no hosting step. A public URL works too |
| [`should_texture`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `true` | You want a textured model, not a gray mesh. Set `false` for geometry only |
| [`enable_pbr`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `true` | Adds metallic, roughness and normal maps that Blender wires into the Principled BSDF on import. Needs `should_texture: true` |
| [`target_formats`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `["glb"]` | Only generates what you asked for; faster task. Blender imports GLB natively. Add `"fbx"` or `"obj"` for other tools |

`ai_model` is left out on purpose, so the task runs on `latest`, which used Meshy 7 for the measurements recorded in this README (documented September 16, 2026; the default can change).

## What you have now

`output/character.glb` is one mesh with one material and three 2048 × 2048 JPEG textures: base color, metallic-roughness and normal. It stands 1.90 m tall in scene units, has 813,722 triangles, is 29.7 MB on disk, and cost 30 credits. Cookbook 02, text prompt to hero prop, is next in the series and starts from a sentence instead of art.
