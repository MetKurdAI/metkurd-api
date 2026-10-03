#!/usr/bin/env bash
set -euo pipefail
# Bash + cURL + jq. Keep credentials server-side. Do not use shell tracing (set -x).
base='https://metkurd.ai/api/v2'
require_value() {
  case "${!1:-}" in
    ''|YOUR_API_KEY|VOICE_ID|YOUR_UNIQUE_REQUEST_ID|JOB_ID)
      printf 'Set %s locally; replace the placeholder.\n' "$1" >&2; exit 1 ;;
  esac
}
require_value METKURD_API_KEY
command -v jq >/dev/null || { echo 'Install jq first.' >&2; exit 1; }
scratch=$(mktemp -d)
trap 'rm -f -- "$scratch/body" "$scratch/headers"; rmdir -- "$scratch"' EXIT

request_json() {
  if ! status=$(curl --silent --show-error --connect-timeout 15 --max-time 90 \
    --proto '=https' -D "$scratch/headers" -o "$scratch/body" -w '%{http_code}' \
    -H "Authorization: Bearer $METKURD_API_KEY" -H 'Accept: application/json' "$@"); then
    echo 'Network failure. Keep original input/key; resume the job ID if known.' >&2
    exit 1
  fi
}
check_status() {
  case "$status" in
    2??) ;;
    *) printf 'HTTP %s: ' "$status" >&2
       jq -r '.error.code // "http_error"' "$scratch/body" >&2 || true
       echo 'Keep original input/key; inspect the error before retrying.' >&2; exit 1 ;;
  esac
}
job_id=${METKURD_JOB_ID:-}
if [[ -n "$job_id" ]]; then
  require_value METKURD_JOB_ID
else
  require_value METKURD_VOICE_ID
  require_value METKURD_IDEMPOTENCY_KEY
  body=$(jq -n --arg voice "$METKURD_VOICE_ID" '{text:"سڵاو لە مێتکوردەوە",voice:$voice,model:"2.0",language:"ckb",storage_mode:"temporary"}')
  request_json "$base/speech" -X POST -H "Idempotency-Key: $METKURD_IDEMPOTENCY_KEY" \
    -H 'Content-Type: application/json' --data "$body"
  check_status
  job_id=$(jq -er '.id | select(type == "string" and length > 0)' "$scratch/body")
fi
printf 'Job: %s\n' "$job_id"
encoded_job=$(jq -nr --arg id "$job_id" '$id | @uri')
for ((attempt=0; attempt<60; attempt++)); do
  request_json "$base/jobs/$encoded_job"
  if [[ "$status" == 429 ]]; then
    retry=$(awk 'tolower($1)=="retry-after:" {gsub("\r", "", $2); print $2}' "$scratch/headers")
    [[ "$retry" =~ ^[0-9]+$ && "$retry" -gt 0 ]] || retry=10
    sleep "$retry"
    continue
  fi
  check_status
  state=$(jq -er '.status' "$scratch/body")
  printf 'Status: %s\n' "$state"
  case "$state" in
    completed)
      if ! jq -e '(.result.expired != true) and (.result.files | length > 0)' "$scratch/body" >/dev/null; then
        echo 'No available result files; result may have expired.' >&2; exit 1
      fi
      file_id=$(jq -er '.result.files[0].id | @uri' "$scratch/body")
      # No redirect following; credentials remain on the canonical origin.
      download_status=$(curl --silent --show-error --fail-with-body --connect-timeout 15 --max-time 90 \
        --proto '=https' "$base/files/$file_id/download" -H "Authorization: Bearer $METKURD_API_KEY" \
        -o result.wav -w '%{http_code}')
      [[ "$download_status" == 2?? ]] || { echo 'Download failed; output may be incomplete.' >&2; exit 1; }
      echo 'Downloaded: result.wav'; exit 0 ;;
    failed|cancelled)
      jq -r '.error.code // .status' "$scratch/body" >&2; exit 1 ;;
    queued|processing) ;;
    *) echo 'Unknown job status; inspect before continuing.' >&2; exit 1 ;;
  esac
  if ((attempt < 59)); then sleep 10; fi
done
printf 'Polling limit reached. Job still exists; resume with METKURD_JOB_ID=%s.\n' "$job_id" >&2
exit 1
