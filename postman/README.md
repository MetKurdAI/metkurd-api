# Postman

Import [MetKurd-API.postman_collection.json](MetKurd-API.postman_collection.json).
Use a private local environment or local variable values for credentials; do not
sync/share/export a real key with this collection.

1. Set `api_key` locally. `base_url` is `https://metkurd.ai/api/v2`.
2. Run Getting Started → Discover services, then Discovery / Voices. Copy an allowed
   ID into `voice_id`; discovery does not choose a voice on your behalf.
3. Set `idempotency_key` to a new unique value before your new logical job. Keep that
   same value and exact request for retries. The collection deliberately does not
   generate a fresh key on every Send. A pre-request check rejects the placeholder.
4. Choose one service request, supply your own files where required, and Send.
5. The response script captures `job_id` from successful submission/replay responses.
6. Read Jobs → Read job about every ten seconds. Stop at a terminal state. On an
   available completed result the script captures the first `file_id`; inspect the
   response manually to choose another artifact.
7. Files → Download result inherits Bearer authentication. Use Send and Download.

For Theta, first run Multi-Speaker → Upload reusable reference; its response script
sets `reference_id`. This variable starts as `REFERENCE_ID` and must become the actual
returned integer before the raw Theta/saved-clone JSON is valid. Uploads use quota
and require Theta entitlement. No generation key is required for reference uploads.

File selectors are deliberately empty. Do not manually add a multipart Content-Type:
Postman supplies its boundary. OCR uses repeated `exports[]` fields. STEM 2 and
STEM 4 are separate examples of the same endpoint. Apollo/Vector default to 2.0;
change model to string `1.5` only for a new logical request with a new key.

The collection covers all 14 operations with 16 requests, including both STEM modes
and both clone input forms. There is no automatic collection runner, polling loop,
environment export containing secrets, or new-key-per-retry script.
