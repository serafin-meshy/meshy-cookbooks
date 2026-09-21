# Text prompt to hero prop

Turn one sentence into an Ultra 4K hero prop GLB in about 7 minutes.

**Endpoints:** `POST /openapi/v1/text-to-image` → `GET /openapi/v1/text-to-image/:id`, then `POST /openapi/v1/image-to-3d` → `GET /openapi/v1/image-to-3d/:id`  
**Credits:** ~44 per run (9 for the image, 35 for the model)  
**Time:** ~7 minutes  
**Languages:** Python 3.10+ · TypeScript (Node 22+)

## Run it

Live runs need a Meshy plan with API access (Pro, Premium, Ultra, Studio, or Enterprise) and about 44 credits. Create an API key at https://www.meshy.ai/developers/ and check your credit balance at https://www.meshy.ai/settings/subscription. Current rates are at https://docs.meshy.ai/en/api/pricing. Then:

**Python**

    cd examples/02-text-to-hero-prop/python
    python3 -m venv .venv && source .venv/bin/activate
    cp .env.example .env          # paste your key
    pip install -r requirements.txt
    python main.py

**TypeScript**

    cd examples/02-text-to-hero-prop/typescript
    cp .env.example .env          # paste your key
    npm install
    npm start

You get `output/hero-prop.glb`, the generated concept image at `output/hero-prop-concept.png`, and a 512 px preview at `output/hero-prop-thumbnail.png`. Open the GLB in Blender with File > Import > glTF 2.0.

To describe your own prop, pass the description:

    python main.py "A weathered pirate chest"
    npm start -- "A weathered pirate chest"

Each run overwrites the files in `output/`. Stopping a run does not cancel the task: the script prints each task ID first, and `client.get` with that ID returns the finished task for up to three days.

## Use with a coding agent

1. Clone the repository and open the folder in your coding agent:

       git clone https://github.com/serafin-meshy/meshy-cookbooks.git
       cd meshy-cookbooks

2. Paste this prompt as written. It names this cookbook and its included example, so there is nothing to fill in:

   > Read `AGENTS.md` and `examples/02-text-to-hero-prop/README.md`, then run the
   > included Marrow’s sea chest example with the default description and settings.
   > Tell me the expected Meshy credit cost and wait for my approval before generating.

3. The agent installs dependencies and tells you the expected credit cost. Once you approve, it runs the generation and reports the output files.

**Use your own asset:** Describe your own prop and ask the agent to pass that description instead.

**Integrate into a project:** Also provide your project path and describe how the
feature should work. The agent will adapt the matching Python or TypeScript implementation.

## How it works

1. **Generate the concept image from the prompt.** `client.create` POSTs the prompt to `/openapi/v1/text-to-image` with GPT Image 2.5 Sunburst and `remove_background` set, prints the new task ID, and returns it.

```python
concept_id = client.create(
    "text-to-image",
    {
        "ai_model": "gpt-image-2-5-sunburst",
        "prompt": PROMPT,
        "remove_background": True,
    },
)
```

   `remove_background` returns the chest as a transparent cut-out, and the three-quarter view asked for in the default prompt shows the 3D stage two sides of it instead of one.

2. **Save the completed concept image.** `client.wait` GETs `/openapi/v1/text-to-image/:id` every 5 seconds, printing each status change, and `client.download` saves the one entry in `image_urls`.

```python
concept = client.wait("text-to-image", concept_id)
client.download(concept["image_urls"][0], OUTPUT / "hero-prop-concept.png")
```

   This stage takes 37 to 40 seconds. Leave `generate_multi_view` off here: `image-to-3d` only accepts `input_task_id` from a task that produced one image, and the multi-image route is what cookbook 03 uses.

3. **Chain the image into an Ultra 4K image-to-3d task.** `client.create` POSTs to `/openapi/v1/image-to-3d` with `input_task_id` pointing at the text-to-image task, so the image never leaves Meshy.

