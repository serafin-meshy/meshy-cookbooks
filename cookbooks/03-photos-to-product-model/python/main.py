"""Turn three product photos into a life-size, 4K-textured GLB and USDZ."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # so `shared` imports
from shared.python.meshy import Meshy
from shared.python.run import Run, arguments

DIRECTORY = Path(__file__).resolve().parent
PHOTOS = [
    DIRECTORY.parent / "input/armchair-001/1-front.jpg",
    DIRECTORY.parent / "input/armchair-001/2-back.jpg",
    DIRECTORY.parent / "input/armchair-001/3-side.jpg",
]


def main() -> None:
    args = arguments(
        DIRECTORY,
        "Turn three product photos into a life-size, 4K-textured GLB and USDZ.",
        images=PHOTOS,
    )
    run = Run("03-photos-to-product-model", args, DIRECTORY, 35)

    def pipeline(run):
        task = run.task(
            "model",
            "multi-image-to-3d",
            {
                "image_urls": [Meshy.data_uri(p) for p in args.input],
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
        run.download(task["model_urls"]["glb"], "armchair.glb")
        run.download(task["model_urls"]["usdz"], "armchair.usdz")
        for view, url in task["thumbnail_urls"].items():
            run.download(url, f"armchair-{view}.png")

    run.execute(pipeline)


if __name__ == "__main__":
    main()
