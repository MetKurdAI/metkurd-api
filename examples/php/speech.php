<?php
// PHP 8.2+ with ext-curl. Server/CLI only; see examples/README.md.
declare(strict_types=1);

const API_BASE = 'https://metkurd.ai/api/v2';

function configured(string $name): string
{
    $value = trim((string) getenv($name));
    if ($value === '' || in_array($value, ['YOUR_API_KEY', 'VOICE_ID', 'YOUR_UNIQUE_REQUEST_ID', 'JOB_ID'], true)) {
        throw new RuntimeException("Set $name locally; replace the placeholder.");
    }
    return $value;
}

function requestJson(string $path, array $headers, ?array $payload = null): array
{
    $ch = curl_init(API_BASE.$path);
    $responseHeaders = [];
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true, CURLOPT_FOLLOWLOCATION => false,
        CURLOPT_CONNECTTIMEOUT => 15, CURLOPT_TIMEOUT => $payload === null ? 30 : 90,
        CURLOPT_HTTPHEADER => [...$headers, 'Accept: application/json', ...($payload !== null ? ['Content-Type: application/json'] : [])],
        CURLOPT_HEADERFUNCTION => function ($handle, string $line) use (&$responseHeaders): int {
            if (str_contains($line, ':')) {
                [$name, $value] = explode(':', $line, 2);
                $responseHeaders[strtolower(trim($name))] = trim($value);
            }
            return strlen($line);
        },
    ]);
    if ($payload !== null) {
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload, JSON_THROW_ON_ERROR));
    }
    $raw = curl_exec($ch);
    $status = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    if ($raw === false) throw new RuntimeException('Network failure. Keep original input/key; resume known job ID.');
    if ($status === 429 && $payload === null) return ['rate_limited' => true, 'retry' => $responseHeaders['retry-after'] ?? '10'];
    $body = json_decode($raw, true);
    if ($status < 200 || $status >= 300) {
        $code = is_array($body) ? ($body['error']['code'] ?? 'http_error') : 'non_json_response';
        throw new RuntimeException("HTTP $status: $code. Keep original input/key.");
    }
    if (!is_array($body)) throw new RuntimeException('Expected a JSON object.');
    return $body;
}

function download(string $id, array $headers, string $output): void
{
    $target = fopen($output, 'wb');
    if ($target === false) throw new RuntimeException('Cannot open output file.');
    $ch = curl_init(API_BASE.'/files/'.rawurlencode($id).'/download');
    curl_setopt_array($ch, [CURLOPT_FILE => $target, CURLOPT_HTTPHEADER => $headers,
        CURLOPT_FOLLOWLOCATION => false, CURLOPT_FAILONERROR => true,
        CURLOPT_CONNECTTIMEOUT => 15, CURLOPT_TIMEOUT => 90]);
    $ok = curl_exec($ch);
    $status = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    fclose($target);
    if ($ok === false || $status < 200 || $status >= 300) {
        throw new RuntimeException("Download failed (HTTP $status); the output may be incomplete.");
    }
}

try {
    $headers = ['Authorization: Bearer '.configured('METKURD_API_KEY')];
    $id = trim((string) getenv('METKURD_JOB_ID'));
    if ($id !== '') {
        $id = configured('METKURD_JOB_ID');
    } else {
        $job = requestJson('/speech', [...$headers, 'Idempotency-Key: '.configured('METKURD_IDEMPOTENCY_KEY')], [
            'text' => 'سڵاو لە مێتکوردەوە', 'voice' => configured('METKURD_VOICE_ID'),
            'model' => '2.0', 'language' => 'ckb', 'storage_mode' => 'temporary',
        ]);
        $id = $job['id'] ?? '';
        if (!is_string($id) || $id === '') throw new RuntimeException('Missing job ID; preserve original input/key.');
    }
    echo "Job: $id\n";
    for ($attempt = 0; $attempt < 60; $attempt++) {
        $job = requestJson('/jobs/'.rawurlencode($id), $headers);
        if ($job['rate_limited'] ?? false) {
            sleep(ctype_digit($job['retry']) ? max(1, (int) $job['retry']) : 10);
            continue;
        }
        $status = $job['status'] ?? '';
        echo "Status: $status\n";
        if (in_array($status, ['failed', 'cancelled'], true)) {
            throw new RuntimeException('Job '.$status.': '.($job['error']['code'] ?? $status));
        }
        if ($status === 'completed') {
            $files = $job['result']['files'] ?? [];
            if (($job['result']['expired'] ?? false) || !$files) throw new RuntimeException('No available result files; result may have expired.');
            download($files[0]['id'], $headers, 'result.wav');
            echo "Downloaded: result.wav\n";
            exit(0);
        }
        if (!in_array($status, ['queued', 'processing'], true)) throw new RuntimeException('Unknown job status.');
        if ($attempt < 59) sleep(10);
    }
    throw new RuntimeException("Polling limit reached. Job still exists; resume with METKURD_JOB_ID=$id.");
} catch (Throwable $e) {
    fwrite(STDERR, $e->getMessage()."\n");
    exit(1);
}
