# Concept art to game character

Turn one piece of character concept art into a textured GLB in 2 to 3 minutes.

**Endpoints:** `POST /openapi/v1/image-to-3d` → `GET /openapi/v1/image-to-3d/:id`  
**Credits:** ~30 per run  
**Time:** ~2 to 3 minutes  
**Languages:** Python 3.10+ · TypeScript (Node 22+)

`image-to-3d` takes one picture and returns a textured mesh, and it runs as a single task, so the whole recipe is one request, one poll loop and one download. That makes it the right starting point when you already have concept art and want to see it as a model before deciding how far to take it. This recipe sends one PNG as a data URI with texturing and PBR maps turned on and downloads a dense GLB of around a million triangles; cookbook 02 uses the same endpoint with Smart Topology when you want a light, untextured low-poly mesh instead.

## Run it

Live runs need a Meshy plan with API access (Pro, Premium, Ultra, Studio, or Enterprise) and about 30 credits. Create an API key at https://www.meshy.ai/developers/ and check your credit balance at https://www.meshy.ai/settings/subscription. Current rates are at https://docs.meshy.ai/en/api/pricing. Then:

**Python**

    cd examples/01-image-to-3d-character/python
    python3 -m venv .venv && source .venv/bin/activate
    cp .env.example .env          # paste your key
    pip install -r requirements.txt
    python main.py

**TypeScript**

    cd examples/01-image-to-3d-character/typescript
    cp .env.example .env          # paste your key
    npm install
    npm start

You get `output/character.glb` and a 512 px preview at `output/character-thumbnail.png`. Open the GLB in Blender with File > Import > glTF 2.0.

To use your own art, pass the path to a PNG or JPEG:

    python main.py /path/to/character.png
    npm start -- /path/to/character.png

Each run overwrites the files in `output/`. Stopping a run does not cancel the task: the script prints the task ID first, and `client.get` with that ID returns the finished task for up to three days.

## Use with a coding agent

1. Clone the repository and open the folder in your coding agent:

       git clone https://github.com/serafin-meshy/meshy-cookbooks.git
       cd meshy-cookbooks

2. Paste this prompt as written. It names this cookbook and its included example, so there is nothing to fill in:

   > Read `AGENTS.md` and `examples/01-image-to-3d-character/README.md`, then run
   > the included armored-character example from `input/concept-art.png` with the
   > default settings. Tell me the expected Meshy credit cost and wait for my
   > approval before generating.

3. The agent installs dependencies and tells you the expected credit cost. Once you approve, it runs the generation and reports the output files.

**Use your own asset:** Give the agent the path to your own PNG or JPEG instead.

**Integrate into a project:** Also provide your project path and describe how the
feature should work. The agent will adapt the matching Python or TypeScript implementation.

## How it works

1. **Encode the art and create the task.** `Meshy.data_uri` reads `input/concept-art.png` into a base64 data URI, and `client.create` POSTs the payload to `/openapi/v1/image-to-3d`, prints the new task ID, and returns it.

```python
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

   A data URI means you never have to host the image anywhere. The sample is the armored character from the Meshy quick start guide; pass your own PNG or JPG as the first argument to use it instead.

2. **Poll until the task finishes.** `client.wait` GETs `/openapi/v1/image-to-3d/:id` every 5 seconds, prints each status change, and returns the task object once the status is `SUCCEEDED`.

```python
task = client.wait("image-to-3d", task_id)
```

   On `FAILED` or `CANCELED` it raises with `task_error.message` and the script exits non-zero, and Meshy refunds the credits of a `FAILED` task. A run takes between 1 min 34 s and 2 min 40 s end to end, almost all of it generation rather than queue time.

3. **Download the GLB and the thumbnail.** `client.download` streams the signed `model_urls.glb` URL to `output/character.glb` and `thumbnail_url` to `output/character-thumbnail.png`, then the script prints the path and the credits the task reported.

```python
client.download(task["model_urls"]["glb"], OUTPUT / "character.glb")
client.download(task["thumbnail_url"], OUTPUT / "character-thumbnail.png")
```

   The mesh comes back dense: 765,812 to 1,028,430 triangles and 28.0 to 35.9 MB, far heavier than a game-ready asset, so plan on a decimation pass in Blender before it goes into a scene.

## Parameters worth changing

| Parameter | We use | Why |
|---|---|---|
| [`image_url`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | data URI of `input/concept-art.png` | Works from a local file with no hosting step. A public URL works too |
| [`should_texture`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `true` | You want a textured model, not a gray mesh. Set `false` for geometry only |
| [`enable_pbr`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `true` | Adds metallic, roughness and normal maps that Blender wires into the Principled BSDF on import. Needs `should_texture: true` |
| [`target_formats`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `["glb"]` | Only generates what you asked for; faster task. Blender imports GLB natively. Add `"fbx"` or `"obj"` for other tools |

`ai_model` is left out on purpose, so the task runs on `latest`, which has been Meshy 7.1 since September 18, 2026 and was used for the measurements recorded in this README (documented September 21, 2026; the default can change).

## What you have now

`output/character.glb` is one mesh with one material and three 2048 × 2048 JPEG textures: base color, metallic-roughness and normal. It stands 1.90 m tall in scene units, has 1,003,852 triangles, is 35.2 MB on disk, and cost 30 credits. Cookbook 02, concept image to low-poly game prop, is next in the series; it sends the same kind of image to the same endpoint with Smart Topology and gets back an untextured mesh of about a thousand triangles in seconds.
