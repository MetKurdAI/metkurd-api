# OCR Scanner

`POST /ocr` accepts one local PDF/image as multipart `file`. Scope: `v2:ocr`.
You do not need to host a document or supply a URL.

| Field | Required | Contract |
| --- | --- | --- |
| file | yes | PDF/JPG/JPEG/PNG/WebP/BMP/GIF/TIF/TIFF; maximum 100 MiB |
| pages | no | String, max 255 characters; default `all`; e.g. `1-3,5` |
| exports[] | no | Repeated multipart values: txt, docx, markdown, html, zip; omitted default: txt/docx |
| intelligent | no | Boolean correction option; multipart 0/1, default false |
| storage_mode | no | temporary (default) or permanent |

Select 1–20 unique pages. `all` means the first 20 or fewer pages, not necessarily
the entire PDF. A later range such as `21-40` is supported. Ranges are deduplicated
and sorted, and checked against the document when its total is known. An image is
one page. Use valid, unlocked documents. Upload size limits imposed by hosting may be lower.

Allow cURL/the HTTP client to generate multipart boundaries. Use `exports[]` or
indexed `exports[0]`, `exports[1]`, not a JSON string in one multipart field.
Omitting exports selects the defaults; sending an explicit empty array does not.
Only available artifacts are returned. Completion includes `text` and `files`.
A URL-only request fails with `invalid_file`; no public remote-fetch input is supported.

## Submit a Job

Set `METKURD_API_KEY` and a new `METKURD_IDEMPOTENCY_KEY` locally as in the
[quick start](../../README.md#quick-start). Use your own permitted input files.

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

## Read and Download

Save the returned `id`, then follow the [job lifecycle](../job-lifecycle.md) and
[authenticated downloads](../files-and-downloads.md). The same input/key can be retried
without creating a second accepted job; see [idempotency](../idempotency.md).
Recommended functional fields are defined in [OpenAPI](../../openapi.yaml).
See [contract notes](../contract-notes.md#compatibility-observations) for compatibility behavior.
