# MetKurd REST API V2

MetKurd AI provides Kurdish-focused AI APIs for speech, voice cloning, transcription,
captions, OCR, diacritization, multi-speaker generation and audio separation.
This is the official documentation and plain-example repository for MetKurd REST API V2.

You need a [MetKurd AI account](https://metkurd.ai), an eligible active subscription/plan
with API access, the relevant service permissions, and sufficient API credits.
Sign in to MetKurd and open the developer/API portal to create an API key.
Keep the key on your trusted backend and never commit it to source control.
Account and service availability, limits and entitlements are determined by your
current MetKurd account and plan. Check the website and developer/API portal for details.

## Quick Start

Base URL: `https://metkurd.ai/api/v2`. Machine API paths have no locale prefix.
The commands below use Bash syntax and cURL. Replace placeholders locally.

```bash
export METKURD_API_KEY='YOUR_API_KEY'
# Choose a new unique value for a new request; keep it for retries of that request.
export METKURD_IDEMPOTENCY_KEY='YOUR_UNIQUE_REQUEST_ID'

# Discover voice IDs allowed for your account.
curl --fail-with-body 'https://metkurd.ai/api/v2/voices' \
  -H "Authorization: Bearer $METKURD_API_KEY" \
  -H 'Accept: application/json'
```

Replace `VOICE_ID` below with an `id` from `voices[]`, then submit Apollo 2:

```bash
curl --fail-with-body -X POST "https://metkurd.ai/api/v2/speech" \
  -H "Authorization: Bearer $METKURD_API_KEY" \
  -H "Idempotency-Key: $METKURD_IDEMPOTENCY_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"text": "سڵاو لە مێتکوردەوە", "voice": "VOICE_ID", "model": "2.0", "language": "ckb", "storage_mode": "temporary"}'
```

The first accepted submission returns **202** with a job `id`. It does not wait
for generation to finish. An identical accepted retry returns **200** with the same job.
Save the returned ID and read its status:

```bash
curl --fail-with-body 'https://metkurd.ai/api/v2/jobs/JOB_ID' \
  -H "Authorization: Bearer $METKURD_API_KEY" \
  -H 'Accept: application/json'
```

Poll about every ten seconds; stop at `completed`, `failed`, or `cancelled`.
When completed, inspect `result.files[]`. Use each returned file ID or download URL:

```bash
curl --fail-with-body 'https://metkurd.ai/api/v2/files/FILE_ID/download' \
  -H "Authorization: Bearer $METKURD_API_KEY" \
  --output result.wav
```

`JOB_ID` and `FILE_ID` are placeholders, not usable identifiers.
Every request above, including downloads, requires authentication.

## Postman Quick Start

**[Import the MetKurd API collection](postman/MetKurd-API.postman_collection.json)**
to try all services without writing a client.

1. Import the collection in Postman and set `api_key` in a private local environment.
   Keep `base_url` as `https://metkurd.ai/api/v2`; never share or export your real key.
2. Send **Discovery / Voices → Discover allowed voice IDs**, then copy a returned
   `id` into `voice_id`.
3. Set `idempotency_key` to a new unique value for this logical request. Send
   **Speech / Apollo → Submit speech**. Keep the same key and inputs for retries.
4. The collection captures `job_id`. Send **Jobs → Read job** about every ten seconds
   until `completed`, `failed`, or `cancelled`.
5. On completion, the collection captures the first available `file_id`. Use
   **Files → Download result** with **Send and Download**; Bearer authentication is inherited.

Generation requests can consume API credits. Choose one request at a time; do not
run the whole collection as a retry mechanism. See [Postman instructions](postman/README.md)
for uploads, reusable references and choosing other result files.

## Run a Complete Example

Each example submits speech, prints the job ID, polls, handles terminal failure,
and downloads a result. They can also resume an existing job without submitting again.

| Client | Entry point | Requirements |
| --- | --- | --- |
| cURL | [speech.sh](examples/curl/speech.sh) | Bash, cURL, jq |
| Python | [speech.py](examples/python/speech.py) | Python 3.10+, requests |
| PHP | [speech.php](examples/php/speech.php) | PHP 8.2+, cURL extension |
| Node.js | [speech.mjs](examples/node/speech.mjs) | Node.js 20+, native fetch |
| JavaScript | [server-speech.mjs](examples/javascript/server-speech.mjs) | Trusted server runtime, Node.js 20+ |

See [example setup](examples/README.md). Browser applications should call their own
authenticated backend; never bundle a MetKurd key into frontend code.

## Available Services

| Product | Endpoint | Guide |
| --- | --- | --- |
| Apollo 1.5 / 2.0 | `POST /speech` | [Speech](docs/services/speech.md) |
| Vector 1.5 / 2.0 | `POST /voice-clone` | [Voice clone](docs/services/voice-clone.md) |
| Zeta 1.0 | `POST /zeta` | [Multi-speaker](docs/services/multi-speaker.md) |
| Theta 1.0 | `POST /theta` | [Multi-speaker](docs/services/multi-speaker.md) |
| Leo | `POST /transcriptions` | [Speech-to-text](docs/services/speech-to-text.md) |
| Caption | `POST /captions` | [Caption](docs/services/caption.md) |
| OCR Scanner | `POST /ocr` | [OCR](docs/services/ocr.md) |
| Harakat 1.0 | `POST /harakat` | [Harakat](docs/services/harakat.md) |
| STEM 2 / 4 | `POST /stem` | [STEM](docs/services/stem.md) |

Discovery: `GET /services`, `GET /voices`. Reusable references: `POST /references`.
Jobs: `GET /jobs/{id}`. Results: `GET /files/{id}/download`.
Service discovery lists the API catalog; it is not a promise that your plan can use every service.

## API Rules

- **Authentication:** use `Authorization: Bearer YOUR_API_KEY` on every endpoint.
- **Idempotency:** generation POSTs require a unique `Idempotency-Key` per logical
  request. Reuse the same key and exact inputs for retries. Changed input returns
  `409 idempotency_conflict`. Do not blindly resubmit under a new key after a timeout.
- **Async lifecycle:** submit → job ID → read status → `completed` → `result.files[]`
  → authenticated download. Reads use MetKurd persisted state.
- **Retention:** `storage_mode` defaults to `temporary`; `permanent` is explicit and
  uses storage quota. Trust returned `expires_at`, not a hardcoded duration.
- **Errors:** handle HTTP errors and failed jobs separately. Respect `Retry-After`
  when present, and back off on 429 responses.

## Documentation

[Getting started](docs/getting-started.md) · [Authentication](docs/authentication.md) ·
[Idempotency](docs/idempotency.md) · [Job lifecycle](docs/job-lifecycle.md) ·
[Downloads](docs/files-and-downloads.md) · [Storage](docs/storage-and-retention.md) ·
[Errors](docs/errors.md) · [Voices](docs/voices.md) · [Contract notes](docs/contract-notes.md)

- [OpenAPI 3.1 specification](openapi.yaml): all 14 public REST V2 operations.
- [Postman collection](postman/MetKurd-API.postman_collection.json) and [instructions](postman/README.md).
- [AGENTS.md](AGENTS.md) and [llms.txt](llms.txt): coding-agent entry points.
- [Security](SECURITY.md), [contributing](CONTRIBUTING.md), [changelog](CHANGELOG.md).

This repository documents MetKurd REST API V2 and provides plain examples; there is
no published SDK package. See [validation](docs/validation.md) for repository checks.

## License

Repository documentation and sample code are licensed under [Apache-2.0](LICENSE).
This license does not cover the hosted MetKurd API service, models, customer data
or generated outputs; their applicable terms remain separate.
