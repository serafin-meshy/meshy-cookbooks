# Product photos to a 4K product model

Turn three product photos into a life-size, 4K-textured GLB and USDZ in under 6 minutes.

**Endpoints:** `POST /openapi/v1/multi-image-to-3d` → `GET /openapi/v1/multi-image-to-3d/:id`  
**Credits:** ~35 per run (30 for the model, 5 for Ultra)  
**Time:** ~5 to 6 minutes  
**Languages:** Python 3.10+ · TypeScript (Node 22+)

## Run it

Live runs need a Meshy plan with API access (Pro, Premium, Ultra, Studio, or Enterprise) and about 35 credits. Create an API key at https://www.meshy.ai/settings/api and check your credit balance at https://www.meshy.ai/settings/subscription. Current rates are at https://docs.meshy.ai/en/api/pricing. Then:

**Python**

    cd cookbooks/03-photos-to-product-model/python
    python3 -m venv .venv && source .venv/bin/activate
    cp .env.example .env          # paste your key
    pip install -r requirements.txt
    python main.py

**TypeScript**

    cd cookbooks/03-photos-to-product-model/typescript
    cp .env.example .env          # paste your key
    npm install
    npm start

You get `output/armchair.glb`, `output/armchair.usdz` and four 512 px renders, `output/armchair-front.png`, `-right.png`, `-back.png` and `-left.png`. Drop the GLB on https://modelviewer.dev/editor to see it with its PBR maps and copy the `<model-viewer>` embed tag; select the USDZ in Finder and press Space for Quick Look.

## Use with a coding agent

1. Clone the repository and open the folder in your coding agent:

       git clone https://github.com/serafin-meshy/meshy-cookbooks.git
       cd meshy-cookbooks

2. Paste this prompt as written. It names this cookbook and its included example, so there is nothing to fill in:

   > Follow `cookbooks/03-photos-to-product-model/PROMPT.md` to prepare
   > the included armchair example from `input/armchair-001/1-front.jpg`,
   > `input/armchair-001/2-back.jpg`, and `input/armchair-001/3-side.jpg`, in that order.
   > Keep the default settings and run the offline checks. Explain the expected Meshy
   > credit cost and wait for my approval before generating.

3. The agent reads [PROMPT.md](PROMPT.md), installs dependencies, runs the offline checks, and tells you the
   expected credit cost. Once you approve, it runs the generation and reports the output files.

**Use your own asset:** Provide one to four PNG or JPEG paths, front view first, and ask the agent to repeat `--input` for each view.

**Integrate into a project:** Also provide your project path and describe how the
feature should work. The agent will adapt the matching Python or TypeScript implementation.

## Custom inputs and resume

From the selected language folder, validate the sample with `python main.py --dry-run`
or `npm run dry-run`. No API key, network request, or output files are needed.
For your own asset:

```sh
python main.py --input /path/to/front.jpg --input /path/to/back.jpg --output /path/to/new-run --dry-run
npm start -- --input /path/to/front.jpg --input /path/to/back.jpg --output /path/to/new-run --dry-run
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

1. **Encode the three photos and create the task.** `Meshy.data_uri` reads each JPEG in `PHOTOS` into a base64 data URI, and `run.task` creates or resumes a task and polls it; new tasks POST them as one `image_urls` list to `/openapi/v1/multi-image-to-3d` with Ultra mode, 4K textures, life-size scaling and both output formats, and `run.task` returns the completed task after polling.

```python
        task = run.task(
            "model",
            "multi-image-to-3d",
            {
                "image_urls": [Meshy.data_uri(p) for p in args.input],
                "ultra_mode": True,
                "should_texture": True,
                "enable_pbr": True,
                "texture_resolution": "4k",
                "auto_size": True,
                "origin_at": "bottom",
                "multi_view_thumbnails": True,
                "target_formats": ["glb", "usdz"],
            },
        )
