# Voice Clone / Vector

`POST /voice-clone` uses scope `v2:voice-clone`.
Upload a local reference with multipart, or send JSON with an owned `reference_id`.
Provide **exactly one** of `file` or `reference_id`.

| Field | Required | Contract |
| --- | --- | --- |
| text | yes | Nonempty trimmed text, account/service character limit |
| file | conditional | Uploaded reference audio, maximum 20 MiB |
| reference_id | conditional | Positive integer ID of an active owned reusable reference |
| reference_text | no | Reference transcript, nullable, maximum 4000 characters |
| model | no | String `1.5` or `2.0`; default `2.0` |
| language | no | `ckb`, `ar`, `en`; default `ckb` |
| storage_mode | no | `temporary` (default) or `permanent` |

Reference audio supports WAV, MP3, MP4/M4A, AAC, OGG and WebM audio; FLAC is excluded.
The server checks media content and duration. At most the first 20 seconds are used
as voice reference. An existing reference must remain owned, active, present and unexpired.
Use audio you have permission to use.

For reusable uploads see [multi-speaker](multi-speaker.md#upload-a-reference).
That upload route additionally requires Theta entitlement. Returned results are audio files.

## Submit a Job

Set `METKURD_API_KEY` and a new `METKURD_IDEMPOTENCY_KEY` locally as in the
[quick start](../../README.md#quick-start). Use your own permitted input files.

```bash
curl --fail-with-body -X POST "https://metkurd.ai/api/v2/voice-clone" \
  -H "Authorization: Bearer $METKURD_API_KEY" \
  -H "Idempotency-Key: $METKURD_IDEMPOTENCY_KEY" \
  -H "Accept: application/json" \
  -F 'file=@./reference.wav' \
  -F 'text=سڵاو لە مێتکوردەوە' \
  -F 'model=2.0' \
  -F 'language=ckb' \
  -F 'storage_mode=temporary'
```

## Read and Download

Save the returned `id`, then follow the [job lifecycle](../job-lifecycle.md) and
[authenticated downloads](../files-and-downloads.md). The same input/key can be retried
without creating a second accepted job; see [idempotency](../idempotency.md).
Recommended functional fields are defined in [OpenAPI](../../openapi.yaml).
See [contract notes](../contract-notes.md#compatibility-observations) for compatibility behavior.
