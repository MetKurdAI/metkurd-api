import { createWriteStream } from 'node:fs';
import { Readable } from 'node:stream';
import { pipeline } from 'node:stream/promises';
import { runSpeech } from '../javascript/workflow.mjs';

try {
  await runSpeech({
    apiKey: process.env.METKURD_API_KEY,
    voice: process.env.METKURD_VOICE_ID,
    idempotencyKey: process.env.METKURD_IDEMPOTENCY_KEY,
    jobId: process.env.METKURD_JOB_ID,
    save: async body => {
      await pipeline(Readable.fromWeb(body), createWriteStream('result.wav'));
      console.log('Downloaded: result.wav');
    },
  });
} catch (error) {
  console.error(error.message);
  console.error('Keep the original input/key. Resume with the job ID if known; do not blindly resubmit.');
  process.exitCode = 1;
}
