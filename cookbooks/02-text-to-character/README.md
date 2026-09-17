# Text prompt to T-posed character

Turn one sentence into a T-posed, 4K-textured character GLB in 6 to 9 minutes.

**Endpoints:** `POST /openapi/v1/text-to-image` → `GET /openapi/v1/text-to-image/:id`, then `POST /openapi/v1/image-to-3d` → `GET /openapi/v1/image-to-3d/:id`  
**Credits:** ~44 per run (9 for the image, 35 for the model)  
**Time:** ~6 to 9 minutes  
**Languages:** Python 3.10+ · TypeScript (Node 22+)

## Who this is for

Indie developers who need a character they can rig and animate but have a description instead of art. You write one sentence and get back a T-posed character with 4K base color, metallic, roughness and normal maps.

## Run it

Get an API key at https://www.meshy.ai/settings/api. The API is pay-before-you-go: this recipe spends about 44 credits per run, and API usage is bought at https://www.meshy.ai/settings/subscription. Then:

**Python**

    cd cookbooks/02-text-to-character/python
    python3 -m venv .venv && source .venv/bin/activate
    cp .env.example .env          # paste your key
    pip install -r requirements.txt
    python main.py

**TypeScript**

    cd cookbooks/02-text-to-character/typescript
    cp .env.example .env          # paste your key
    npm install
    npm start

You get `output/character.glb`, the generated concept image at `output/character-concept.png`, and a 512 px preview at `output/character-thumbnail.png`. Open the GLB in Blender with File > Import > glTF 2.0.

## How it works

1. **Generate the concept image from the prompt.** `client.create` POSTs the prompt to `/openapi/v1/text-to-image` with GPT Image 2.5 Sunburst, `remove_background` and `pose_mode` set, and returns the task id.

```python
    client = Meshy()  # reads MESHY_API_KEY from .env
    concept_id = client.create(
        "text-to-image",
        {
            "ai_model": "gpt-image-2-5-sunburst",
            "prompt": PROMPT,
            "remove_background": True,
            "pose_mode": "t-pose",
        },
    )
```

   `pose_mode` adds the T-pose preset for you, so `PROMPT` only has to describe who Wren is, and `remove_background` returns her as a transparent PNG cut-out.

2. **Wait for the image and save it.** `client.wait` GETs `/openapi/v1/text-to-image/:id` every 5 seconds, printing each status change under the `concept` label, and `client.download` saves the one entry in `image_urls`.

```python
    concept = client.wait("text-to-image", concept_id, "concept")
    client.download(concept["image_urls"][0], OUTPUT / "character-concept.png")
```

   This stage took 36 to 42 seconds in the four runs behind this README. Leave `generate_multi_view` off here: `image-to-3d` only accepts `input_task_id` from a task that produced one image, and the three-view route needs `multi-image-to-3d`, which cookbook 03 uses.

3. **Chain the image into an Ultra, 4K image-to-3d task.** `client.create` POSTs to `/openapi/v1/image-to-3d` with `input_task_id` pointing at the text-to-image task, so the image never leaves Meshy.

```python
    task_id = client.create(
        "image-to-3d",
        {
            "input_task_id": concept_id,
            "ultra_mode": True,
            "should_texture": True,
            "enable_pbr": True,
            "texture_resolution": "4k",
            "pose_mode": "t-pose",
            "target_formats": ["glb"],
        },
    )
```

   `ultra_mode` adds 5 credits for higher-fidelity geometry and `texture_resolution: "4k"` costs the same as the 2K default; both need Meshy 7, which is what `latest` resolves to today.

4. **Wait again, then download the GLB and the thumbnail.** `client.wait` polls `/openapi/v1/image-to-3d/:id` the same way under the `model` label, `client.download` streams `model_urls.glb` and `thumbnail_url` to disk, and the script prints the path and the credits of both tasks.

```python
    task = client.wait("image-to-3d", task_id, "model")
    glb = client.download(task["model_urls"]["glb"], OUTPUT / "character.glb")
    client.download(task["thumbnail_url"], OUTPUT / "character-thumbnail.png")
    credits = concept["consumed_credits"] + task["consumed_credits"]
    print(f"Done: {glb}  ({credits} credits)")
```

   Generation took between 5 min 37 s and 8 min 10 s across the four runs, so most of the wait is here. The mesh comes back dense: 0.82 to 1.77 million triangles and 43 to 70 MB with the 4K maps, so plan on a decimation pass in Blender before you rig it.

## Parameters worth changing

| Parameter | We use | Why |
|---|---|---|
| [`ai_model`](https://docs.meshy.ai/en/api/text-to-image#create-a-text-to-image-task) (text-to-image) | `"gpt-image-2-5-sunburst"` | 9 credits per image. `"nano-banana"` costs 3 and is fine for a first look |
| [`prompt`](https://docs.meshy.ai/en/api/text-to-image#create-a-text-to-image-task) | `PROMPT` | Describe the character, not the pose or the background. The next two parameters handle those |
| [`remove_background`](https://docs.meshy.ai/en/api/text-to-image#create-a-text-to-image-task) | `true` | Returns a transparent PNG cropped to the character, so the 3D stage gets a clean cut-out |
| [`pose_mode`](https://docs.meshy.ai/en/api/text-to-image#create-a-text-to-image-task) (both tasks) | `"t-pose"` | Rigging tools expect a T or A pose. Use `"a-pose"` if your rig wants the arms lower |
| [`input_task_id`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | the text-to-image task id | Chains the two tasks inside Meshy. Swap in `image_url` with a data URI of your own PNG to skip the prompt stage, as cookbook 01 does |
| [`ultra_mode`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `true` | Higher-fidelity geometry with finer surface detail, for 5 extra credits. Only on Meshy 7 |
| [`should_texture`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `true` | You want a textured model, not a gray mesh. Set `false` for geometry only, which drops the task to 25 credits with Ultra |
| [`enable_pbr`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `true` | Adds metallic, roughness and normal maps that Blender wires into the Principled BSDF on import. Needs `should_texture: true` |
| [`texture_resolution`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `"4k"` | 4096 × 4096 maps instead of the 2048 default at the same credit cost. `"8k"` costs 5 more |
| [`target_formats`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `["glb"]` | Only generates what you asked for; faster task. Add `"fbx"` if your rigging tool wants it |

`ai_model` on the 3D task is left out on purpose, so it runs on `latest`, which resolves to Meshy 7 today.

## What you have now

`output/character.glb` is one mesh with one material and three JPEG textures: a 4096 × 4096 base color, a 4096 × 4096 normal map and a 2048 × 2048 metallic-roughness map, since `texture_resolution` applies to the base color and normal only. Wren stands 1.90 m tall in scene units with her arms out in a T, has 823,204 triangles, is 43.3 MB on disk, and cost 44 credits including the concept image. Cookbook 03, product photos to a 4K product model, is next in the series and picks up `multi-image-to-3d`.
