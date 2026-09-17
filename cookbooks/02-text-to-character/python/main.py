"""Turn a text prompt into a T-posed, 4K-textured character GLB."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # so `shared` imports
from shared.python.meshy import Meshy

PROMPT = (
    "Wren, a young forest ranger: short auburn hair, green hooded cloak, "
    "leather bracers, brown boots, a small satchel on the hip. "
    "Full body, stylized hand-painted game character, no weapon."
)
OUTPUT = Path("output")


def main() -> None:
    client = Meshy()  # reads MESHY_API_KEY from .env
    concept_id = client.create(
        "text-to-image",
        {
            "ai_model": "gpt-image-2-5-sunburst",
            "prompt": PROMPT,
            "remove_background": True,
            "pose_mode": "t-pose",
        },
    )
    concept = client.wait("text-to-image", concept_id, "concept")
    client.download(concept["image_urls"][0], OUTPUT / "character-concept.png")

    task_id = client.create(
        "image-to-3d",
        {
            "input_task_id": concept_id,
            "ultra_mode": True,
            "should_texture": True,
            "enable_pbr": True,
            "texture_resolution": "4k",
            "pose_mode": "t-pose",
            "target_formats": ["glb"],
        },
    )
    task = client.wait("image-to-3d", task_id, "model")
    glb = client.download(task["model_urls"]["glb"], OUTPUT / "character.glb")
    client.download(task["thumbnail_url"], OUTPUT / "character-thumbnail.png")
    credits = concept["consumed_credits"] + task["consumed_credits"]
    print(f"Done: {glb}  ({credits} credits)")


if __name__ == "__main__":
    main()
