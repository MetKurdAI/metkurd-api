# Multi-Speaker / Zeta and Theta

Zeta uses built-in voices (`POST /zeta`, scope `v2:speech`). Theta uses saved voice
references (`POST /theta`, scope `v2:voice-clone`). Both accept JSON with only
`segments` and optional `storage_mode` (temporary by default, or permanent).
They each produce one combined final audio, not separate public jobs per segment.

## Segments

`segments` is a required nonempty ordered list. Each segment has:

| Field | Required | Contract |
| --- | --- | --- |
| text | yes | Nonempty trimmed string |
| language | yes | ckb, ar or en |
| pause_after_ms | yes | Integer 0, 500, 1000 or 2000 |
| voice | Zeta only | Allowed voice ID from GET /voices |
| reference_id | Theta only | Positive integer ID from an available owned reference |
| reference_text | Theta, optional | Nullable transcript, maximum 4000 characters |

No other segment fields are accepted. The final pause is always normalized to 0,
even when another permitted pause was supplied. Do not send top-level model,
language or processing options. Limits are returned at `GET /services` in
`service_details.zeta.limits` and `.theta.limits`: maximum segments, characters per
segment and total characters. Theta also reports per-reference and project byte limits.
Project reference bytes count distinct stored references; all must remain available.

## Submit Zeta

Discover real voice IDs and replace both placeholders:

```bash
curl --fail-with-body -X POST "https://metkurd.ai/api/v2/zeta" \
  -H "Authorization: Bearer $METKURD_API_KEY" \
  -H "Idempotency-Key: $METKURD_IDEMPOTENCY_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"segments": [{"text": "سڵاو", "voice": "VOICE_ID", "language": "ckb", "pause_after_ms": 500}, {"text": "بەخێربێن", "voice": "ANOTHER_VOICE_ID", "language": "ckb", "pause_after_ms": 0}], "storage_mode": "temporary"}'
```

## Upload a Reference

```bash
curl --fail-with-body -X POST 'https://metkurd.ai/api/v2/references' \
  -H "Authorization: Bearer $METKURD_API_KEY" \
  -H 'Accept: application/json' \
  -F 'file=@./reference.wav'
```

Only `file` is accepted. Maximum 20 MiB; WAV, MP3, MP4/M4A, AAC, OGG or WebM audio,
with valid positive duration. FLAC is excluded. This operation requires Theta
entitlement as well as clone scope, returns **201**, and does not create a generation
job or require Idempotency-Key. Its response contains positive integer `reference_id`,
`mime_type`, `size_bytes`, and nullable `expires_at`. Identical available owned bytes
may reuse an existing reference. References have independent storage policy and use quota.

## Submit Theta

In this example `123` is a **synthetic placeholder** for the actual integer
`reference_id` returned by your upload; replace it before submitting.
Use a new generation idempotency key for this logical job.

```bash
curl --fail-with-body -X POST "https://metkurd.ai/api/v2/theta" \
  -H "Authorization: Bearer $METKURD_API_KEY" \
  -H "Idempotency-Key: $METKURD_IDEMPOTENCY_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"segments": [{"text": "سڵاو", "reference_id": 123, "language": "ckb", "pause_after_ms": 0}], "storage_mode": "temporary"}'
```

Reference audio uses at most its first 20 seconds. A reference may be reused in
multiple segments. Completed Zeta/Theta results include `files`, `segment_count`,
`total_chars`, and `duration` in seconds. Follow the standard [job lifecycle](../job-lifecycle.md)
and [authenticated download](../files-and-downloads.md) flow.
