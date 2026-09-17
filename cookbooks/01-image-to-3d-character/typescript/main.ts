// Turn character concept art into a textured GLB.

import { Meshy } from "../../../shared/typescript/meshy.js";

const INPUT = "../input/concept-art.png";
const OUTPUT = "output";

const client = new Meshy(); // reads MESHY_API_KEY from .env
const taskId = await client.create("image-to-3d", {
  image_url: await Meshy.dataUri(INPUT),
  should_texture: true,
  enable_pbr: true,
  target_formats: ["glb"],
});
const task = await client.wait("image-to-3d", taskId);
const glb = await client.download(task.model_urls.glb, `${OUTPUT}/character.glb`);
await client.download(task.thumbnail_url, `${OUTPUT}/character-thumbnail.png`);
console.log(`Done: ${glb}  (${task.consumed_credits} credits)`);
