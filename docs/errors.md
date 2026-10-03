# Error Handling

HTTP failures return an error object, for example:

```json
{"error":{"code":"invalid_request","message":"Check the supplied fields.","fields":["text"]}}
```

`fields` is an optional list of field names, not a map of validation messages.
Use `code` for branching; do not depend on message text. This API does not use
`validation_failed` or `access_denied` as its normal V2 codes.

| Code | HTTP status / location | Message |
| --- | --- | --- |
| `invalid_request` | 400 / 422; other request statuses possible | Check the supplied fields. |
| `authentication_failed` | 401 | A valid API key is required. |
| `permission_denied` | 403 | This request is not permitted. |
| `insufficient_credits` | 422 or failed job | Insufficient API credits. |
| `rate_limit_exceeded` | 429 | Too many requests. Try again later. |
| `invalid_file` | 422 | The supplied file is invalid. |
| `unsupported_format` | 422 | The file format is not supported. |
| `job_not_found` | 404 | The requested job was not found. |
| `file_not_found` | 404 | The requested file was not found or has expired. |
| `processing_failed` | failed job | Processing failed. |
| `storage_limit_exceeded` | failed job | The storage limit was exceeded. |
| `server_error` | 500 | The request could not be completed. |
| `idempotency_conflict` | 409 | This idempotency key was used for a different request. |
| `concurrency_limit_exceeded` | 429 | The concurrent job limit was reached. |

## Recovery

- **400/422:** fix malformed JSON, required fields, allowed values, file formats or
  account credit problems. Validation can select `invalid_file` or `unsupported_format`.
- **401/403:** check the key, current plan/API access, key scopes and service entitlement.
- **404:** verify ownership and the returned identifier; result files may have expired.
- **409:** stop; the key was used with different input. Restore the original input
  for its retry, or intentionally create a distinct request with a new key.
- **429:** back off. `rate_limit_exceeded` returns `Retry-After`; concurrency responses
  may omit it. Poll outstanding jobs at a modest interval and avoid a retry storm.
- **5xx or lost connection:** keep the same idempotency key and input. If known,
  read the existing job. A failed HTTP exchange does not prove non-acceptance.

`invalid_request` may also carry other framework request statuses, including 404
when the API is unavailable. Gateway/proxy failures can return non-JSON responses;
clients should handle them without logging secrets or repeatedly submitting new jobs.

## Failed Jobs

A job read can be HTTP 200 with `status: "failed"`, `result: null` and `error`.
Its safe public code is `processing_failed`, `storage_limit_exceeded`, or
`insufficient_credits`. Stop polling and inspect the failure. Do not interpret
HTTP success as generation success. Internal stack traces and processing details
are not part of this contract.
