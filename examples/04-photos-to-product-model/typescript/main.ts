// Turn three product photos into a life-size, 4K-textured GLB and USDZ.

import { join } from "node:path";
import { Meshy } from "../../../shared/typescript/meshy.js";

const DIRECTORY = import.meta.dirname;
const SAMPLE = [
  join(DIRECTORY, "../input/armchair-001/1-front.jpg"),
  join(DIRECTORY, "../input/armchair-001/2-back.jpg"),
  join(DIRECTORY, "../input/armchair-001/3-side.jpg"),
];
const PHOTOS = process.argv.length > 2 ? process.argv.slice(2) : SAMPLE; // front view first
const OUTPUT = join(DIRECTORY, "output");

const client = new Meshy(); // reads MESHY_API_KEY from .env
const taskId = await client.create("multi-image-to-3d", {
  image_urls: await Promise.all(PHOTOS.map((path) => Meshy.dataUri(path))),
  geometry_resolution: "2k",
  should_texture: true,
  enable_pbr: true,
  texture_resolution: "4k",
  auto_size: true,
  origin_at: "bottom",
  multi_view_thumbnails: true,
  target_formats: ["glb", "usdz"],
});
const task = await client.wait("multi-image-to-3d", taskId);
await client.download(task.model_urls.glb, join(OUTPUT, "armchair.glb"));
await client.download(task.model_urls.usdz!, join(OUTPUT, "armchair.usdz"));
for (const [view, url] of Object.entries(task.thumbnail_urls!)) {
  await client.download(url, join(OUTPUT, `armchair-${view}.png`));
}
console.log(`Done: ${join(OUTPUT, "armchair.glb")}  (${task.consumed_credits} credits)`);
