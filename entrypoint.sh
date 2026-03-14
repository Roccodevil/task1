#!/bin/sh
set -e

OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://ollama:11434}"
OLLAMA_MODEL="${OLLAMA_MODEL:-llama3}"
OLLAMA_BASE_URL="${OLLAMA_BASE_URL%/}"

echo "[startup] Pulling Ollama model '${OLLAMA_MODEL}' from ${OLLAMA_BASE_URL} ..."
echo "[startup] This may take several minutes on first run (model is ~4 GB)."

# stream:false blocks until the pull is fully complete then returns one JSON line.
# --max-time 3600 gives up to 1 hour for slow connections.
if curl -fsSL -X POST "${OLLAMA_BASE_URL}/api/pull" \
     -H "Content-Type: application/json" \
     -d "{\"name\":\"${OLLAMA_MODEL}\",\"stream\":false}" \
     --max-time 3600 \
     -o /tmp/pull_result.json 2>/tmp/pull_err.txt; then
  echo "[startup] Model '${OLLAMA_MODEL}' is ready."
else
  echo "[startup] Warning: pull returned non-zero ($(cat /tmp/pull_err.txt)). Continuing anyway."
fi

exec "$@"
