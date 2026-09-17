"""Turn character concept art into a textured GLB."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # so `shared` imports
from shared.python.meshy import Meshy

INPUT = Path("../input/concept-art.png")
OUTPUT = Path("output")


def main() -> None:
    client = Meshy()  # reads MESHY_API_KEY from .env
    task_id = client.create(
        "image-to-3d",
        {
            "image_url": Meshy.data_uri(INPUT),
            "should_texture": True,
            "enable_pbr": True,
            "target_formats": ["glb"],
        },
    )
    task = client.wait("image-to-3d", task_id)
    glb = client.download(task["model_urls"]["glb"], OUTPUT / "character.glb")
    client.download(task["thumbnail_url"], OUTPUT / "character-thumbnail.png")
    print(f"Done: {glb}  ({task['consumed_credits']} credits)")


if __name__ == "__main__":
    main()
