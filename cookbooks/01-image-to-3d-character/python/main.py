"""Turn character concept art into a textured GLB."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # so `shared` imports
from shared.python.meshy import Meshy
from shared.python.run import Run, arguments

DIRECTORY = Path(__file__).resolve().parent
INPUT = DIRECTORY.parent / "input/concept-art.png"


def main() -> None:
    args = arguments(
        DIRECTORY, "Turn character concept art into a textured GLB.", images=[INPUT]
    )
    run = Run("01-image-to-3d-character", args, DIRECTORY, 30)

    def pipeline(run):
        task = run.task(
            "model",
            "image-to-3d",
            {
                "image_url": Meshy.data_uri(args.input[0]),
                "should_texture": True,
                "enable_pbr": True,
                "target_formats": ["glb"],
            },
        )
        run.download(task["model_urls"]["glb"], "character.glb")
        run.download(task["thumbnail_url"], "character-thumbnail.png")

    run.execute(pipeline)


if __name__ == "__main__":
    main()
