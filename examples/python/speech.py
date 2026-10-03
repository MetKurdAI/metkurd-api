"""Server-side Apollo workflow. Configure environment variables; see examples/README.md."""
import os
import sys
import time
from urllib.parse import quote

import requests

BASE = "https://metkurd.ai/api/v2"


def configured(name):
    value = os.environ.get(name, "").strip()
    if not value or value in {"YOUR_API_KEY", "VOICE_ID", "YOUR_UNIQUE_REQUEST_ID", "JOB_ID"}:
        raise RuntimeError(f"Set {name} locally; replace the placeholder.")
    return value


def check(response):
    if not 200 <= response.status_code < 300:
        try:
            code = response.json().get("error", {}).get("code", "http_error")
        except (ValueError, AttributeError):
            code = "non_json_response"
        raise RuntimeError(f"HTTP {response.status_code}: {code}. Preserve the original request key/input.")
    return response


def run(http=requests, sleep=time.sleep, output="result.wav", attempts=60):
    headers = {"Authorization": "Bearer " + configured("METKURD_API_KEY"), "Accept": "application/json"}
    job_id = os.environ.get("METKURD_JOB_ID", "").strip()
    if job_id:
        job_id = configured("METKURD_JOB_ID")
    else:
        key = configured("METKURD_IDEMPOTENCY_KEY")
        payload = {"text": "سڵاو لە مێتکوردەوە", "voice": configured("METKURD_VOICE_ID"),
                   "model": "2.0", "language": "ckb", "storage_mode": "temporary"}
        # A timeout here is ambiguous: rerun with the SAME key and payload.
        with http.post(BASE + "/speech", headers={**headers, "Idempotency-Key": key},
                       json=payload, timeout=(15, 90), allow_redirects=False) as response:
            job_id = check(response).json()["id"]
    print("Job:", job_id, flush=True)
    for attempt in range(attempts):
        with http.get(BASE + "/jobs/" + quote(job_id, safe=""), headers=headers,
                      timeout=(15, 30), allow_redirects=False) as response:
            if response.status_code == 429:
                retry = response.headers.get("Retry-After", "10")
                sleep(max(1, int(retry)) if retry.isdigit() else 10)
                continue
            job = check(response).json()
        status = job["status"]
        print("Status:", status, flush=True)
        if status in {"failed", "cancelled"}:
            raise RuntimeError(f"Job {status}: {job.get('error', {}).get('code', status)}")
        if status == "completed":
            result = job.get("result") or {}
            files = result.get("files", [])
            if result.get("expired") or not files:
                raise RuntimeError("No available result files; the result may have expired.")
            # Use the returned public file ID on the canonical authenticated origin.
            url = BASE + "/files/" + quote(files[0]["id"], safe="") + "/download"
            with http.get(url, headers={"Authorization": headers["Authorization"]}, stream=True,
                          timeout=(15, 90), allow_redirects=False) as response:
                check(response)
                with open(output, "wb") as target:
                    for chunk in response.iter_content(chunk_size=64 * 1024):
                        if chunk:
                            target.write(chunk)
            print("Downloaded:", output)
            return job_id
        if status not in {"queued", "processing"}:
            raise RuntimeError("Unknown job status; inspect the response before continuing.")
        if attempt + 1 < attempts:
            sleep(10)
    raise RuntimeError(f"Polling limit reached. Job still exists; resume with METKURD_JOB_ID={job_id}.")


if __name__ == "__main__":
    try:
        run()
    except requests.RequestException:
        print("Network request failed. Keep the same input/key; resume with the job ID if known.", file=sys.stderr)
        sys.exit(1)
    except (RuntimeError, KeyError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
