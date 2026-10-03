# Speech / Apollo

`POST /speech` accepts JSON. Scope: `v2:speech`.

| Field | Required | Contract |
| --- | --- | --- |
| text | yes | Nonempty trimmed text; character limit depends on account/service |
| voice | yes | Allowed string ID from GET /voices |
| model | no | String `1.5` or `2.0`; default `2.0` |
| language | no | `ckb`, `ar`, `en`; default `ckb` |
| storage_mode | no | `temporary` (default) or `permanent` |

Returns a job; completed `result.files` contains available audio. Do not hardcode
voice IDs. The examples use a placeholder that must be replaced after discovery.

## Submit a Job

Set `METKURD_API_KEY` and a new `METKURD_IDEMPOTENCY_KEY` locally as in the
[quick start](../../README.md#quick-start). Use your own permitted input files.

```bash
curl --fail-with-body -X POST "https://metkurd.ai/api/v2/speech" \
  -H "Authorization: Bearer $METKURD_API_KEY" \
  -H "Idempotency-Key: $METKURD_IDEMPOTENCY_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"text": "سڵاو لە مێتکوردەوە", "voice": "VOICE_ID", "model": "2.0", "language": "ckb", "storage_mode": "temporary"}'
```

## Read and Download

Save the returned `id`, then follow the [job lifecycle](../job-lifecycle.md) and
[authenticated downloads](../files-and-downloads.md). The same input/key can be retried
without creating a second accepted job; see [idempotency](../idempotency.md).
Recommended functional fields are defined in [OpenAPI](../../openapi.yaml).
See [contract notes](../contract-notes.md#compatibility-observations) for compatibility behavior.
