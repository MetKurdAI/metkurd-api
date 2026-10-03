# Files and Downloads

## Result Files

Read the completed job's `result.files[]`; never guess a filename or file ID.

| Field | Meaning |
| --- | --- |
| `id` | Public API file identifier, an opaque string |
| `kind` | Result role label; not a closed enum |
| `mime_type` | Reported media type |
| `size_bytes` | Reported byte size |
| `expires_at` | Expiry timestamp or null |
| `download_url` | Authenticated API download URL |

Synthetic shape example:

```json
{"id":"FILE_ID","kind":"render","mime_type":"audio/wav","size_bytes":96044,"expires_at":null,"download_url":"https://metkurd.ai/api/v2/files/FILE_ID/download"}
```

File IDs are different from reusable reference IDs. File ordering and exact kinds
are not guaranteed; inspect metadata and choose the artifact your application needs.
Caption, OCR and STEM can produce multiple artifacts. Only returned files are available.

## Download a Result

```bash
curl --fail-with-body 'https://metkurd.ai/api/v2/files/FILE_ID/download' \
  -H "Authorization: Bearer $METKURD_API_KEY" \
  --output result.wav
```

The endpoint streams bytes and sets the file media type. Authentication, current
API access, download scope, ownership and file availability are all checked.
Missing, expired, deleted or inaccessible files return `404 file_not_found`.
Responses use private/no-store caching. Download before expiration.

For Python streaming, see [speech.py](../examples/python/speech.py), which uses
`stream=True` and writes chunks. For Node, see [speech.mjs](../examples/node/speech.mjs),
which pipes the native fetch response to a file. Both build the documented download
endpoint from the returned public ID, keeping credentials on the canonical API origin.

When using `download_url` directly, validate that it is HTTPS on the expected MetKurd
origin before attaching your key. Do not forward credentials to arbitrary URLs or
redirect targets. Do not expose protected URLs as if they were unauthenticated media links.
