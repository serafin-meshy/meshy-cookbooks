"""Compare the actual offline plans from both languages; no API calls."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TSX = (
    ROOT
    / "cookbooks/01-image-to-3d-character/typescript/node_modules/tsx/dist/loader.mjs"
)


def invoke(command, cwd):
    env = dict(os.environ)
    env.pop("MESHY_API_KEY", None)
    result = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True)
    if result.returncode:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


with tempfile.TemporaryDirectory() as directory:
    for recipe in sorted((ROOT / "cookbooks").iterdir()):
        if not (recipe / "python/main.py").exists():
            continue
        output = str(Path(directory).resolve() / recipe.name)
        flags = ["--dry-run", "--output", output]
        for custom in (False, True):
            extra = []
            if custom:
                extra = (
                    ["--prompt", "A ceramic café lamp 🪔"]
                    if recipe.name.startswith("02")
                    else [
                        "--input",
                        str(
                            next(
                                (recipe / "input").rglob(
                                    "*.png" if recipe.name.startswith("01") else "*.jpg"
                                )
                            )
                        ),
                    ]
                )
            python = invoke(
                [sys.executable, str(recipe / "python/main.py"), *flags, *extra],
                directory,
            )
            typescript = invoke(
                [
                    "node",
                    "--import",
                    TSX.as_uri(),
                    str(recipe / "typescript/main.ts"),
                    *flags,
                    *extra,
                ],
                directory,
            )
            assert python == typescript, f"Language drift: {recipe.name}"
            assert not Path(output).exists(), "Dry run created output files"
        print(f"PASS: {recipe.name} (default and custom inputs, launched outside repo)")
