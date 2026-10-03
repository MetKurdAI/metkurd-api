# Offline Validation

These checks validate repository artifacts and mocked client behavior. They do not
contact the MetKurd API, create paid jobs or demonstrate live service availability.

From the repository root, with Python 3.10+, Node.js 20+, PHP 8.2+ and Bash available:

```bash
python -m pip install -r scripts/requirements.txt
python scripts/validate.py
python -B -m unittest discover -s tests -p 'test_*.py'
node --test tests/javascript.test.mjs
node --check examples/node/speech.mjs
node --check examples/javascript/server-speech.mjs
node --check examples/javascript/workflow.mjs
php -l examples/php/speech.php
bash -n examples/curl/speech.sh
```

The validator checks OpenAPI 3.1 with openapi-spec-validator, local schema references,
schema examples, all 14 expected operations, Postman JSON and operation/request-schema
coverage, Python syntax, local Markdown links/anchors and sensitive-data patterns.
No network schema resolution is needed. Dependencies must already be installed for
the offline check itself; dependency installation is a separate network operation.

Mock tests cover submit/read/streamed download, resume without submission, rate-limit
backoff, terminal failures/cancellation, expiration, bounded polling, lost submission
response and idempotency conflict. Synthetic placeholders are never sent to an API.
PHP and Bash receive syntax checks; these checks do not exercise their HTTP runtimes.

## Initial Verification — 2026-10-03

- OpenAPI 3.1 schema, local references and 31 request/response examples: passed.
- All 14 operations and 16 Postman requests: passed; the collection also passed
  the official Postman v2.1 JSON Schema. All 24 embedded scripts passed syntax checks.
- Python: 8 offline lifecycle tests passed. JavaScript: 10 offline lifecycle tests passed.
- Python, PHP, JavaScript and Bash example syntax checks: passed.
- 121 local Markdown links/anchors: passed. External destinations were not tested.
- Sensitive-data patterns and a manual public-content review: no secrets, private
  implementation content, development paths or infrastructure identifiers found.

This is local artifact verification, not production or interactive Postman acceptance.

## Public-Release Cleanup Verification — 2026-10-03

- Standard Apache-2.0 LICENSE downloaded unchanged from the Apache Software Foundation;
  pending-license references removed and repository-only scope documented.
- OpenAPI 3.1, all 14 operations and 31 schema examples: passed. Canonical request
  field sets and string-only model values were checked separately.
- Official Postman v2.1 schema, 16 requests and 24 embedded script syntax checks:
  passed. An isolated script harness passed 84 scenarios for idempotency setup,
  job/file capture, reference capture, expired results and unsuccessful responses.
- All 8 Python and 10 JavaScript offline lifecycle tests passed again.
- Python, PHP, Node.js, JavaScript and Bash example syntax passed, including
  29 Markdown shell snippets. PHP/Bash HTTP execution remains outside these checks.
- All 136 local Markdown links/anchors passed. External destinations were not tested.
- Secret, private-path, production-shaped identifier and infrastructure-identifier
  scans found no matches. Example IDs remain clearly marked synthetic placeholders.
- Security guidance remained intact during license/schema cleanup; the confirmed
  reporting channel is documented in the subsequent contact update. No production
  API requests, backend changes, Git initialization or push were performed.

## Security Contact Verification — 2026-10-03

- Confirmed private vulnerability reporting is documented in SECURITY.md, with
  sanitized reproduction guidance and a clear separation from normal developer support.
- Obsolete security-contact placeholders and pending-channel statements were removed.
- OpenAPI 3.1, all 14 operations and 31 schema examples passed again.
- The 16-request Postman collection passed its official schema; all 24 embedded
  scripts passed syntax checks and 84 offline script scenarios passed.
- All 8 Python and 10 JavaScript lifecycle tests passed. Python, PHP, Node.js,
  JavaScript and Bash syntax checks passed, including 29 Markdown shell snippets.
- All 136 local Markdown links/anchors passed.
- Secret, private/local-path, production-shaped ID and infrastructure-identifier
  scans found no matches. Explicit obsolete license-placeholder and security-contact
  checks also found no matches. No outstanding security contact decision remains.
- No production access, private-application changes, deployment, Git initialization,
  GitHub repository creation or push was performed.

After future edits, maintainers should revalidate the collection against the
official Postman v2.1 schema and review the public/private boundary. Keep vulnerability
reporting guidance consistent with SECURITY.md. Pattern scans reduce risk but cannot
prove that every possible secret has been detected. External links are not fetched
by the validator. Live processing and interactive Postman acceptance are separate.
