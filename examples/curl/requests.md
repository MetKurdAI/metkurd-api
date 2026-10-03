# Service Requests

Set `METKURD_API_KEY` and a new `METKURD_IDEMPOTENCY_KEY` as in
[example setup](../README.md). Replace voice placeholders and the synthetic
Theta reference ID 123 using discovery/upload responses. Provide your own input files.

## speech

```bash
curl --fail-with-body -X POST "https://metkurd.ai/api/v2/speech" \
  -H "Authorization: Bearer $METKURD_API_KEY" \
  -H "Idempotency-Key: $METKURD_IDEMPOTENCY_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"text": "سڵاو لە مێتکوردەوە", "voice": "VOICE_ID", "model": "2.0", "language": "ckb", "storage_mode": "temporary"}'
```

## voice-clone

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

## transcriptions

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

## captions

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

## ocr

```bash
curl --fail-with-body -X POST "https://metkurd.ai/api/v2/ocr" \
  -H "Authorization: Bearer $METKURD_API_KEY" \
  -H "Idempotency-Key: $METKURD_IDEMPOTENCY_KEY" \
  -H "Accept: application/json" \
  -F 'file=@./document.pdf' \
  -F 'pages=1' \
  -F 'exports[]=txt' \
  -F 'exports[]=docx' \
  -F 'intelligent=0' \
  -F 'storage_mode=temporary'
```

## stem

```bash
curl --fail-with-body -X POST "https://metkurd.ai/api/v2/stem" \
  -H "Authorization: Bearer $METKURD_API_KEY" \
  -H "Idempotency-Key: $METKURD_IDEMPOTENCY_KEY" \
  -H "Accept: application/json" \
  -F 'file=@./audio.wav' \
  -F 'mode=2' \
  -F 'storage_mode=temporary'
```

## zeta

```bash
curl --fail-with-body -X POST "https://metkurd.ai/api/v2/zeta" \
  -H "Authorization: Bearer $METKURD_API_KEY" \
  -H "Idempotency-Key: $METKURD_IDEMPOTENCY_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"segments": [{"text": "سڵاو", "voice": "VOICE_ID", "language": "ckb", "pause_after_ms": 500}, {"text": "بەخێربێن", "voice": "ANOTHER_VOICE_ID", "language": "ckb", "pause_after_ms": 0}], "storage_mode": "temporary"}'
```

## theta

```bash
curl --fail-with-body -X POST "https://metkurd.ai/api/v2/theta" \
  -H "Authorization: Bearer $METKURD_API_KEY" \
  -H "Idempotency-Key: $METKURD_IDEMPOTENCY_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"segments": [{"text": "سڵاو", "reference_id": 123, "language": "ckb", "pause_after_ms": 0}], "storage_mode": "temporary"}'
```

## harakat

```bash
curl --fail-with-body -X POST "https://metkurd.ai/api/v2/harakat" \
  -H "Authorization: Bearer $METKURD_API_KEY" \
  -H "Idempotency-Key: $METKURD_IDEMPOTENCY_KEY" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"text": "مرحبا بكم", "storage_mode": "temporary"}'
```

Use `mode=4` for STEM 4. Follow [job lifecycle](../../docs/job-lifecycle.md) after submission.
For reusable reference uploads see [multi-speaker](../../docs/services/multi-speaker.md).
