import test from 'node:test';
import assert from 'node:assert/strict';
import { runSpeech } from '../examples/javascript/workflow.mjs';

const json = (body, status = 200, headers = {}) => new Response(JSON.stringify(body), { status, headers });
const complete = () => json({ status: 'completed', result: { files: [{ id: 'FILE_ID' }] } });
function fixture(reads, { resume = false, submitError, submitStatus = 202 } = {}) {
  const calls = [], delays = [], saved = [];
  const options = {
    apiKey: 'UNUSED_PLACEHOLDER', voice: 'DISCOVERED_VOICE_PLACEHOLDER', idempotencyKey: 'REQUEST_PLACEHOLDER',
    jobId: resume ? 'SAVED_JOB_PLACEHOLDER' : undefined, log: () => {},
    sleep: async ms => delays.push(ms),
    save: async body => saved.push(await new Response(body).text()),
    fetchImpl: async (url, init) => {
      calls.push({ url, init });
      if (init.method === 'POST') {
        if (submitError) throw submitError;
        return submitStatus === 409 ? json({ error: { code: 'idempotency_conflict' } }, 409) : json({ id: 'JOB_ID' }, submitStatus);
      }
      if (url.endsWith('/download')) return new Response('SYNTHETIC_AUDIO');
      assert.ok(reads.length, 'Unexpected extra read');
      return reads.shift();
    },
  };
  return { options, calls, delays, saved };
}

test('submit, poll, authenticate and stream without redirects', async () => {
  const f = fixture([json({ status: 'queued' }), json({ status: 'processing' }), complete()]);
  assert.equal(await runSpeech(f.options), 'JOB_ID');
  assert.deepEqual(f.saved, ['SYNTHETIC_AUDIO']);
  assert.equal(f.calls.filter(c => c.init.method === 'POST').length, 1);
  assert.equal(f.calls[0].init.headers['Idempotency-Key'], 'REQUEST_PLACEHOLDER');
  for (const c of f.calls) {
    assert.equal(c.init.headers.Authorization, 'Bearer UNUSED_PLACEHOLDER');
    assert.equal(c.init.redirect, 'error');
    assert.ok(c.url.startsWith('https://metkurd.ai/api/v2/'));
  }
});
test('accepted replay works with HTTP 200', async () => {
  const f = fixture([complete()], { submitStatus: 200 });
  assert.equal(await runSpeech(f.options), 'JOB_ID');
});
test('resume skips submission', async () => {
  const f = fixture([complete()], { resume: true });
  await runSpeech(f.options);
  assert.equal(f.calls.filter(c => c.init.method === 'POST').length, 0);
});
test('429 waits for Retry-After', async () => {
  const f = fixture([json({}, 429, { 'Retry-After': '17' }), complete()]);
  await runSpeech(f.options);
  assert.deepEqual(f.delays, [17000]);
});
for (const status of ['failed', 'cancelled']) {
  test(`${status} stops without download or new submission`, async () => {
    const f = fixture([json({ status, error: { code: 'processing_failed' } })]);
    await assert.rejects(runSpeech(f.options), new RegExp(`Job ${status}`));
    assert.equal(f.calls.length, 2);
    assert.deepEqual(f.saved, []);
  });
}
test('expired completion stops without download', async () => {
  const f = fixture([json({ status: 'completed', result: { expired: true, files: [] } })]);
  await assert.rejects(runSpeech(f.options), /No available/);
  assert.equal(f.calls.length, 2);
});
test('bounded polling preserves resumable job', async () => {
  const f = fixture([json({ status: 'processing' })]);
  await assert.rejects(runSpeech({ ...f.options, attempts: 1 }), /resume with METKURD_JOB_ID/);
  assert.equal(f.calls.length, 2);
});
test('ambiguous submission never retries with a new identity', async () => {
  const f = fixture([], { submitError: new Error('Synthetic timeout') });
  await assert.rejects(runSpeech(f.options), /Synthetic timeout/);
  assert.equal(f.calls.length, 1);
});
test('idempotency conflict never retries', async () => {
  const f = fixture([], { submitStatus: 409 });
  await assert.rejects(runSpeech(f.options), /idempotency_conflict/);
  assert.equal(f.calls.length, 1);
});
