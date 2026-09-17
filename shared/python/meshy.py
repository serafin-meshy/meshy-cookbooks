"""Minimal Meshy API client: create a task, poll it, download the result.

Copy this file into your own project. Needs `requests` and `python-dotenv`.
"""

from __future__ import annotations

import base64
import mimetypes
import os
import time
from pathlib import Path

import requests
from dotenv import find_dotenv, load_dotenv

BASE_URL = "https://api.meshy.ai/openapi/v1"
POLL_SECONDS = 5


class MeshyAPIError(Exception):
    """Non-2xx response from the Meshy API. Carries `status` and `body`."""

    def __init__(self, status: int, body: str) -> None:
        super().__init__(f"Meshy API returned {status}: {body}")
        self.status = status
        self.body = body


class MeshyTaskError(Exception):
    """Task ended FAILED or CANCELED. Carries the task and `task_error.message`."""

    def __init__(self, task: dict) -> None:
        self.task = task
        self.message = (task.get("task_error") or {}).get("message") or task["status"]
        super().__init__(f"Task {task['id']} {task['status']}: {self.message}")


class MeshyTimeoutError(TimeoutError):
    """Task still PENDING or IN_PROGRESS when `wait` hit its timeout. Carries the task."""

    def __init__(self, task: dict, timeout: float) -> None:
        self.task = task
        super().__init__(
            f"Task {task['id']} still {task['status']} after {timeout:.0f} s"
        )


class Meshy:
    """Thin client over POST /<endpoint>, GET /<endpoint>/:id, and result downloads."""

    def __init__(
        self, api_key: str | None = None, env_file: Path | None = None
    ) -> None:
        """Use `api_key`, or MESHY_API_KEY from the environment or the nearest .env."""
        load_dotenv(env_file if env_file is not None else find_dotenv(usecwd=True))
        self.api_key = api_key or os.environ.get("MESHY_API_KEY", "")
        if not self.api_key:
            raise RuntimeError(
                "MESHY_API_KEY is not set. Copy .env.example to .env and paste your key."
            )
        self.session = requests.Session()
        self.session.headers["Authorization"] = f"Bearer {self.api_key}"

    def create(self, endpoint: str, payload: dict) -> str:
        """POST `payload` to /<endpoint>; return the task id. Retries 429 three times."""
        post = lambda: self.session.post(
            f"{BASE_URL}/{endpoint}", json=payload, timeout=60
        )
        response = post()
        for attempt in range(3):
            if response.status_code != 429:
                break
            time.sleep(2**attempt)
            response = post()
        if not response.ok:
            raise MeshyAPIError(response.status_code, response.text)
        return response.json()["result"]

    def get(self, endpoint: str, task_id: str) -> dict:
        """GET /<endpoint>/<task_id> and return the task object."""
        response = self.session.get(f"{BASE_URL}/{endpoint}/{task_id}", timeout=60)
        if not response.ok:
            raise MeshyAPIError(response.status_code, response.text)
        return response.json()

    def wait(
        self, endpoint: str, task_id: str, label: str = "", timeout: float = 1800
    ) -> dict:
        """Poll every 5 s, printing progress (prefixed by `label`), until SUCCEEDED. Raises on FAILED/CANCELED/timeout."""
        deadline = time.monotonic() + timeout
        prefix = f"{label} " if label else ""
        last = ""
        while True:
            task = self.get(endpoint, task_id)
            state = f"  {prefix}{task['status']:<11} {task.get('progress', 0):>3}%"
            if state != last:
                print(state, flush=True)
                last = state
            if task["status"] == "SUCCEEDED":
                return task
            if task["status"] in ("FAILED", "CANCELED"):
                raise MeshyTaskError(task)
            if time.monotonic() >= deadline:
                raise MeshyTimeoutError(task, timeout)
            time.sleep(POLL_SECONDS)

    def download(self, url: str, dest: Path) -> Path:
        """Stream a result URL to `dest` (parent folders created) and return `dest`."""
        dest.parent.mkdir(parents=True, exist_ok=True)
        # Signed URL: no auth header.
        with requests.get(url, stream=True, timeout=120) as response:
            if not response.ok:
                raise MeshyAPIError(response.status_code, response.text)
            with open(dest, "wb") as f:
                for chunk in response.iter_content(chunk_size=1 << 16):
                    f.write(chunk)
        return dest

    @staticmethod
    def data_uri(path: Path) -> str:
        """Encode a local .png/.jpg as a base64 data URI for `image_url` fields."""
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"
