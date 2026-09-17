"""Turn three product photos into a life-size, 4K-textured GLB and USDZ."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # so `shared` imports
from shared.python.meshy import Meshy

PHOTOS = [
    Path("../input/armchair-001/1-front.jpg"),
    Path("../input/armchair-001/2-back.jpg"),
    Path("../input/armchair-001/3-side.jpg"),
]
OUTPUT = Path("output")


def main() -> None:
    client = Meshy()  # reads MESHY_API_KEY from .env
    task_id = client.create(
        "multi-image-to-3d",
        {
            "image_urls": [Meshy.data_uri(p) for p in PHOTOS],
            "ultra_mode": True,
            "should_texture": True,
            "enable_pbr": True,
            "texture_resolution": "4k",
            "auto_size": True,
            "origin_at": "bottom",
            "multi_view_thumbnails": True,
            "target_formats": ["glb", "usdz"],
        },
    )
    task = client.wait("multi-image-to-3d", task_id)
    glb = client.download(task["model_urls"]["glb"], OUTPUT / "armchair.glb")
    client.download(task["model_urls"]["usdz"], OUTPUT / "armchair.usdz")
    for view, url in task["thumbnail_urls"].items():
        client.download(url, OUTPUT / f"armchair-{view}.png")
    print(f"Done: {glb}  ({task['consumed_credits']} credits)")


if __name__ == "__main__":
    main()
