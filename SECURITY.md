# Security

- Never publish API keys, including in issues, screenshots, Postman exports or logs.
- Rotate compromised keys through the MetKurd developer/API portal; revoke the old key.
- Send keys only in the Authorization header, never in query strings.
- Use HTTPS only and keep keys on a trusted server.
- Browser applications should use their own authenticated backend, which must enforce
  authorization and rate limits before making paid requests.
- Authenticate downloads. Do not forward a key to an untrusted origin or follow
  arbitrary redirects with credentials. Treat generated content as untrusted input.

## Responsible Disclosure

Report security vulnerabilities privately to **security@metkurd.ai**.
This address is for vulnerability and security reports. Keep normal API/developer
support requests separate from private security reporting.

Do not post API keys, customer data, vulnerability details, logs or sensitive
reproduction information in public GitHub issues.

Include enough sanitized technical detail in your private report to reproduce the
issue: the affected API endpoint or component, relevant client versions, reproduction
steps, expected and observed behavior, and the potential security impact. Remove
credentials, personal information and customer data from examples and diagnostic
material before sending them. Use synthetic inputs where possible.
