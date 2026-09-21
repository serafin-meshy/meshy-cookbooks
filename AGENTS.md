# Using the Meshy cookbooks

Pick the recipe that matches the user's input and outcome, then read its README, the
selected language's `main` file, and the shared client it imports.

| Input / outcome | Recipe |
|---|---|
| One image → character or prop GLB | `examples/01-image-to-3d-character` |
| One concept image → low-poly GLB at a chosen face count | `examples/02-image-to-low-poly-prop` |
| Description → concept image → textured prop GLB | `examples/03-text-to-hero-prop` |
| One to four product photos, front first → GLB and USDZ | `examples/04-photos-to-product-model` |

- A live run spends Meshy credits; each README states the amount. Tell the user the cost
  and wait for their approval before running, unless they already gave it.
- Use the language the user names or their project already uses. Otherwise use Python.
  Both versions send the same payloads.
- Read `MESHY_API_KEY` from the environment or a local `.env`. Never write it into code or
  ask for it in chat, and keep API calls on the server in browser apps.
- Custom inputs are positional arguments: an image path, a description, or photo paths;
  cookbook 02 also takes a face count after the image. Leave the sample defaults in the code.
- To adapt a recipe into a project, copy `shared/<language>/meshy.*` next to the pipeline
  and keep the payloads literal.
