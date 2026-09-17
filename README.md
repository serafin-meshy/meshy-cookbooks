![Meshy Cookbooks](./cookbooks-header.png)

Short, runnable recipes for the [Meshy API](https://docs.meshy.ai). Each one takes you from an API key to a model file you can use, in one command, in Python or TypeScript.

| Cookbook | What you get |
|---|---|
| [01 · Concept art to game character](cookbooks/01-image-to-3d-character/) | A textured, PBR character GLB from one piece of concept art, ready for Blender |
| [02 · Text prompt to hero prop](cookbooks/02-text-to-hero-prop/) | A hero prop GLB from one sentence, with Ultra geometry, 4K PBR textures and the concept image |
| [03 · Product photos to a 4K product model](cookbooks/03-photos-to-product-model/) | A life-size, Ultra-mode GLB and USDZ with 4K PBR textures from three product photos, plus four renders |

## Use with your coding agent

1. Clone this repository and open it in your coding agent.
2. Paste the prompt below, replacing the bracketed text with your asset description.
   For an image-based request, include the local image paths.
3. The agent will choose a cookbook, check the setup, and explain the cost before generation.

> Read AGENTS.md and follow the matching cookbook’s PROMPT.md. I want to
> **[describe your asset]**. Set up the cookbook for my request and run its offline
> checks. Before generating anything, explain the expected Meshy credit cost and
> wait for my approval.

**Already know which cookbook you want?** Use its ready-to-paste example prompt instead:

- [Included character concept art → character GLB](cookbooks/01-image-to-3d-character/README.md#use-with-a-coding-agent)
- [Marrow’s sea chest description → hero prop GLB](cookbooks/02-text-to-hero-prop/README.md#use-with-a-coding-agent)
- [Included armchair photos → GLB and USDZ](cookbooks/03-photos-to-product-model/README.md#use-with-a-coding-agent)

## How the repo is laid out

- `cookbooks/NN-name/` holds one recipe with a README, a sample `input/` when the recipe starts from a file, and both a `python/` and a `typescript/` entry point that do the same thing.
- `shared/python/meshy.py` and `shared/typescript/meshy.ts` are the small API clients. The adjacent `run.py` / `run.ts` handle CLI options, checkpoints, and result files. Copy both for your language to keep that behavior.

## Run one

Live API runs require a Meshy plan with API access: Pro, Premium, Ultra, Studio, or Enterprise. Create an [API key](https://www.meshy.ai/settings/api), then check your plan and credit balance in [subscription settings](https://www.meshy.ai/settings/subscription). These cookbooks consumed approximately 30–44 credits per complete run in our recorded examples; consult [current API pricing](https://docs.meshy.ai/en/api/pricing) before running.

Open the cookbook’s README and follow “Run it.” After installing dependencies, start with `python main.py --dry-run` or `npm run dry-run` to validate inputs without an API key or paid requests.

## License

MIT. See [LICENSE](LICENSE).

