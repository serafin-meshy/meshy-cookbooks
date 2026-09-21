"""Turn a low-poly concept image into a low-poly GLB in seconds."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # so `shared` imports
from shared.python.meshy import Meshy

DIRECTORY = Path(__file__).resolve().parent
SAMPLE = DIRECTORY.parent / "input/low-poly-oak.png"
INPUT = Path(sys.argv[1]) if len(sys.argv) > 1 else SAMPLE
POLYCOUNT = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
OUTPUT = DIRECTORY / "output"

client = Meshy()  # reads MESHY_API_KEY from .env
task_id = client.create(
    "image-to-3d",
    {
        "image_url": Meshy.data_uri(INPUT),
        "model_type": "smart-topology",
        "target_polycount": POLYCOUNT,
        "should_texture": False,
        "target_formats": ["glb"],
    },
)
task = client.wait("image-to-3d", task_id)
client.download(task["model_urls"]["glb"], OUTPUT / "low-poly-prop.glb")
client.download(task["thumbnail_url"], OUTPUT / "low-poly-prop-thumbnail.png")
print(f"Done: {OUTPUT / 'low-poly-prop.glb'}  ({task['consumed_credits']} credits)")
