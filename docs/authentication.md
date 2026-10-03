# Authentication

Every endpoint requires `Authorization: Bearer YOUR_API_KEY` over HTTPS. Add
`Accept: application/json` for JSON responses. JSON submissions also use
`Content-Type: application/json`; let your client generate multipart boundaries.

Create and revoke keys in the signed-in MetKurd developer/API portal. Key secrets
are shown once; store them securely. A revoked key or loss of current API access
affects subsequent requests, including job reads and result downloads.

## Scopes and Access

Both the key and current plan must permit the relevant scope. Submission also
requires service entitlement and sufficient API credits. A discovery listing
does not grant permission to generate with a service.

| Operation | Required scope |
| --- | --- |
| GET /services, GET /jobs/{id} | `v2:jobs:read` |
| GET /voices, POST /speech, POST /zeta | `v2:speech` |
| POST /voice-clone, POST /theta, POST /references | `v2:voice-clone` |
| POST /transcriptions | `v2:transcriptions` |
| POST /captions | `v2:captions` |
| POST /ocr | `v2:ocr` |
| POST /harakat | `v2:harakat` |
| POST /stem | `v2:stem` |
| GET /files/{id}/download | `v2:files:download` |

Reference uploads additionally require Theta service entitlement; clone scope alone
does not establish this permission. Check your account's available services in the portal.

## Authenticated Downloads

Downloads are protected API requests, not public links. Opening a download URL
in a browser tab without a Bearer header may return `401 authentication_failed`.
A website session alone is not an API Bearer key. Use a trusted backend to stream
results to an authorized browser user; do not expose the key in frontend code.

Missing/invalid/revoked keys return `authentication_failed`. Permission failures
normally return `permission_denied`. See [errors](errors.md) for other failures.
