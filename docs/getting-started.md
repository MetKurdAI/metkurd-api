# Getting Started

## Requirements

Create an account at [MetKurd AI](https://metkurd.ai), select an eligible active plan
with API access, and create a key in the signed-in developer/API portal. Confirm
service permissions and API credits there. Website credits and API credits are separate.
Current pricing and access are maintained in the live website/portal, not this repository.

## First Request

Follow the [README quick start](../README.md#quick-start), or run a complete
[example](../examples/README.md). Discover a permitted voice with `GET /voices`.
Use the exact returned `id` for `voice`; do not use its display name.

For a new logical request, choose and save a unique idempotency key. Store credentials
locally in environment variables or your secret manager, outside version control.
Submit to `https://metkurd.ai/api/v2/speech`. Save the job `id` before polling.
Generation POSTs can consume API credits. Discovery and status reads do not create jobs.

## Check Job Status

Read `GET /jobs/{id}` about every ten seconds. Both 202 submissions and 200 reads/replays
use the same [job envelope](job-lifecycle.md). Status may already be terminal when read.
Stop on completed, failed or cancelled. Download available files before their expiry.

## Next Steps

- [Import Postman](../postman/README.md) for all services.
- Use [OpenAPI](../openapi.yaml) for exact fields and response shapes.
- Read [idempotency](idempotency.md) before adding automated retries.
- Handle [errors](errors.md) and [retention](storage-and-retention.md).

Examples use Bash syntax where shell commands are shown. In Windows PowerShell,
invoke `curl.exe` and adapt line continuation/quoting, or use Python, PHP, or Node.
There is no API V2 account-creation, key-creation, usage, job-list, delete, cancellation,
or webhook-management endpoint in this documented surface.
