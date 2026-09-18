// Turn a text prompt into an Ultra, 4K-textured hero prop GLB.

import { join } from "node:path";
import { Meshy } from "../../../shared/typescript/meshy.js";

const DIRECTORY = import.meta.dirname;
const SAMPLE =
  "Marrow's sea chest, a closed pirate treasure chest: weathered oak planks, " +
  "black iron straps and rivets, a heavy brass padlock, barnacles along the base. " +
  "Stylized hand-painted game prop, three-quarter view.";
const PROMPT = process.argv.slice(2).join(" ") || SAMPLE;
const OUTPUT = join(DIRECTORY, "output");

const client = new Meshy(); // reads MESHY_API_KEY from .env
const conceptId = await client.create("text-to-image", {
  ai_model: "gpt-image-2-5-sunburst",
  prompt: PROMPT,
  remove_background: true,
});
const concept = await client.wait("text-to-image", conceptId);
await client.download(concept.image_urls[0], join(OUTPUT, "hero-prop-concept.png"));

const taskId = await client.create("image-to-3d", {
  input_task_id: conceptId,
  ultra_mode: true,
  should_texture: true,
  enable_pbr: true,
  texture_resolution: "4k",
  target_formats: ["glb"],
});
const task = await client.wait("image-to-3d", taskId);
await client.download(task.model_urls.glb, join(OUTPUT, "hero-prop.glb"));
await client.download(task.thumbnail_url, join(OUTPUT, "hero-prop-thumbnail.png"));
const credits = concept.consumed_credits + task.consumed_credits;
console.log(`Done: ${join(OUTPUT, "hero-prop.glb")}  (${credits} credits)`);
