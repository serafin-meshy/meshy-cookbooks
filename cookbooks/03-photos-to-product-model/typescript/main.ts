// Turn three product photos into a life-size, 4K-textured GLB and USDZ.

import { Meshy } from "../../../shared/typescript/meshy.js";

const PHOTOS = [
  "../input/armchair-001/1-front.jpg",
  "../input/armchair-001/2-back.jpg",
  "../input/armchair-001/3-side.jpg",
];
const OUTPUT = "output";

const client = new Meshy(); // reads MESHY_API_KEY from .env
const taskId = await client.create("multi-image-to-3d", {
  image_urls: await Promise.all(PHOTOS.map((path) => Meshy.dataUri(path))),
  ultra_mode: true,
  should_texture: true,
  enable_pbr: true,
  texture_resolution: "4k",
  auto_size: true,
  origin_at: "bottom",
  multi_view_thumbnails: true,
  target_formats: ["glb", "usdz"],
});
const task = await client.wait("multi-image-to-3d", taskId);
const glb = await client.download(task.model_urls.glb, `${OUTPUT}/armchair.glb`);
await client.download(task.model_urls.usdz!, `${OUTPUT}/armchair.usdz`);
for (const [view, url] of Object.entries(task.thumbnail_urls!)) {
  await client.download(url, `${OUTPUT}/armchair-${view}.png`);
}
console.log(`Done: ${glb}  (${task.consumed_credits} credits)`);
