# Contributing

Contributions should improve documentation accuracy or plain examples. Report
incorrect fields, unclear behavior and reproducible example problems. Describe
the expected and observed behavior with sanitized requests, HTTP status and public
error codes. Remove keys, personal content and real job/file identifiers.

Never include secrets, test keys, production/customer data or service implementation
code. Do not invent endpoints or widen the contract based on assumptions.
Keep OpenAPI, Postman, service guides and agent instructions consistent.

Run the offline checks in [validation](docs/validation.md). Real API calls may consume
credits; they are not part of the local validation suite. Maintainers must confirm
contract changes before merging. See [security](SECURITY.md) for sensitive reports.

Repository documentation and sample code are licensed under [Apache-2.0](LICENSE).
Contributions are made under that license. It does not cover the hosted MetKurd API
service, models, customer data or generated outputs; their applicable terms remain separate.
