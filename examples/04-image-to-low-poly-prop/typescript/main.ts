// Turn a low-poly concept image into a low-poly GLB in seconds.

import { join } from "node:path";
import { Meshy } from "../../../shared/typescript/meshy.js";

const DIRECTORY = import.meta.dirname;
const SAMPLE = join(DIRECTORY, "../input/low-poly-oak.png");
const INPUT = process.argv[2] ?? SAMPLE;
const POLYCOUNT = process.argv[3] ? Number(process.argv[3]) : 1000;
const OUTPUT = join(DIRECTORY, "output");

const client = new Meshy(); // reads MESHY_API_KEY from .env
const taskId = await client.create("image-to-3d", {
  image_url: await Meshy.dataUri(INPUT),
  model_type: "smart-topology",
  target_polycount: POLYCOUNT,
  should_texture: false,
  target_formats: ["glb"],
});
const task = await client.wait("image-to-3d", taskId);
await client.download(task.model_urls.glb, join(OUTPUT, "low-poly-prop.glb"));
await client.download(task.thumbnail_url, join(OUTPUT, "low-poly-prop-thumbnail.png"));
console.log(`Done: ${join(OUTPUT, "low-poly-prop.glb")}  (${task.consumed_credits} credits)`);
