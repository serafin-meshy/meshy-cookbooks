![Meshy Cookbooks](./cookbooks-header.png)

Short, runnable recipes for the [Meshy API](https://docs.meshy.ai). Each one takes you from an API key to a model file you can use, in one command, in Python or TypeScript.

| Cookbook | What you get | Difficulty |
|---|---|---|
| [01 · Concept art to game character](cookbooks/01-image-to-3d-character/) | A textured, PBR character GLB from one piece of concept art, ready for Blender | Beginner |
| [02 · Text prompt to hero prop](cookbooks/02-text-to-hero-prop/) | A hero prop GLB from one sentence, with Ultra geometry, 4K PBR textures and the concept image | Intermediate |
| [03 · Product photos to a 4K product model](cookbooks/03-photos-to-product-model/) | A life-size, Ultra-mode GLB and USDZ with 4K PBR textures from three product photos, plus four renders | Intermediate |

## Use with your coding agent

Paste this repository's URL into your coding agent with this prompt, or clone the repo and use it there:

> Read this repository's AGENTS.md and choose the cookbook that fits my request.
> Follow its PROMPT.md and adapt the matching Python or TypeScript implementation
> to my existing project. Preserve task checkpoints and resumable downloads.
> Run the offline checks first and explain the expected credit cost before a live run.
> I want to: **[describe your asset or integration here]**.

[Agent guide](AGENTS.md) · [Inputs, dry runs, resume, and results](RUNNING.md)

Each cookbook also has a focused prompt you can use directly:

- [One image → character or prop](cookbooks/01-image-to-3d-character/PROMPT.md)
- [Text → hero prop](cookbooks/02-text-to-hero-prop/PROMPT.md)
- [Product photos → model](cookbooks/03-photos-to-product-model/PROMPT.md)

## How the repo is laid out

- `cookbooks/NN-name/` holds one recipe with a README, a sample `input/` when the recipe starts from a file, and both a `python/` and a `typescript/` entry point that do the same thing.
- `shared/python/meshy.py` and `shared/typescript/meshy.ts` are the small API clients. The adjacent `run.py` / `run.ts` handle CLI options, checkpoints, and result files. Copy both for your language to keep that behavior.

## Run one

Live API runs require a Meshy plan with API access: Pro, Premium, Ultra, Studio, or Enterprise. Create an [API key](https://www.meshy.ai/settings/api), then check your plan and credit balance in [subscription settings](https://www.meshy.ai/settings/subscription). These cookbooks consumed approximately 30–44 credits per complete run in our recorded examples; consult [current API pricing](https://docs.meshy.ai/en/api/pricing) before running.

Open the cookbook’s README and follow “Run it.” After installing dependencies, start with `python main.py --dry-run` or `npm run dry-run` to validate inputs without an API key or paid requests.

## License

MIT. See [LICENSE](LICENSE).
