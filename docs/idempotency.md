# Idempotency

All nine generation POST endpoints require `Idempotency-Key`. The value is trimmed,
must be nonempty, and must be at most 128 bytes. Use ASCII values for portability.
A UUID such as `00000000-0000-4000-8000-000000000001` illustrates the format;
generate your own unique value rather than copying this example. UUID format is not required.

## New Requests and Retries

1. Choose and persist a new unique key before starting a new logical request.
2. Save the endpoint and exact request fields and file bytes with that key.
3. Submit once. Save the returned job ID and poll it.
4. If the response is lost, retry the same endpoint/input/key. Do not rotate the key
   just because an HTTP timeout occurred.

An accepted identical replay returns HTTP **200**, the same job ID and its current
state. A newly accepted request returns **202**. Changing the endpoint, fields, their
types, segment order or uploaded bytes under an existing key can return
**409 `idempotency_conflict`**. The key is scoped to the account across API keys and
endpoints, not just one credential or service.

The comparison is not a semantic equivalence guarantee. Preserve optional fields,
whitespace and multipart encodings between retries. For example, adding an explicit
default model after first omitting it may conflict. JSON object-key order is not
significant for multi-speaker segments, but segment-list order is significant.

A retry can return a failed job if that logical request has already failed. Do not
expect the same key to start a replacement generation. Decide deliberately whether
a new job is appropriate after inspecting the terminal error.

## Ambiguous Outcomes

A network error or HTTP 5xx does not prove that a job was never accepted. Keep the
original key and input. If a job ID is known, read it. A long-running `processing`
status is not an instruction to submit a second paid request. The examples stop
after a bounded polling window and print how to resume; they do not cancel the job.

Reads and downloads need no Idempotency-Key. `POST /references` is also an exception:
it returns 201 reference metadata directly and does not use generation idempotency.
The server may reuse an available owned reference for identical bytes; this is not
a general retry-key contract. No public idempotency-expiration duration is promised.
