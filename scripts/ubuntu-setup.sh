#!/bin/bash
# Personify — full Ubuntu server setup (Hostinger VPS or any Ubuntu 22.04+)
#
# BEFORE running:
#   1. Upload the "backend" folder to the server (see README in comments below)
#   2. Create .env with Supabase SECRET key
#
# Run:
#   cd ~/personify/backend
#   chmod +x scripts/ubuntu-setup.sh scripts/deploy-vps.sh
#   sudo ./scripts/ubuntu-setup.sh

set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Run with sudo:  sudo ./scripts/ubuntu-setup.sh"
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=============================================="
echo " Personify API — Ubuntu setup"
echo " Folder: $ROOT"
echo "=============================================="

export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq curl ca-certificates gnupg ufw nano git

# Firewall: SSH + API port
ufw allow OpenSSH 2>/dev/null || ufw allow 22/tcp
ufw allow 8000/tcp
echo "y" | ufw enable 2>/dev/null || true
ufw status || true

if ! command -v docker >/dev/null 2>&1; then
  echo "==> Installing Docker..."
  curl -fsSL https://get.docker.com | sh
fi
systemctl enable --now docker

if ! docker compose version >/dev/null 2>&1; then
  apt-get install -y -qq docker-compose-plugin
fi

if [ ! -f .env ]; then
  echo ""
  echo "Creating .env template — YOU MUST EDIT THE SECRET KEY:"
  cat > .env <<'EOF'
SUPABASE_URL=https://mginpcemkvealaumocfa.supabase.co
SUPABASE_KEY=REPLACE_WITH_sb_secret_FROM_SUPABASE_DASHBOARD
MATCH_DISTANCE_THRESHOLD=0.6
API_HOST=0.0.0.0
API_PORT=8000
EOF
  chmod 600 .env
  echo ""
  echo "  nano $ROOT/.env"
  echo "Replace SUPABASE_KEY, save, then run:"
  echo "  cd $ROOT && ./scripts/deploy-vps.sh"
  exit 0
fi

# Delegate to deploy script (no sudo needed for docker if user in group — run as root here is ok)
bash "$ROOT/scripts/deploy-vps.sh"

PUBLIC_IP=$(curl -sf --max-time 5 ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')
echo ""
echo "=============================================="
echo " Done. Test from your phone/PC:"
echo "   http://${PUBLIC_IP}:8000/health"
echo " Flutter api_constants.dart:"
echo "   http://${PUBLIC_IP}:8000"
echo "=============================================="
