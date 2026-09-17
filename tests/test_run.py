import json
import struct
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

from shared.python.run import Run, validate_glb


class FakeMeshy:
    def __init__(self):
        self.creates = []
        self.waits = []
        self.downloads = []
        self.fail_wait = False
        self.fail_create = False
        self.bad_download = False

    def create(self, endpoint, payload):
        self.creates.append((endpoint, payload))
        if self.fail_create:
            raise TimeoutError("POST response lost")
        return str(len(self.creates))

    def wait(self, endpoint, task_id, label):
        self.waits.append(task_id)
        if self.fail_wait:
            raise TimeoutError("Polling interrupted")
        return {
            "id": task_id,
            "status": "SUCCEEDED",
            "consumed_credits": 9 if label == "concept" else 35,
            "model_urls": {"glb": "fake-url"},
        }

    def download(self, url, dest):
        self.downloads.append(str(dest))
        dest.write_bytes(
            b"broken" if self.bad_download else struct.pack("<4sII", b"glTF", 2, 12)
        )
        return dest


class RunTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.output = self.directory / "output"
        self.api = FakeMeshy()
        self.mock = patch("shared.python.run.Meshy", return_value=self.api)
        self.mock.start()

    def tearDown(self):
        self.mock.stop()
        self.temp.cleanup()

    def run_for(self, resume=False, prompt="chair", dry=False):
        args = Namespace(output=self.output, resume=resume, dry_run=dry, prompt=prompt)
        return Run("test", args, self.directory, 44)

    def pipeline(self, run):
        concept = run.task("concept", "text-to-image", {"prompt": "chair"})
        task = run.task("model", "image-to-3d", {"input_task_id": concept["id"]})
        run.download(task["model_urls"]["glb"], "chair.glb")

    def state(self):
        return json.loads((self.output / "result.json").read_text())

    def test_resume_after_polling_timeout_and_completed_run_is_offline(self):
        self.api.fail_wait = True
        with self.assertRaises(TimeoutError):
            self.run_for().execute(self.pipeline)
        self.assertEqual(self.state()["tasks"]["concept"]["id"], "1")
        self.api.fail_wait = False
        self.run_for(resume=True).execute(self.pipeline)
        self.assertEqual(len(self.api.creates), 2)
        self.assertEqual(self.state()["consumed_credits"], 44)
        self.assertEqual(self.state()["status"], "SUCCEEDED")
        waits = len(self.api.waits)
        self.run_for(resume=True).execute(self.pipeline)
        self.assertEqual(len(self.api.waits), waits)
        self.assertEqual(len(self.api.downloads), 1)

    def test_ambiguous_submission_is_never_resubmitted(self):
        self.api.fail_create = True
        with self.assertRaises(TimeoutError):
            self.run_for().execute(self.pipeline)
        with self.assertRaisesRegex(RuntimeError, "outcome unknown"):
            self.run_for(resume=True).execute(self.pipeline)
        self.assertEqual(len(self.api.creates), 1)

    def test_existing_run_changed_inputs_and_changed_payload_are_rejected(self):
        self.api.fail_wait = True
        with self.assertRaises(TimeoutError):
            self.run_for().execute(self.pipeline)
        for run in [self.run_for(), self.run_for(resume=True, prompt="lamp")]:
            with self.assertRaises(ValueError):
                run.execute(self.pipeline)
        with self.assertRaisesRegex(ValueError, "parameters changed"):
            self.run_for(resume=True).execute(
                lambda run: run.task("concept", "text-to-image", {"prompt": "lamp"})
            )
        self.assertEqual(len(self.api.creates), 1)

    def test_bad_download_recovers_without_new_tasks(self):
        self.api.bad_download = True
        with self.assertRaises(ValueError):
            self.run_for().execute(self.pipeline)
        self.assertFalse((self.output / "chair.glb").exists())
        self.assertEqual(self.state()["artifacts"], {})
        self.api.bad_download = False
        self.run_for(resume=True).execute(self.pipeline)
        self.assertEqual(len(self.api.creates), 2)
        self.assertEqual(self.state()["consumed_credits"], 44)
        validate_glb(self.output / "chair.glb")

    def test_modified_artifact_is_redownloaded(self):
        self.run_for().execute(self.pipeline)
        (self.output / "chair.glb").write_bytes(b"damaged")
        self.run_for(resume=True).execute(self.pipeline)
        self.assertEqual(len(self.api.creates), 2)
        self.assertEqual(len(self.api.downloads), 2)

    def test_lock_missing_resume_and_dry_run(self):
        with self.assertRaises(FileNotFoundError):
            self.run_for(resume=True).execute(self.pipeline)
        self.assertFalse((self.output / ".run.lock").exists())
        (self.output / ".run.lock").touch()
        with self.assertRaisesRegex(RuntimeError, "locked"):
            self.run_for().execute(self.pipeline)
        self.run_for(dry=True).execute(self.pipeline)
        self.assertEqual(self.api.creates, [])
        self.assertFalse((self.output / "result.json").exists())


if __name__ == "__main__":
    unittest.main()
