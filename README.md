![Meshy Cookbooks](./cookbooks-header.png)

Short, runnable recipes for the [Meshy API](https://docs.meshy.ai). Each one takes you from an API key to a model file you can use, in one command, in Python or TypeScript.

Follow cookbooks 01 → 02 → 03 → 04 in sequence to learn the core workflow and then explore its variations. Or jump to the project that matches your needs.

| Cookbook | What you get |
|---|---|
| [01 · Concept art to game character](examples/01-image-to-3d-character/) | A textured, PBR character GLB from one piece of concept art, ready for Blender |
| [02 · Concept image to low-poly game prop](examples/02-image-to-low-poly-prop/) | A low-poly GLB at a face count you choose, from one concept image, in seconds |
| [03 · Text prompt to hero prop](examples/03-text-to-hero-prop/) | A hero prop GLB from one sentence, with Ultra 4K geometry, 4K PBR textures and the concept image |
| [04 · Product photos to a 4K product model](examples/04-photos-to-product-model/) | A life-size GLB and USDZ with Ultra 2K geometry and 4K PBR textures from three product photos, plus four renders |

## How the repo is laid out

- `examples/NN-name/` holds one recipe with a README, a sample `input/` when the recipe starts from a file, and both a `python/` and a `typescript/` entry point that do the same thing.
- `shared/python/meshy.py` and `shared/typescript/meshy.ts` are the small API clients: create a task, poll it, download the result. Copy the one for your language into your own project.

## Run one

Live API runs require a Meshy plan with API access: Pro, Premium, Ultra, Studio, or Enterprise. Create an [API key](https://www.meshy.ai/developers/), then check your plan and credit balance in [subscription settings](https://www.meshy.ai/settings/subscription). These cookbooks consumed approximately 5–44 credits per complete run in our recorded examples; consult [current API pricing](https://docs.meshy.ai/en/api/pricing) before running.

Open the cookbook’s README and follow “Run it.”

## License

MIT. See [LICENSE](LICENSE).
