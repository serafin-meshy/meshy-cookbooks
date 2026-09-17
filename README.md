# Meshy Cookbooks

Short, runnable recipes for the [Meshy API](https://docs.meshy.ai). Each one takes you from an API key to a model file you can use, in one command, in Python or TypeScript.

| Cookbook | What you get | Difficulty |
|---|---|---|
| [01 · Concept art to game character](cookbooks/01-image-to-3d-character/) | A textured, PBR character GLB from one piece of concept art, ready for Blender | Beginner |
| [02 · Text prompt to T-posed character](cookbooks/02-text-to-character/) | A T-posed character GLB from one sentence, with Ultra geometry, 4K PBR textures and the concept image | Intermediate |
| [03 · Product photos to a 4K product model](cookbooks/03-photos-to-product-model/) | A life-size, Ultra-mode GLB and USDZ with 4K PBR textures from three product photos, plus four renders | Intermediate |

## How the repo is laid out

- `cookbooks/NN-name/` holds one recipe with a README, a sample `input/` when the recipe starts from a file, and both a `python/` and a `typescript/` entry point that do the same thing.
- `shared/python/meshy.py` and `shared/typescript/meshy.ts` are the small client every recipe imports. Copy the one for your language into your own project.

## Run one

Get an API key at https://www.meshy.ai/settings/api and buy API usage at https://www.meshy.ai/settings/subscription: the API is pay-before-you-go and one run costs 30 to 44 credits. Then open the cookbook's README and follow "Run it".

## License

MIT. See [LICENSE](LICENSE).
