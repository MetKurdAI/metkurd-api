# Contract Notes

This repository describes MetKurd REST API V2. Account/service availability, limits
and entitlements are determined by your current MetKurd account and plan. See the
developer/API portal for account details and [validation](validation.md) for repository checks.

## Client-Relevant Caveats

- Discovery describes the catalog, not your exact service entitlements or pricing.
  Multi-speaker and Harakat limits are exposed through `GET /services`; use returned
  limits rather than assuming deployment-specific values remain fixed.
- Apollo/Vector text limits depend on account/service permissions and are not
  exposed by that discovery response. Check the portal and handle text validation errors.
- Primary OpenAPI request schemas expose recommended functional fields. The
  compatibility observations below do not add fields to the recommended contract
  or change server validation. Existing permissive schemas remain permissive;
  Zeta/Theta/Harakat and reference uploads reject unknown input fields.
- Boolean JSON values and multipart `0`/`1` are supported. The strings `true`/`false`
  are not accepted boolean encodings. Use model strings `"1.5"`/`"2.0"`, not numbers.
- OCR arrays must use multipart names `exports[]` or `exports[0]`, `exports[1]`.
  A generic OpenAPI client's repeated `exports` field may not bind correctly. Follow
  the cURL/Postman examples. An explicitly empty exports array is not equivalent
  to omitting it; only omission selects the default TXT/DOCX request.
- Reference uploads require Theta entitlement in addition to clone scope. Their
  storage policy is independent of generation storage_mode and uses quota.
- Reference IDs are positive integers; job/file/voice IDs are strings. Do not
  interchange these identifiers or invent IDs to satisfy an example.
- File `kind` is descriptive, not a stable closed enum. Not every completed job
  necessarily has downloadable files at the time you read it.
- Failed-job errors differ from HTTP errors. Expiry is represented in `result`,
  not by an `expired` job status. Harakat metadata requires available files.
- Rate-limit responses carry Retry-After; concurrency-limit responses may not.
  A generic client must also tolerate non-JSON transport/gateway errors.
- Caption segments expose only available start/end/text fields. Presence and value
  types are not normalized by the public response boundary; clients should parse
  them defensively and not depend on unlisted metadata.

## Repository License and Security Reporting

Report vulnerabilities privately through the confirmed channel in
[SECURITY.md](../SECURITY.md). Keep normal API/developer support separate from
security reporting. Repository documentation and sample code are licensed
under [Apache-2.0](../LICENSE). This license does not cover the hosted MetKurd API
service, models, customer data or generated outputs.

## Compatibility Observations

The following accepted fields have no processing effect on these endpoints and
are omitted from the primary request schemas:

| Endpoint | No-op fields |
| --- | --- |
| `/speech` | `intelligent`, `reference_id`, `reference_text` |
| `/voice-clone` | `intelligent`, `voice` |
| `/ocr` | `language` |
| `/stem` | `language`, `intelligent` |

They can still participate in request validation and idempotency comparison. Omit
them from new integrations, but preserve the exact original fields when retrying an
existing logical request. Removing a no-op field during a retry can cause a conflict.
Other unrecognized fields can be ignored by these older endpoints; that is not a
promise of functionality or permission to supply undocumented processing options.

Numeric `1.5` is accepted by the existing model handling, but numeric `2.0` loses
its decimal representation and is not a valid model. The canonical OpenAPI contract
therefore uses only the string values `"1.5"` and `"2.0"` for Apollo and Vector.
This is a documentation simplification; backend acceptance has not changed.