```python
task_id = client.create(
    "image-to-3d",
    {
        "input_task_id": concept_id,
        "geometry_resolution": "4k",
        "should_texture": True,
        "enable_pbr": True,
        "texture_resolution": "4k",
        "target_formats": ["glb"],
    },
)
```

   `geometry_resolution: "4k"` runs the geometry pass at 4096³ for 5 extra credits, and `texture_resolution: "4k"` sets the size of the base color and normal maps at the same credit cost as the 2K default; they are two separate settings. `geometry_resolution` needs Meshy 7.1, which `latest` has resolved to since September 18, 2026, and the older `ultra_mode: true` still works as an alias for `"2k"`.

4. **Download the completed GLB and thumbnail.** `client.wait` polls `/openapi/v1/image-to-3d/:id` the same way, `client.download` streams `model_urls.glb` and `thumbnail_url` to disk, and the script prints the path and the credits of both tasks.

```python
task = client.wait("image-to-3d", task_id)
client.download(task["model_urls"]["glb"], OUTPUT / "hero-prop.glb")
client.download(task["thumbnail_url"], OUTPUT / "hero-prop-thumbnail.png")
```

   Generation takes between 6 min 09 s and 6 min 30 s, so most of the wait is here. The mesh comes back dense: 0.82 to 1.25 million triangles and 53 to 68 MB with the 4K maps, so plan on a decimation pass in Blender before it goes into a scene.

## Parameters worth changing

| Parameter | We use | Why |
|---|---|---|
| [`ai_model`](https://docs.meshy.ai/en/api/text-to-image#create-a-text-to-image-task) (text-to-image) | `"gpt-image-2-5-sunburst"` | 9 credits per image. `"nano-banana"` costs 3 and is fine for a first look |
| [`prompt`](https://docs.meshy.ai/en/api/text-to-image#create-a-text-to-image-task) | `PROMPT` | Name the prop, list its materials, and ask for a three-quarter view. Leave the background to the next parameter |
| [`remove_background`](https://docs.meshy.ai/en/api/text-to-image#create-a-text-to-image-task) | `true` | Returns a transparent PNG of just the prop, so the 3D stage gets a clean cut-out |
| [`input_task_id`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | the text-to-image task id | Chains the two tasks inside Meshy. Swap in `image_url` with a data URI of your own PNG to skip the prompt stage, as cookbook 01 does |
| [`geometry_resolution`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `"4k"` | Geometry pass resolution: `standard`, `2k` (2048³) or `4k` (4096³); either Ultra tier adds 5 credits. On the same two chest concepts, `2k` generated in 3 min 33 s to 3 min 36 s and `4k` in 6 min 09 s to 6 min 30 s, for 0.96 million triangles at `2k` against 0.93 to 1.12 million at `4k`, so the extra time buys finer surface detail rather than more triangles. Needs Meshy 7.1 and a single input image, so it is not an option in cookbook 03 |
| [`should_texture`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `true` | You want a textured model, not a gray mesh. Set `false` for geometry only, which drops the task to 25 credits with Ultra |
| [`enable_pbr`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `true` | Adds metallic, roughness and normal maps that Blender wires into the Principled BSDF on import. Needs `should_texture: true` |
| [`texture_resolution`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `"4k"` | 4096 × 4096 base color and normal maps at the same credit cost as 2K. `"8k"` costs 5 more and, on this chest, took 12 min 15 s for a 108 MB file with only the base color at 8192 × 8192 |
| [`target_formats`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `["glb"]` | Only generates what you asked for; faster task. Add `"fbx"` for Unity or Unreal |

`ai_model` on the 3D task is left out on purpose, so it runs on `latest`, which has been Meshy 7.1 since September 18, 2026 and was used for the measurements recorded in this README (documented September 21, 2026; the default can change).

## What you have now

`output/hero-prop.glb` is one mesh with one material and three JPEG textures: a 4096 × 4096 base color, a 4096 × 4096 normal map and a 2048 × 2048 metallic-roughness map, since `texture_resolution` applies to the base color and normal only. Marrow's sea chest has 1,121,650 triangles, is 63.9 MB on disk, and cost 44 credits including the concept image. It measures 1.90 m along its longest side because Meshy normalizes scale, so size it in Blender or your engine before it goes into a scene. Cookbook 03, product photos to a 4K product model, is next in the series and feeds several photos into `multi-image-to-3d`.
