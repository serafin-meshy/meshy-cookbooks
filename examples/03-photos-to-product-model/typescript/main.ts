// Turn three product photos into a life-size, 4K-textured GLB and USDZ.

import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { Run, argumentsFor } from "../../../shared/typescript/run.js";
import { Meshy } from "../../../shared/typescript/meshy.js";

const DIRECTORY = dirname(fileURLToPath(import.meta.url));
const PHOTOS = [
  join(DIRECTORY, "../input/armchair-001/1-front.jpg"),
  join(DIRECTORY, "../input/armchair-001/2-back.jpg"),
  join(DIRECTORY, "../input/armchair-001/3-side.jpg"),
];

const args = await argumentsFor(DIRECTORY, "Turn three product photos into a life-size, 4K-textured GLB and USDZ.", { images: PHOTOS });
const run = new Run("03-photos-to-product-model", args, DIRECTORY, 35);
await run.execute(async (run) => {
  const task = await run.task("model", "multi-image-to-3d", {
    image_urls: await Promise.all(args.input.map((path) => Meshy.dataUri(path))),
    ultra_mode: true,
    should_texture: true,
    enable_pbr: true,
    texture_resolution: "4k",
    auto_size: true,
    origin_at: "bottom",
    multi_view_thumbnails: true,
    target_formats: ["glb", "usdz"],
  });
  await run.download(task.model_urls.glb, `armchair.glb`);
  await run.download(task.model_urls.usdz!, `armchair.usdz`);
  for (const [view, url] of Object.entries(task.thumbnail_urls!)) {
    await run.download(url, `armchair-${view}.png`);
  }
});
