# Speech-to-Text / Leo

`POST /transcriptions` accepts multipart. Scope: `v2:transcriptions`.

| Field | Required | Contract |
| --- | --- | --- |
| file | yes | Local audio bytes, maximum 100 MiB |
| language | no | `ckb`, `ar`, `en`; default `ckb` |
| intelligent | no | Boolean; multipart `0` or `1`, default false |
| storage_mode | no | `temporary` (default) or `permanent` |

Supported audio: WAV, MP3, MP4/M4A, AAC, OGG, WebM and FLAC. Valid positive duration
is checked by the server; do not submit your own duration or minute count.
Completed results contain `text` and available transcript files.

## Submit a Job

Set `METKURD_API_KEY` and a new `METKURD_IDEMPOTENCY_KEY` locally as in the
[quick start](../../README.md#quick-start). Use your own permitted input files.

```bash
curl --fail-with-body -X POST "https://metkurd.ai/api/v2/transcriptions" \
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
