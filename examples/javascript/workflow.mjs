// Server-side only. Never bundle a secret API key into browser code.
const BASE = 'https://metkurd.ai/api/v2';
const defaultSleep = ms => new Promise(resolve => setTimeout(resolve, ms));

async function checked(response) {
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(`HTTP ${response.status}: ${body.error?.code ?? 'http_error'}. Keep original input/key.`);
  }
  return response;
}

export async function runSpeech({ apiKey, voice, idempotencyKey, jobId, save,
  fetchImpl = globalThis.fetch, sleep = defaultSleep, log = console.log, attempts = 60 }) {
  if (!apiKey || apiKey === 'YOUR_API_KEY') throw new Error('Set METKURD_API_KEY locally.');
  if (typeof save !== 'function') throw new Error('A trusted server download sink is required.');
  if (jobId === 'JOB_ID') throw new Error('Replace METKURD_JOB_ID with the returned job ID.');
  const headers = { Authorization: `Bearer ${apiKey}`, Accept: 'application/json' };
  if (!jobId) {
    if (!voice || voice === 'VOICE_ID') throw new Error('Discover and set METKURD_VOICE_ID.');
    if (!idempotencyKey || idempotencyKey === 'YOUR_UNIQUE_REQUEST_ID') {
      throw new Error('Set and retain METKURD_IDEMPOTENCY_KEY before submitting.');
    }
    // Never automatically change this key after a network failure.
    const response = await checked(await fetchImpl(`${BASE}/speech`, {
      method: 'POST', redirect: 'error', signal: AbortSignal.timeout(90000),
      headers: { ...headers, 'Idempotency-Key': idempotencyKey, 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: 'سڵاو لە مێتکوردەوە', voice, model: '2.0', language: 'ckb', storage_mode: 'temporary' }),
    }));
    jobId = (await response.json()).id;
    if (typeof jobId !== 'string' || !jobId) throw new Error('Missing job ID; preserve original input/key.');
  }
  log(`Job: ${jobId}`);
  for (let attempt = 0; attempt < attempts; attempt++) {
    const response = await fetchImpl(`${BASE}/jobs/${encodeURIComponent(jobId)}`, {
      headers, redirect: 'error', signal: AbortSignal.timeout(30000),
    });
    if (response.status === 429) {
      const retry = response.headers.get('Retry-After');
      await response.body?.cancel();
      await sleep(retry && /^\d+$/.test(retry) ? Math.max(1, Number(retry)) * 1000 : 10000);
      continue;
    }
    const job = await (await checked(response)).json();
    log(`Status: ${job.status}`);
    if (['failed', 'cancelled'].includes(job.status)) {
      throw new Error(`Job ${job.status}: ${job.error?.code ?? job.status}`);
    }
    if (job.status === 'completed') {
      const files = job.result?.files ?? [];
      if (job.result?.expired || !files.length) throw new Error('No available result files; result may have expired.');
      const file = files[0];
      // Returned public ID, fixed origin: never send credentials to an arbitrary URL.
      const result = await checked(await fetchImpl(`${BASE}/files/${encodeURIComponent(file.id)}/download`, {
        headers: { Authorization: headers.Authorization }, redirect: 'error', signal: AbortSignal.timeout(90000),
      }));
      if (!result.body) throw new Error('Missing download body.');
      await save(result.body, file);
      return jobId;
    }
    if (!['queued', 'processing'].includes(job.status)) throw new Error('Unknown status; inspect before continuing.');
    if (attempt + 1 < attempts) await sleep(10000);
  }
  throw new Error(`Polling limit reached. Job still exists; resume with METKURD_JOB_ID=${jobId}.`);
}
