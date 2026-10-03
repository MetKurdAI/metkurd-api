# Storage and Retention

All generation services accept optional `storage_mode`:

| Mode | Behavior |
| --- | --- |
| `temporary` (default) | Results expire according to API retention policy; temporary API files do not consume permanent storage quota |
| `permanent` | Results use permanent storage behavior and quota; this is not a guarantee of indefinite availability |

Use each job and file's returned `expires_at`. Temporary job retention starts at
submission, so processing time can consume part of the available window. No fixed
global duration is promised here. A null expiry means no scheduled expiry is reported,
not immunity from deletion, account restrictions or other storage policies.

Active owned API result files may also appear in V2 My Storage with API and retention
labels. Temporary upload/staging inputs are not customer result files and do not
appear in `result.files[]`. Expired/deleted files are unavailable even before physical cleanup.

When the job expiry is reached, a completed result becomes
`{"expired":true,"files":[]}`. Files can also expire individually or become unavailable
earlier; always check the returned list and download response. Harakat inline text and
counts are omitted if no result files remain. Do not rely on inline text as a retention bypass.

## Reusable References

`POST /references` accepts only `file`, not `storage_mode`. Saved references follow
their own storage policy, currently count toward permanent quota, and return their own
nullable `expires_at`. A later temporary Theta/Vector job does not change that policy.
This differs from uploading a reference directly as part of a temporary Vector job.
See [multi-speaker](services/multi-speaker.md) for reference upload details.
