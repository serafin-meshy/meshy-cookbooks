# Concept image to low-poly game prop

Turn one concept image into a low-poly GLB in under 10 seconds.

**Endpoints:** `POST /openapi/v1/image-to-3d` → `GET /openapi/v1/image-to-3d/:id`  
**Credits:** ~5 per run  
**Time:** under 10 seconds  
**Languages:** Python 3.10+ · TypeScript (Node 22+)

Smart Topology is a separate generation model, `meshy-t2`, that builds the mesh at the face count you ask for instead of sculpting a dense one and decimating it. That makes it the right tool when you need many small props for a stylized low-poly world and care more about the triangle budget and the turnaround than about surface detail. This recipe sends one image, gets back an untextured GLB of about 1,100 triangles, and lets you change the face count from the command line; cookbook 01 uses the same endpoint without Smart Topology when you want the dense, textured version instead.

## Run it

Live runs need a Meshy plan with API access (Pro, Premium, Ultra, Studio, or Enterprise) and about 5 credits. Create an API key at https://www.meshy.ai/developers/ and check your credit balance at https://www.meshy.ai/settings/subscription. Current rates are at https://docs.meshy.ai/en/api/pricing. Then:

**Python**

    cd examples/02-image-to-low-poly-prop/python
    python3 -m venv .venv && source .venv/bin/activate
    cp .env.example .env          # paste your key
    pip install -r requirements.txt
    python main.py

**TypeScript**

    cd examples/02-image-to-low-poly-prop/typescript
    cp .env.example .env          # paste your key
    npm install
    npm start

You get `output/low-poly-prop.glb` and a 512 px preview at `output/low-poly-prop-thumbnail.png`. Open the GLB in Blender with File > Import > glTF 2.0, then press Z and choose Wireframe to see the triangles.

To use your own image, or a different face count, pass them in that order:

    python main.py my-sketch.png 300
    npm start -- my-sketch.png 300

The face count can be anything from 100 to 15,000. Each run overwrites the files in `output/`. Stopping a run does not cancel the task: the script prints the task ID first, and `client.get` with that ID returns the finished task for up to three days.

## Use with a coding agent

1. Clone the repository and open the folder in your coding agent:

       git clone https://github.com/serafin-meshy/meshy-cookbooks.git
       cd meshy-cookbooks

2. Paste this prompt as written. It names this cookbook and its included example, so there is nothing to fill in:

   > Read `AGENTS.md` and `examples/02-image-to-low-poly-prop/README.md`, then run the
   > included oak tree example with the default image and face count.
   > Tell me the expected Meshy credit cost and wait for my approval before generating.

3. The agent installs dependencies and tells you the expected credit cost. Once you approve, it runs the generation and reports the output files.

**Use your own asset:** Point the agent at your own image and, if you want, a face count, and ask it to pass those instead.

**Integrate into a project:** Also provide your project path and describe how the
feature should work. The agent will adapt the matching Python or TypeScript implementation.

## How it works

1. **Create a Smart Topology task from the image.** `client.create` encodes the PNG as a data URI, POSTs it to `/openapi/v1/image-to-3d` with `model_type` set to `smart-topology` and the face count you asked for, prints the new task ID, and returns it.

```python
task_id = client.create(
    "image-to-3d",
    {
        "image_url": Meshy.data_uri(INPUT),
        "model_type": "smart-topology",
        "target_polycount": POLYCOUNT,
        "should_texture": False,
        "target_formats": ["glb"],
    },
)
```

   The mesh is generated directly at the target face count instead of being sculpted dense and decimated afterwards, which is where the speed comes from. The count is approximate: on the oak a target of 1,000 gave 1,096 to 1,104 triangles, 100 gave 98, and 15,000 gave 15,540.

2. **Wait for it.** `client.wait` GETs `/openapi/v1/image-to-3d/:id` every 5 seconds and prints each status change, so you will see one `IN_PROGRESS` line before `SUCCEEDED`.

