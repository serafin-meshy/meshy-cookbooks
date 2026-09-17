// Turn a text prompt into a T-posed, 4K-textured character GLB.

import { Meshy } from "../../../shared/typescript/meshy.js";

const PROMPT =
  "Wren, a young forest ranger: short auburn hair, green hooded cloak, " +
  "leather bracers, brown boots, a small satchel on the hip. " +
  "Full body, stylized hand-painted game character, no weapon.";
const OUTPUT = "output";

const client = new Meshy(); // reads MESHY_API_KEY from .env
const conceptId = await client.create("text-to-image", {
  ai_model: "gpt-image-2-5-sunburst",
  prompt: PROMPT,
  remove_background: true,
  pose_mode: "t-pose",
});
const concept = await client.wait("text-to-image", conceptId, "concept");
await client.download(concept.image_urls[0], `${OUTPUT}/character-concept.png`);

const taskId = await client.create("image-to-3d", {
  input_task_id: conceptId,
  ultra_mode: true,
  should_texture: true,
  enable_pbr: true,
  texture_resolution: "4k",
  pose_mode: "t-pose",
  target_formats: ["glb"],
});
const task = await client.wait("image-to-3d", taskId, "model");
const glb = await client.download(task.model_urls.glb, `${OUTPUT}/character.glb`);
await client.download(task.thumbnail_url, `${OUTPUT}/character-thumbnail.png`);
const credits = concept.consumed_credits + task.consumed_credits;
console.log(`Done: ${glb}  (${credits} credits)`);
