// Turn character concept art into a textured GLB.

import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { Run, argumentsFor } from "../../../shared/typescript/run.js";
import { Meshy } from "../../../shared/typescript/meshy.js";

const DIRECTORY = dirname(fileURLToPath(import.meta.url));
const INPUT = join(DIRECTORY, "../input/concept-art.png");

const args = await argumentsFor(DIRECTORY, "Turn character concept art into a textured GLB.", { images: [INPUT] });
const run = new Run("01-image-to-3d-character", args, DIRECTORY, 30);
await run.execute(async (run) => {
  const task = await run.task("model", "image-to-3d", {
    image_url: await Meshy.dataUri(args.input[0]),
    should_texture: true,
    enable_pbr: true,
    target_formats: ["glb"],
  });
  await run.download(task.model_urls.glb, `character.glb`);
  await run.download(task.thumbnail_url, `character-thumbnail.png`);
});