```python
task = client.wait("image-to-3d", task_id)
```

   Generation takes 2.5 to 3.1 seconds on the oak, and the wall time from `python main.py` to the file on disk is 7 to 8 seconds, most of it waiting for the next poll. Generation time depends on server load rather than on the image: an identical request took up to 11 seconds at another point on the day these numbers were measured. The task object does not report which model ran; `consumed_credits` of 5 (rather than 20 for a standard untextured task) is your confirmation that Smart Topology did.

3. **Download the GLB and the preview.** `client.download` streams `model_urls.glb` and `thumbnail_url` to disk and the script prints the path and the credits.

```python
client.download(task["model_urls"]["glb"], OUTPUT / "low-poly-prop.glb")
client.download(task["thumbnail_url"], OUTPUT / "low-poly-prop-thumbnail.png")
print(f"Done: {OUTPUT / 'low-poly-prop.glb'}  ({task['consumed_credits']} credits)")
```

   The untextured GLB is about 20 KB and contains vertex positions and triangle indices only: no normals, no UVs, no material. Blender and game engines compute flat normals on import, so it renders as a gray, faceted mesh, and if you want a texture later you regenerate with `should_texture` set to `true` rather than unwrapping it yourself. The "natively separated parts" that Smart Topology advertises are loose pieces inside one mesh, not named objects: the oak comes back as four of them, the trunk and the three canopy clumps, and in Blender, Edit Mode > Mesh > Separate > By Loose Parts turns them into four objects.

## Parameters worth changing

| Parameter | We use | Why |
|---|---|---|
| [`model_type`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `"smart-topology"` | Selects the Smart Topology model, `meshy-t2`, at 5 credits untextured. Leave it out for the standard model, which cookbook 01 uses: denser, 30 credits with texture, minutes instead of seconds. `"lowpoly"` is the deprecated predecessor |
| [`target_polycount`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `POLYCOUNT` (default `1000`) | Face count for the generated mesh, 100 to 15,000 (default 4,000). On the oak, 100 gives 98 triangles and still reads as a tree, 300 gives 324, 1,000 keeps the faceted canopy of the concept, and 15,000 gives 15,540 in a 281 KB file with the canopy broken into leaf clusters. Below 100 the API returns `400 TargetPolycount must be 100 or greater`; above 15,000 it returns `400 target_polycount must be between 100 and 15000 for meshy-t2` |
| [`should_texture`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `false` | Geometry only, for the 5 credits and the seconds. `true` costs 15 credits, took 47 to 50 seconds on the oak, and returns a 3.6 to 3.8 MB GLB with normals, UVs and three 2048 × 2048 JPEG maps (base color, metallic-roughness, normal); add `"enable_pbr": true` at the same time for the metallic-roughness and normal maps, since the API rejects `enable_pbr` without `should_texture` |
| [`target_formats`](https://docs.meshy.ai/en/api/image-to-3d#create-an-image-to-3d-task) | `["glb"]` | Only generates what you asked for; faster task. Add `"fbx"` for Unity or Unreal |

`topology`, `should_remesh` and `geometry_resolution` are not in the table because Smart Topology ignores the first two (its output is always triangles; asking for `"quad"` returns a `400`) and the third applies to the standard model only. `ai_model` is left out on purpose, so the task runs on `meshy-t2`, the only Smart Topology model the API documented when this README was measured (September 21, 2026; the default can change).

## What you have now

`output/low-poly-prop.glb` is one mesh of 1,096 triangles and 556 vertices, 20.5 KB on disk, made from the oak concept for 5 credits in 7 seconds. Meshy normalizes it to 1.00 m along its longest side, so scale it in Blender or your engine before it goes into a scene. Cookbook 01, concept art to game character, is the same endpoint without `model_type` and shows what the dense standard pass gives you for the same kind of input. Cookbook 03, text prompt to hero prop, is next in the series; it starts from a sentence instead of an image and adds `geometry_resolution` for the Ultra geometry pass.
