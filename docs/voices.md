# Voice Discovery

```bash
curl --fail-with-body 'https://metkurd.ai/api/v2/voices' \
  -H "Authorization: Bearer $METKURD_API_KEY" \
  -H 'Accept: application/json'
```

This authenticated read requires `v2:speech` and current API access. It requires
no idempotency key and creates no job. It returns:

```json
{"voices":[{"id":"VOICE_ID","name":"Voice Name"}]}
```

The shown ID/name are placeholders. Use actual returned `id` strings for Apollo's
`voice` and Zeta's segment `voice`. Do not use names or guess speaker identifiers.
The result is scoped to your account's available voices; an empty catalog is
`{"voices":[]}`. Access can change with your plan or voice availability, so refresh
discovery when a previously accepted voice is rejected. No public voice preview or
voice-upload endpoint is included in this REST V2 surface.
