"""CLI and resumable execution for the cookbooks. Copy alongside meshy.py."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from .meshy import Meshy


def arguments(directory: Path, description: str, *, images=None, prompt=None):
    """Parse the same options supported by the TypeScript recipes."""
    parser = argparse.ArgumentParser(description=description)
    if images is not None:
        parser.add_argument(
            "--input",
            action="append",
            type=Path,
            help="PNG/JPEG path; repeat for product photos, front first",
        )
    if prompt is not None:
        parser.add_argument("--prompt", default=prompt)
    parser.add_argument("--output", type=Path, default=directory / "output")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print a plan; no API calls or files",
    )
    parser.add_argument(
        "--resume", action="store_true", help="Continue the run saved in --output"
    )
    args = parser.parse_args()
    if args.dry_run and args.resume:
        parser.error("--dry-run and --resume cannot be combined")
    args.output = args.output.resolve()
    if images is not None:
        args.input = [p.resolve() for p in (args.input or images)]
        maximum = 1 if len(images) == 1 else 4
        if not 1 <= len(args.input) <= maximum:
            parser.error(f"Expected 1 to {maximum} input images")
        for path in args.input:
            data = path.read_bytes()
            valid = (
                path.suffix.lower() == ".png" and data.startswith(b"\x89PNG\r\n\x1a\n")
            ) or (
                path.suffix.lower() in (".jpg", ".jpeg")
                and data.startswith(b"\xff\xd8\xff")
            )
            if not valid:
                parser.error(
                    f"Expected a PNG or JPEG with a matching extension: {path}"
                )
    if prompt is not None and not args.prompt.strip():
        parser.error("--prompt must not be empty")
    return args


def digest(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
    ).hexdigest()


def validate_glb(path: Path):
    """Check GLB v2 header and declared length, not geometry or visual quality."""
    with path.open("rb") as stream:
        header = stream.read(12)
    if len(header) != 12 or struct.unpack("<4sII", header) != (
        b"glTF",
        2,
        path.stat().st_size,
    ):
        raise ValueError(f"Invalid GLB v2 header or length: {path}")


def summarize(value):
    if isinstance(value, dict):
        return {k: summarize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [summarize(v) for v in value]
    if isinstance(value, str) and value.startswith("data:"):
        return value.split(",", 1)[0] + ",<omitted>"
    return value


class Run:
    """Persist task IDs before polling; never blindly resubmit an uncertain POST."""

    def __init__(self, recipe, args, directory, estimated_credits):
        self.recipe, self.args, self.directory = recipe, args, directory
        self.estimated_credits = estimated_credits
        self.output = args.output
        self.path = self.output / "result.json"
        self.client = None
        self.state = {
            "schema_version": 1,
            "recipe": recipe,
            "status": "RUNNING",
            "tasks": {},
            "artifacts": {},
            "consumed_credits": 0,
        }
        self.plan = []

    def save(self):
        temporary = self.output / "result.json.tmp"
        temporary.write_text(json.dumps(self.state, indent=2) + "\n")
        temporary.replace(self.path)

    def execute(self, workflow):
        """Run under an exclusive output-folder lock, or print an offline plan."""
        if self.args.dry_run:
            workflow(self)
            print(
                json.dumps(
                    {
                        "mode": "dry-run",
                        "recipe": self.recipe,
                        "estimated_credits": self.estimated_credits,
                        "output": str(self.output),
                        "steps": self.plan,
                    },
                    indent=2,
                )
            )
            return
        self.output.mkdir(parents=True, exist_ok=True)
        lock = self.output / ".run.lock"
        try:
            handle = lock.open("x")
        except FileExistsError:
            raise RuntimeError(
                f"Run locked: {lock}. See RUNNING.md before removing a stale lock."
            )
        try:
            handle.close()
            configuration = {
                "prompt": getattr(self.args, "prompt", None),
                "input_sha256": [
                    hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in getattr(self.args, "input", [])
                ],
            }
            if self.args.resume:
                self.state = json.loads(self.path.read_text())
                if (
                    self.state.get("schema_version") != 1
                    or self.state.get("recipe") != self.recipe
                ):
                    raise ValueError(
                        "Saved run has a different recipe or unsupported schema"
                    )
                if self.state.get("configuration") != configuration:
                    raise ValueError(
                        "Inputs changed. Repeat the original flags or use a new --output directory."
                    )
                if (
                    self.state["status"] == "SUCCEEDED"
                    and self.state["artifacts"]
                    and all(
                        (self.output / name).is_file()
                        and hashlib.sha256(
                            (self.output / name).read_bytes()
                        ).hexdigest()
                        == saved["sha256"]
                        for name, saved in self.state["artifacts"].items()
                    )
                ):
                    print(
                        f"Already complete: {self.path}  ({self.state['consumed_credits']} credits)"
                    )
                    return
            elif self.path.exists():
                raise ValueError(
                    "This output already has a run. Use --resume or a new --output directory."
                )
            if not self.args.resume and any(
                p.name not in (".run.lock", ".gitkeep", ".DS_Store")
                for p in self.output.iterdir()
            ):
                raise ValueError(
                    "Output directory contains files without a saved run. Use a new --output directory."
                )
            self.state["configuration"] = configuration
            self.state["status"] = "RUNNING"
            self.save()
            print(
                f"Estimated full-run cost: ~{self.estimated_credits} credits; resuming reuses saved task IDs."
            )
            try:
                workflow(self)
                self.state["status"] = "SUCCEEDED"
                self.save()
                print(f"Done: {self.path}  ({self.state['consumed_credits']} credits)")
            except BaseException as error:
                self.state["status"] = (
                    "INTERRUPTED" if isinstance(error, KeyboardInterrupt) else "ERROR"
                )
                self.save()
                raise
        finally:
            lock.unlink()

    def api(self):
        if self.client is None:
            self.client = Meshy(env_file=self.directory / ".env")
        return self.client

    def task(self, label, endpoint, payload):
        """Create once, save the ID, and poll; a resume fetches fresh result URLs."""
        if self.args.dry_run:
            self.plan.append(
                {"stage": label, "endpoint": endpoint, "payload": summarize(payload)}
            )
            return {
                "id": f"<saved-{label}-id>",
                "model_urls": {"glb": "<glb-url>", "usdz": "<usdz-url>"},
                "image_urls": ["<image-url>"],
                "thumbnail_url": "<thumbnail-url>",
                "thumbnail_urls": {
                    view: f"<{view}-url>" for view in ("front", "right", "back", "left")
                },
            }
        fingerprint = digest(payload)
        saved = self.state["tasks"].get(label)
        if saved:
            if saved["endpoint"] != endpoint or saved["payload_sha256"] != fingerprint:
                raise ValueError(
                    f"Inputs or parameters changed for {label}. Use a new --output directory."
                )
            if not saved.get("id"):
                raise RuntimeError(
                    f"Submission outcome unknown for {label}; reconcile the task in Meshy before retrying. See RUNNING.md."
                )
        else:
            client = self.api()  # Validate credentials before recording a submission.
            saved = {
                "endpoint": endpoint,
                "payload_sha256": fingerprint,
                "status": "SUBMITTING",
                "requested_model": payload.get("ai_model", "latest"),
            }
            self.state["tasks"][label] = saved
            self.save()
            saved["id"] = client.create(endpoint, payload)
            saved["status"] = "PENDING"
            self.save()
        try:
            task = self.api().wait(endpoint, saved["id"], label)
        except Exception as error:
            if hasattr(error, "task"):
                saved["status"] = error.task["status"]
                self.save()
            raise
        saved["status"] = task["status"]
        saved["consumed_credits"] = task.get("consumed_credits", 0)
        if task.get("ai_model"):
            saved["reported_model"] = task["ai_model"]
        self.state["consumed_credits"] = sum(
            t.get("consumed_credits", 0) for t in self.state["tasks"].values()
        )
        self.save()
        return task

    def download(self, url, filename):
        """Atomically download; reuse only files matching a saved checksum."""
        if Path(filename).name != filename:
            raise ValueError("Artifact name must be a filename")
        dest = self.output / filename
        if self.args.dry_run:
            self.plan.append({"artifact": str(dest)})
            return dest
        saved = self.state["artifacts"].get(filename)
        if (
            saved
            and dest.is_file()
            and hashlib.sha256(dest.read_bytes()).hexdigest() == saved["sha256"]
        ):
            return dest
        partial = self.output / (filename + ".part")
        self.api().download(url, partial)
        if partial.stat().st_size == 0:
            raise ValueError(f"Empty download: {filename}")
        if dest.suffix == ".glb":
            validate_glb(partial)
        partial.replace(dest)
        self.state["artifacts"][filename] = {
            "path": str(dest),
            "bytes": dest.stat().st_size,
            "sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
            "validation": "glb-header" if dest.suffix == ".glb" else "nonempty",
        }
        self.save()
        return dest
