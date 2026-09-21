"""Turn three product photos into a life-size, 4K-textured GLB and USDZ."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # so `shared` imports
from shared.python.meshy import Meshy

DIRECTORY = Path(__file__).resolve().parent
SAMPLE = [
    DIRECTORY.parent / "input/armchair-001/1-front.jpg",
    DIRECTORY.parent / "input/armchair-001/2-back.jpg",
    DIRECTORY.parent / "input/armchair-001/3-side.jpg",
]
PHOTOS = [Path(p) for p in sys.argv[1:]] or SAMPLE  # front view first
OUTPUT = DIRECTORY / "output"

client = Meshy()  # reads MESHY_API_KEY from .env
task_id = client.create(
    "multi-image-to-3d",
    {
        "image_urls": [Meshy.data_uri(p) for p in PHOTOS],
        "geometry_resolution": "2k",
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
client.download(task["model_urls"]["glb"], OUTPUT / "armchair.glb")
client.download(task["model_urls"]["usdz"], OUTPUT / "armchair.usdz")
for view, url in task["thumbnail_urls"].items():
    client.download(url, OUTPUT / f"armchair-{view}.png")
print(f"Done: {OUTPUT / 'armchair.glb'}  ({task['consumed_credits']} credits)")
