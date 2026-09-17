// Turn a text prompt into an Ultra, 4K-textured hero prop GLB.

import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { Run, argumentsFor } from "../../../shared/typescript/run.js";

const DIRECTORY = dirname(fileURLToPath(import.meta.url));
const PROMPT =
  "Marrow's sea chest, a closed pirate treasure chest: weathered oak planks, " +
  "black iron straps and rivets, a heavy brass padlock, barnacles along the base. " +
  "Stylized hand-painted game prop, three-quarter view.";

const args = await argumentsFor(DIRECTORY, "Turn a text prompt into an Ultra, 4K-textured hero prop GLB.", { prompt: PROMPT });
const run = new Run("02-text-to-hero-prop", args, DIRECTORY, 44);
await run.execute(async (run) => {
  const concept = await run.task("concept", "text-to-image", {
    ai_model: "gpt-image-2-5-sunburst",
    prompt: args.prompt,
    remove_background: true,
  });
  await run.download(concept.image_urls[0], `hero-prop-concept.png`);

  const task = await run.task("model", "image-to-3d", {
    input_task_id: concept.id,
    ultra_mode: true,
    should_texture: true,
    enable_pbr: true,
    texture_resolution: "4k",
    target_formats: ["glb"],
  });
  await run.download(task.model_urls.glb, `hero-prop.glb`);
  await run.download(task.thumbnail_url, `hero-prop-thumbnail.png`);
});