```

   Meshy 7 treats the first image as the front view and the rest as unordered, so `1-front.jpg` comes first in `PHOTOS`. The sample photos were generated with Meshy text-to-image; `input/SOURCES.md` has the prompt. Swap in one to four of your own JPG or PNG photos at the same paths.

2. **Resume and poll until the task finishes.** `run.task` saves the task ID before polling, then GETs `/openapi/v1/multi-image-to-3d/:id` every 5 seconds, prints each status change, and returns the task object once the status is `SUCCEEDED`.

   On `FAILED` or `CANCELED` it raises with `task_error.message`, and after 30 minutes it raises `MeshyTimeoutError`. The armchair took 4 min 42 s to 5 min 45 s to generate in the four runs behind this README. Formats are converted after generation, and that step is where a dense mesh can stall: a plush toy tried while building this cookbook sat at 99 percent for 27 minutes and then failed with `format_conversion_failed`, refunded.

3. **Download the GLB, the USDZ and the four renders.** `run.download` streams `model_urls.glb` and `model_urls.usdz` to `output/`, then each entry of `thumbnail_urls`, and the run records paths and `consumed_credits` in `result.json`.

```python
        run.download(task["model_urls"]["glb"], "armchair.glb")
        run.download(task["model_urls"]["usdz"], "armchair.usdz")
        for view, url in task["thumbnail_urls"].items():
            run.download(url, f"armchair-{view}.png")
```

   The mesh comes back dense for the web: 178,052 to 223,548 triangles and 28.9 to 31.6 MB for the GLB with its 4K maps in the four runs behind this README, so plan on a decimation pass and texture compression before it goes on a product page.

## Parameters worth changing

| Parameter | We use | Why |
|---|---|---|
| [`image_urls`](https://docs.meshy.ai/en/api/multi-image-to-3d#create-a-multi-image-to-3d-task) | three data URIs, front first | The first image is the primary view on Meshy 7; the others fill in the back and sides. One photo works, four is the maximum |
| [`ultra_mode`](https://docs.meshy.ai/en/api/multi-image-to-3d#create-a-multi-image-to-3d-task) | `true` | Higher-fidelity geometry with finer surface detail, for 5 extra credits. Only on Meshy 7 |
| [`should_texture`](https://docs.meshy.ai/en/api/multi-image-to-3d#create-a-multi-image-to-3d-task) | `true` | You want a textured model, not a gray mesh. Set `false` for geometry only, which drops the task to 25 credits with Ultra |
| [`enable_pbr`](https://docs.meshy.ai/en/api/multi-image-to-3d#create-a-multi-image-to-3d-task) | `true` | Adds metallic, roughness and normal maps that model-viewer and three.js render without extra setup. Needs `should_texture: true` |
| [`texture_resolution`](https://docs.meshy.ai/en/api/multi-image-to-3d#create-a-multi-image-to-3d-task) | `"4k"` | 4096 × 4096 base color and normal maps instead of the 2048 default, at the same credit cost. `"8k"` costs 5 more |
| [`auto_size`](https://docs.meshy.ai/en/api/multi-image-to-3d#create-a-multi-image-to-3d-task) | `true` | Scales the model to an estimated real-world size, so AR Quick Look shows it at the right size; without it, every model in cookbooks 01 and 02 came back 1.90 m tall whatever it depicts. The armchair came back 0.80 to 0.85 m tall across four runs. It is an estimate from the photos: a wooden toy car tried while building this cookbook came back as a 2.8 m car, so check the number |
| [`origin_at`](https://docs.meshy.ai/en/api/multi-image-to-3d#create-a-multi-image-to-3d-task) | `"bottom"` | Puts the origin under the model so it sits on the floor in a viewer. Use `"center"` for things that hang or float |
| [`multi_view_thumbnails`](https://docs.meshy.ai/en/api/multi-image-to-3d#create-a-multi-image-to-3d-task) | `true` | Front, right, back and left renders as transparent 512 px PNGs for about three extra seconds. The front one is the same image the API returns as `thumbnail_url` |
| [`target_formats`](https://docs.meshy.ai/en/api/multi-image-to-3d#create-a-multi-image-to-3d-task) | `["glb", "usdz"]` | GLB for the web viewer, USDZ for AR Quick Look on iOS; every format is a conversion step after generation. Add `"fbx"` for a game engine |

`ai_model` is left out on purpose, so the task runs on `latest`, which used Meshy 7 for the measurements recorded in this README (documented September 16, 2026; the default can change); Ultra mode needs it.

## What you have now

`output/armchair.glb` is one mesh with one material and three JPEG textures: a 4096 × 4096 base color, a 4096 × 4096 normal map and a 2048 × 2048 metallic-roughness map, since `texture_resolution` applies to the base color and normal only. It stands 0.85 m tall in scene units with its origin on the floor, has 217,118 triangles, is 31.4 MB on disk next to a 32.3 MB USDZ, and cost 35 credits.

Download everything now: Meshy deletes API results after three days on every plan except Enterprise. This is the last cookbook in the series for now; the shared helper in `shared/` is the piece to copy into your own project.
