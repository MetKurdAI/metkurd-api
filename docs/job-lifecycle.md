# Job Lifecycle

## Submit a Job

Generation is asynchronous:

```text
POST service + Idempotency-Key
  → 202 + job id (200 for accepted replay)
  → GET /jobs/{id}
  → completed
  → result.files[]
  → GET download_url + Bearer authentication
```

POST may spend time validating uploads and accepting work; it does not wait for
generation completion. GET reads MetKurd persisted state. Customers do not need
to query a processing provider. Processing continues without a connected client.

## Check Job Status

| Status | Meaning | Client action |
| --- | --- | --- |
| `queued` | Accepted, waiting for processing | Poll later |
| `processing` | Work is in progress or its outcome is being resolved | Poll later |
| `completed` | Result has been persisted | Inspect result and download available files |
| `failed` | Work ended unsuccessfully | Inspect `error`; stop polling |
| `cancelled` | Work ended without completion | Stop polling |

Poll about every ten seconds, with backoff/jitter as needed. Request limits also
apply to status reads and downloads. Respect `Retry-After` when returned. A local
timeout does not cancel a job. This API surface has no customer cancellation route.

Every submission/replay/read job envelope contains `id`, `status`, `service`,
`created_at`, nullable `completed_at`, nullable `expires_at`, and `result`.
`service` is the route family, e.g. `speech` or `stem`. IDs are opaque strings.
Do not parse IDs to derive storage locations or account information.

Synthetic queued example (all identifiers are placeholders):

```json
{"id":"JOB_ID","status":"queued","service":"speech","created_at":"2026-10-03T12:00:00Z","completed_at":null,"expires_at":"2026-10-04T12:00:00Z","result":null}
```

The dates illustrate shape only; they do not promise a retention duration.
`result` is null before completion and for failed/cancelled jobs. Failed jobs add
`error.code` and `error.message`. HTTP 200 on a read can still contain a failed job.

## Results

All completed results contain `files`, which may be empty. Additional fields:

| Service | Additional result fields |
| --- | --- |
| speech, voice-clone, stem | No additional public fields |
| transcriptions | `text` |
| captions | `text`, nullable `srt`, `segments` containing start/end/text when present |
| ocr | `text` |
| zeta, theta | `segment_count`, `total_chars`, `duration` (seconds) |
| harakat | `text`, `characters`, `words`, `lines`, `chunks`, only while files are available |

When a temporary job has expired, the completed job remains `completed` and its
result becomes `{"expired":true,"files":[]}`. Expiry is not another status.
Never assume completion guarantees that files remain downloadable indefinitely.
See [files](files-and-downloads.md) and [retention](storage-and-retention.md).
