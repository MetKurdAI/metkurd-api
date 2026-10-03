# MetKurd REST API V2 — Agent Contract

- Canonical structured contract: `openapi.yaml`; explanations: `docs/`.
- Primary request schemas describe recommended functional fields. Compatibility
  observations belong in `docs/contract-notes.md`; do not add no-op fields to examples.
- Send speech/clone model as the string `"1.5"` or `"2.0"`, never a number.
- Base URL: `https://metkurd.ai/api/v2`. No locale prefix.
- An active eligible plan, API access, permitted service scope, and API credits are
  distinct requirements. Never hardcode plan prices or allowances.
- All endpoints require `Authorization: Bearer YOUR_API_KEY`, including discovery,
  job reads and downloads. Never expose keys in frontend bundles, URLs or logs.
- Generation POSTs require `Idempotency-Key`: trimmed nonempty value, at most 128
  bytes. UUIDs are convenient, not required. Identity is account-wide across keys
  and endpoints. Same accepted inputs/key return the same job; changed inputs: 409
  `idempotency_conflict`. Preserve file bytes, field values and types for retries.
- Never blindly resubmit a timed-out paid request with a new key. Save the key
  before submission. Resume with the known job ID; otherwise retry the same inputs/key.
- New accepted job: HTTP 202; accepted replay: HTTP 200. Poll `GET /jobs/{id}`
  about every ten seconds. GET reads persisted state; no provider knowledge is needed.
- Public statuses: queued, processing, completed, failed, cancelled. Stop at a terminal
  state. A local polling timeout does not cancel a job. No public cancellation endpoint.
- On completion inspect `result.expired` and `result.files[]`. Use returned public
  IDs and authenticated `download_url`; never derive storage paths or media URLs.
- `storage_mode`: temporary (default) or permanent. Trust job/file `expires_at`.
  Permanent storage uses quota. An expired completed job has `expired: true` and no files.
- Discover allowed `voice` strings at `GET /voices` (`voices[]`, each with id/name).
  `GET /services` supplies catalog and multi-speaker/Harakat limits, not access grants.
- `POST /references` takes only multipart file, returns 201 with integer reference_id,
  and does not create a generation job or require an idempotency key. Saved references
  use their own storage policy and quota; job storage_mode does not change it.
- Zeta/Theta accept segments and storage_mode only; Harakat accepts text and
  storage_mode only. Never send model/language at the top level for these services.
- Parse `{error: {code, message, fields?}}`; failed jobs carry their own error.
  See `docs/errors.md`. Back off on 429 and respect Retry-After when present.
- Never infer undocumented fields, file-kind enums, numeric IDs, fixed expiration
  durations, direct media links, webhooks, cancellation APIs or official SDK packages.
- Examples are server-side and offline validation must not call the production API.
- Repository documentation and sample code use [Apache-2.0](LICENSE). This license
  does not cover the hosted MetKurd API service, models, customer data or generated outputs.
- Follow [SECURITY.md](SECURITY.md) for private vulnerability reports. Keep normal
  API/developer support separate; never put sensitive security details in public issues.
