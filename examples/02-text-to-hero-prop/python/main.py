"""Turn a text prompt into an Ultra, 4K-textured hero prop GLB."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # so `shared` imports
from shared.python.meshy import Meshy

DIRECTORY = Path(__file__).resolve().parent
SAMPLE = (
    "Marrow's sea chest, a closed pirate treasure chest: weathered oak planks, "
    "black iron straps and rivets, a heavy brass padlock, barnacles along the base. "
    "Stylized hand-painted game prop, three-quarter view."
)
PROMPT = " ".join(sys.argv[1:]) or SAMPLE
OUTPUT = DIRECTORY / "output"

client = Meshy()  # reads MESHY_API_KEY from .env
concept_id = client.create(
    "text-to-image",
    {
        "ai_model": "gpt-image-2-5-sunburst",
        "prompt": PROMPT,
        "remove_background": True,
    },
)
concept = client.wait("text-to-image", concept_id)
client.download(concept["image_urls"][0], OUTPUT / "hero-prop-concept.png")

task_id = client.create(
    "image-to-3d",
    {
        "input_task_id": concept_id,
        "ultra_mode": True,
        "should_texture": True,
        "enable_pbr": True,
        "texture_resolution": "4k",
        "target_formats": ["glb"],
    },
)
task = client.wait("image-to-3d", task_id)
client.download(task["model_urls"]["glb"], OUTPUT / "hero-prop.glb")
client.download(task["thumbnail_url"], OUTPUT / "hero-prop-thumbnail.png")
credits = concept["consumed_credits"] + task["consumed_credits"]
print(f"Done: {OUTPUT / 'hero-prop.glb'}  ({credits} credits)")
