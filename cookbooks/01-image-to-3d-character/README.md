# Concept art to game character

Turn one piece of character concept art into a textured GLB in 5 to 9 minutes.

**Endpoints:** `POST /openapi/v1/image-to-3d` → `GET /openapi/v1/image-to-3d/:id`  
**Credits:** ~30 per run  
**Time:** ~5 to 9 minutes  
**Languages:** Python 3.10+ · TypeScript (Node 22+)

## Who this is for

Indie developers who have concept art for a character and want a textured GLB without modeling it by hand. You bring one PNG and get back a mesh with base color, metallic, roughness and normal maps; the same call works on a prop sketch.

## Run it

Get an API key at https://www.meshy.ai/settings/api. The API is pay-before-you-go: this recipe spends about 30 credits per run, and API usage is bought at https://www.meshy.ai/settings/subscription. Then:

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

## How it works

1. **Encode the art and create the task.** `Meshy.data_uri` reads `input/concept-art.png` into a base64 data URI, and `client.create` POSTs the payload to `/openapi/v1/image-to-3d` and returns the task id.

```python
    client = Meshy()  # reads MESHY_API_KEY from .env
    task_id = client.create(
        "image-to-3d",
        {
            "image_url": Meshy.data_uri(INPUT),
            "should_texture": True,
            "enable_pbr": True,
            "target_formats": ["glb"],
        },
    )
```

   A data URI means you never have to host the image anywhere. The sample is the armored character from the Meshy quick start guide; swap in your own PNG or JPG at the same path.

2. **Poll until the task finishes.** `client.wait` GETs `/openapi/v1/image-to-3d/:id` every 5 seconds, prints each status change, and returns the task object once the status is `SUCCEEDED`.

```python
    task = client.wait("image-to-3d", task_id)
```

   On `FAILED` or `CANCELED` it raises with `task_error.message` and the script exits non-zero, and Meshy refunds the credits of a `FAILED` task. The three runs behind this README took between 4 min 44 s and 9 min 16 s end to end, almost all of it generation rather than queue time, so expect to wait.

3. **Download the GLB and the thumbnail.** `client.download` streams the signed `model_urls.glb` URL to `output/character.glb` and `thumbnail_url` to `output/character-thumbnail.png`, then the script prints the path and `consumed_credits`.

```python
    glb = client.download(task["model_urls"]["glb"], OUTPUT / "character.glb")
    client.download(task["thumbnail_url"], OUTPUT / "character-thumbnail.png")
    print(f"Done: {glb}  ({task['consumed_credits']} credits)")
```

   The mesh comes back dense: 731,336 to 898,428 triangles and 27.4 to 32.2 MB across the three runs behind this README, far heavier than a game-ready asset, so plan on a decimation pass in Blender before it goes into a scene.

## Parameters worth changing

| Parameter | We use | Why |
|---|---|---|
| [`image_url`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | data URI of `input/concept-art.png` | Works from a local file with no hosting step. A public URL works too |
| [`should_texture`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `true` | You want a textured model, not a gray mesh. Set `false` for geometry only |
| [`enable_pbr`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `true` | Adds metallic, roughness and normal maps that Blender wires into the Principled BSDF on import. Needs `should_texture: true` |
| [`target_formats`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `["glb"]` | Only generates what you asked for; faster task. Blender imports GLB natively. Add `"fbx"` or `"obj"` for other tools |

`ai_model` is left out on purpose, so the task runs on `latest`, which resolves to Meshy 7 today.

## What you have now

`output/character.glb` is one mesh with one material and three 2048 × 2048 JPEG textures: base color, metallic-roughness and normal. It stands 1.90 m tall in scene units, has 813,722 triangles, is 29.7 MB on disk, and cost 30 credits. Cookbook 02, text prompt to T-posed character, is next in the series and starts from a sentence instead of art.
