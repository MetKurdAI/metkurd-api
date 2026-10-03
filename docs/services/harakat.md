# Harakat 1.0

`POST /harakat` accepts JSON. Scope: `v2:harakat`.

| Field | Required | Contract |
| --- | --- | --- |
| text | yes | Nonempty UTF-8 text after whitespace trimming |
| storage_mode | no | temporary (default) or permanent |

No other fields are accepted. This is direct-text diacritization, not a file upload.
Mixed/non-Arabic characters are accepted rather than removed by input validation.
Discover the current maximum text length at `GET /services` →
`service_details.harakat.limits.max_chars`.

Completed results include a TXT file and `text`, `characters`, `words`, `lines`,
`chunks`. These text/count fields are present only while result files remain available.

## Submit a Job

Set `METKURD_API_KEY` and a new `METKURD_IDEMPOTENCY_KEY` locally as in the
[quick start](../../README.md#quick-start). Use your own permitted input files.

```bash
curl --fail-with-body -X POST "https://metkurd.ai/api/v2/harakat" \
  -H "Authorization: Bearer $METKURD_API_KEY" \
  -H "Idempotency-Key: $METKURD_IDEMPOTENCY_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"text": "مرحبا بكم", "storage_mode": "temporary"}'
```

## Read and Download

Save the returned `id`, then follow the [job lifecycle](../job-lifecycle.md) and
[authenticated downloads](../files-and-downloads.md). The same input/key can be retried
without creating a second accepted job; see [idempotency](../idempotency.md).
Recommended functional fields are defined in [OpenAPI](../../openapi.yaml).
See [contract notes](../contract-notes.md#compatibility-observations) for compatibility behavior.
