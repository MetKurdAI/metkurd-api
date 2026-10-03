# Run the Examples

Run commands from the repository root. Examples make real, potentially billable
requests only when you run them with your own credentials. The offline tests do not.
Do not run every example to retry one job: resume its ID or reuse the exact original input/key.

Set environment variables locally (shown in Bash; use your shell's equivalent):

```bash
export METKURD_API_KEY='YOUR_API_KEY'
export METKURD_VOICE_ID='VOICE_ID'
export METKURD_IDEMPOTENCY_KEY='YOUR_UNIQUE_REQUEST_ID'
```

Replace the voice placeholder using authenticated `GET /voices`. Generate a fresh
unique idempotency value for each new logical request and save it before submission.
The executable examples reject unchanged key/voice/request placeholders. They do
not automatically create a new retry identity. Do not paste real keys into tracked files.

```bash
# Choose ONE client for your first request.
bash examples/curl/speech.sh

python -m pip install -r examples/python/requirements.txt
python examples/python/speech.py

php examples/php/speech.php

node examples/node/speech.mjs

node examples/javascript/server-speech.mjs
```

Python needs 3.10+ and requests. PHP needs 8.2+ with cURL. Node/JavaScript use
Node.js 20+ native fetch, no npm packages. cURL needs Bash, jq and cURL with
`--fail-with-body` support. Examples print the job ID and status, wait about ten
seconds between reads, stop after 60 read attempts, and save the first audio result
as `result.wav`. That filename applies to these Apollo speech examples only.

## Resume a Job

Set the actual returned ID, then run any client:

```bash
export METKURD_JOB_ID='JOB_ID'
```

Replace `JOB_ID` with your returned string. When present, this skips submission
entirely. Voice and idempotency variables are then unnecessary. Unset METKURD_JOB_ID
before intentionally starting a new job. A polling timeout never cancels a job.

On a lost submission response, keep the same idempotency key and exact inputs;
rerun the same client. Do not switch multipart/JSON encodings or change optional
fields for that retry. On HTTP errors, inspect the code and [error guide](../docs/errors.md).
No example silently retries POST with a new key. Downloads use Bearer authentication
and reject redirects. Failed/expired jobs do not trigger a new submission.

## JavaScript and Browsers

[workflow.mjs](javascript/workflow.mjs) contains the complete fetch workflow, reused
by the Node and server JavaScript entry points. It accepts server-held credentials
and a download sink. Do not ship it with credentials in a browser bundle.

A browser should call your own authenticated backend. That backend validates the
user/input, enforces spending and access controls, stores the idempotency identity,
calls MetKurd, and streams only authorized results back. There is no public example
proxy endpoint here because your application's authentication is application-specific.

Other service submissions are shown in [service guides](../README.md#available-services),
[cURL requests](curl/requests.md), and [Postman](../postman/README.md). Use the same
job/read/download flow for all generation services; `/references` returns metadata directly.
