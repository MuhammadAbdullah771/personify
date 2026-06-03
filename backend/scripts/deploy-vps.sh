#!/bin/bash
# Personify AI API — one-shot deploy on Ubuntu VPS (Hostinger)
# Run ON THE VPS after uploading the backend folder:
#   cd ~/personify/backend && chmod +x scripts/deploy-vps.sh && ./scripts/deploy-vps.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> Personify backend deploy (folder: $ROOT)"

if ! command -v docker >/dev/null 2>&1; then
  echo "==> Installing Docker..."
  apt-get update -qq
  apt-get install -y -qq ca-certificates curl
  curl -fsSL https://get.docker.com | sh
  systemctl enable --now docker
fi

if docker compose version >/dev/null 2>&1; then
  COMPOSE="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE="docker-compose"
else
  apt-get install -y -qq docker-compose-plugin || true
  COMPOSE="docker compose"
fi

if [ ! -f .env ]; then
  echo ""
  echo "ERROR: Missing .env in $ROOT"
  echo "Create it now (use Supabase SECRET key, not publishable):"
  echo ""
  cat <<'ENVEXAMPLE'
SUPABASE_URL=https://mginpcemkvealaumocfa.supabase.co
SUPABASE_KEY=sb_secret_PASTE_FROM_SUPABASE_DASHBOARD
MATCH_DISTANCE_THRESHOLD=0.6
API_HOST=0.0.0.0
API_PORT=8000
ENVEXAMPLE
  echo ""
  echo "  nano .env"
  echo "Then run this script again."
  exit 1
fi

# shellcheck disable=SC1091
set -a
source .env
set +a

if [ -z "${SUPABASE_URL:-}" ] || [ -z "${SUPABASE_KEY:-}" ]; then
  echo "ERROR: SUPABASE_URL and SUPABASE_KEY must be set in .env"
  exit 1
fi

if echo "$SUPABASE_KEY" | grep -q publishable; then
  echo "ERROR: Use the SECRET key (sb_secret_...), not the publishable key."
  exit 1
fi

echo "==> Building and starting container..."
$COMPOSE down 2>/dev/null || true
$COMPOSE up -d --build

echo "==> Waiting for health..."
sleep 5
HEALTH=$(curl -sf "http://127.0.0.1:8000/health" || echo "FAILED")
echo "$HEALTH"

if echo "$HEALTH" | grep -q '"supabase_configured":true'; then
  echo ""
  echo "SUCCESS. API is ready on port 8000."
  echo "Flutter: aiServerBaseUrl = http://YOUR_VPS_IP:8000  (no /docs)"
  echo "Test: curl http://$(curl -sf ifconfig.me 2>/dev/null || echo YOUR_VPS_IP):8000/health"
else
  echo ""
  echo "WARNING: Server started but Supabase may not be configured."
  echo "Check: docker logs personify-api"
  exit 1
fi
