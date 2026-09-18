// Turn character concept art into a textured GLB.

import { join } from "node:path";
import { Meshy } from "../../../shared/typescript/meshy.js";

const DIRECTORY = import.meta.dirname;
const SAMPLE = join(DIRECTORY, "../input/concept-art.png");
const INPUT = process.argv[2] ?? SAMPLE;
const OUTPUT = join(DIRECTORY, "output");

const client = new Meshy(); // reads MESHY_API_KEY from .env
const taskId = await client.create("image-to-3d", {
  image_url: await Meshy.dataUri(INPUT),
  should_texture: true,
  enable_pbr: true,
  target_formats: ["glb"],
});
const task = await client.wait("image-to-3d", taskId);
await client.download(task.model_urls.glb, join(OUTPUT, "character.glb"));
await client.download(task.thumbnail_url, join(OUTPUT, "character-thumbnail.png"));
console.log(`Done: ${join(OUTPUT, "character.glb")}  (${task.consumed_credits} credits)`);
