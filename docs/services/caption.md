# Caption

`POST /captions` accepts multipart. Scope: `v2:captions`.

| Field | Required | Contract |
| --- | --- | --- |
| file | yes | Local audio bytes, maximum 100 MiB |
| language | no | `ckb`, `ar`, `en`; default `ckb` |
| intelligent | no | Boolean; multipart `0` or `1`, default false |
| storage_mode | no | `temporary` (default) or `permanent` |

Audio formats and validation match [Leo](speech-to-text.md). Caption returns `text`,
nullable `srt`, `segments`, and available files. Segments expose start/end/text where
present. Current caption settings use SRT and segments, up to 8 words, maximum
6 seconds and minimum 1 second per caption. These are service settings, not public
request fields. Do not send formatting/segmentation controls that are absent from OpenAPI.

## Submit a Job

Set `METKURD_API_KEY` and a new `METKURD_IDEMPOTENCY_KEY` locally as in the
[quick start](../../README.md#quick-start). Use your own permitted input files.

```bash
curl --fail-with-body -X POST "https://metkurd.ai/api/v2/captions" \
  -H "Authorization: Bearer $METKURD_API_KEY" \
  -H "Idempotency-Key: $METKURD_IDEMPOTENCY_KEY" \
  -H "Accept: application/json" \
  -F 'file=@./audio.wav' \
  -F 'language=ckb' \
  -F 'intelligent=0' \
  -F 'storage_mode=temporary'
```

## Read and Download

Save the returned `id`, then follow the [job lifecycle](../job-lifecycle.md) and
[authenticated downloads](../files-and-downloads.md). The same input/key can be retried
without creating a second accepted job; see [idempotency](../idempotency.md).
Recommended functional fields are defined in [OpenAPI](../../openapi.yaml).
See [contract notes](../contract-notes.md#compatibility-observations) for compatibility behavior.
