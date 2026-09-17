"""Turn a text prompt into an Ultra, 4K-textured hero prop GLB."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # so `shared` imports
from shared.python.run import Run, arguments

DIRECTORY = Path(__file__).resolve().parent
PROMPT = (
    "Marrow's sea chest, a closed pirate treasure chest: weathered oak planks, "
    "black iron straps and rivets, a heavy brass padlock, barnacles along the base. "
    "Stylized hand-painted game prop, three-quarter view."
)


def main() -> None:
    args = arguments(
        DIRECTORY,
        "Turn a text prompt into an Ultra, 4K-textured hero prop GLB.",
        prompt=PROMPT,
    )
    run = Run("02-text-to-hero-prop", args, DIRECTORY, 44)

    def pipeline(run):
        concept = run.task(
            "concept",
            "text-to-image",
            {
                "ai_model": "gpt-image-2-5-sunburst",
                "prompt": args.prompt,
                "remove_background": True,
            },
        )
        run.download(concept["image_urls"][0], "hero-prop-concept.png")

        task = run.task(
            "model",
            "image-to-3d",
            {
                "input_task_id": concept["id"],
                "ultra_mode": True,
                "should_texture": True,
                "enable_pbr": True,
                "texture_resolution": "4k",
                "target_formats": ["glb"],
            },
        )
        run.download(task["model_urls"]["glb"], "hero-prop.glb")
        run.download(task["thumbnail_url"], "hero-prop-thumbnail.png")

    run.execute(pipeline)


if __name__ == "__main__":
    main()
