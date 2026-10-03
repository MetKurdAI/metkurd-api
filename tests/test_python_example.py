"""Synthetic offline HTTP responses; no API keys, network calls or paid jobs."""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import requests

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("example", ROOT / "examples/python/speech.py")
example = importlib.util.module_from_spec(spec)
spec.loader.exec_module(example)


class Response:
    def __init__(self, data=None, status=200, headers=None):
        self.data = data
        self.status_code = status
        self.headers = headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def json(self):
        return self.data

    def iter_content(self, chunk_size):
        return iter([b"SYNTHETIC_", b"AUDIO"])


class Http:
    def __init__(self, reads, submit=None):
        self.reads = list(reads)
        self.submit = submit or Response({"id": "JOB_ID"}, 202)
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append(("POST", url, kwargs))
        if isinstance(self.submit, Exception):
            raise self.submit
        return self.submit

    def get(self, url, **kwargs):
        self.calls.append(("GET", url, kwargs))
        if url.endswith("/download"):
            return Response()
        return self.reads.pop(0)


def completed(expired=False):
    return Response({"status": "completed", "result": {"expired": expired,
        "files": [] if expired else [{"id": "FILE_ID"}]}})


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"METKURD_API_KEY": "UNUSED_PLACEHOLDER",
            "METKURD_VOICE_ID": "DISCOVERED_VOICE_PLACEHOLDER",
            "METKURD_IDEMPOTENCY_KEY": "REQUEST_PLACEHOLDER", "METKURD_JOB_ID": ""})
        self.env.start()
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.output = str(Path(self.temp.name) / "result.wav")

    def tearDown(self):
        self.temp.cleanup()
        self.env.stop()

    def run_workflow(self, http, **options):
        self.delays = []
        with contextlib.redirect_stdout(io.StringIO()):
            return example.run(http=http, sleep=self.delays.append, output=self.output, **options)

    def test_submission_polling_and_authenticated_stream(self):
        http = Http([Response({"status": "queued"}), Response({"status": "processing"}), completed()])
        self.assertEqual(self.run_workflow(http), "JOB_ID")
        self.assertEqual(Path(self.output).read_bytes(), b"SYNTHETIC_AUDIO")
        self.assertEqual(len([c for c in http.calls if c[0] == "POST"]), 1)
        self.assertEqual(http.calls[0][2]["headers"]["Idempotency-Key"], "REQUEST_PLACEHOLDER")
        self.assertTrue(http.calls[-1][2]["stream"])
        self.assertTrue(all(c[2]["headers"]["Authorization"] == "Bearer UNUSED_PLACEHOLDER" for c in http.calls))
        self.assertTrue(all(c[2]["allow_redirects"] is False for c in http.calls))

    def test_resume_skips_submission(self):
        os.environ["METKURD_JOB_ID"] = "SAVED_JOB_PLACEHOLDER"
        http = Http([completed()])
        self.run_workflow(http)
        self.assertTrue(all(c[0] == "GET" for c in http.calls))

    def test_rate_limit_respects_retry_after(self):
        self.run_workflow(Http([Response({}, 429, {"Retry-After": "17"}), completed()]))
        self.assertEqual(self.delays, [17])

    def test_terminal_failure_and_cancellation_never_download_or_repost(self):
        for status in ["failed", "cancelled"]:
            with self.subTest(status=status):
                http = Http([Response({"status": status, "error": {"code": "processing_failed"}})])
                with self.assertRaisesRegex(RuntimeError, "Job " + status):
                    self.run_workflow(http)
                self.assertEqual(len(http.calls), 2)

    def test_expiry_never_downloads(self):
        http = Http([completed(True)])
        with self.assertRaisesRegex(RuntimeError, "No available"):
            self.run_workflow(http)
        self.assertEqual(len(http.calls), 2)

    def test_polling_limit_preserves_existing_job(self):
        http = Http([Response({"status": "processing"})])
        with self.assertRaisesRegex(RuntimeError, "resume with METKURD_JOB_ID"):
            self.run_workflow(http, attempts=1)
        self.assertEqual(len(http.calls), 2)

    def test_ambiguous_submission_is_not_retried(self):
        http = Http([], requests.Timeout())
        with self.assertRaises(requests.Timeout):
            self.run_workflow(http)
        self.assertEqual(len(http.calls), 1)

    def test_conflict_is_not_retried(self):
        http = Http([], Response({"error": {"code": "idempotency_conflict"}}, 409))
        with self.assertRaisesRegex(RuntimeError, "idempotency_conflict"):
            self.run_workflow(http)
        self.assertEqual(len(http.calls), 1)


if __name__ == "__main__":
    unittest.main()
