# STEM 2 and STEM 4

`POST /stem` accepts multipart. Scope: `v2:stem`.

| Field | Required | Contract |
| --- | --- | --- |
| file | yes | Local audio bytes, maximum 100 MiB |
| mode | yes | 2 or 4; use multipart strings `2` / `4` |
| storage_mode | no | temporary (default) or permanent |

Mode 2 separates vocals and accompaniment. Mode 4 separates vocals, drums, bass
and other audio. Audio formats and server duration checks match [Leo](speech-to-text.md).
There is no default mode. Inspect returned `result.files` for available tracks and
ZIP artifacts; do not assume a fixed file order or construct track URLs.

## Submit a Job

Set `METKURD_API_KEY` and a new `METKURD_IDEMPOTENCY_KEY` locally as in the
[quick start](../../README.md#quick-start). Use your own permitted input files.

```bash
curl --fail-with-body -X POST "https://metkurd.ai/api/v2/stem" \
  -H "Authorization: Bearer $METKURD_API_KEY" \
  -H "Idempotency-Key: $METKURD_IDEMPOTENCY_KEY" \
  -H "Accept: application/json" \
  -F 'file=@./audio.wav' \
  -F 'mode=2' \
  -F 'storage_mode=temporary'
```

## Read and Download

Save the returned `id`, then follow the [job lifecycle](../job-lifecycle.md) and
[authenticated downloads](../files-and-downloads.md). The same input/key can be retried
without creating a second accepted job; see [idempotency](../idempotency.md).
Recommended functional fields are defined in [OpenAPI](../../openapi.yaml).
See [contract notes](../contract-notes.md#compatibility-observations) for compatibility behavior.
