"""Turn character concept art into a textured GLB."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # so `shared` imports
from shared.python.meshy import Meshy

DIRECTORY = Path(__file__).resolve().parent
SAMPLE = DIRECTORY.parent / "input/concept-art.png"
INPUT = Path(sys.argv[1]) if len(sys.argv) > 1 else SAMPLE
OUTPUT = DIRECTORY / "output"

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
client.download(task["model_urls"]["glb"], OUTPUT / "character.glb")
client.download(task["thumbnail_url"], OUTPUT / "character-thumbnail.png")
print(f"Done: {OUTPUT / 'character.glb'}  ({task['consumed_credits']} credits)")
