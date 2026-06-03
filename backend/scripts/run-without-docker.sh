#!/bin/bash
# Run API directly on Ubuntu (no Docker) — build takes 15–30+ minutes on small VPS.
# Prefer: ./scripts/deploy-vps.sh (Docker)
#
#   cd ~/personify/backend
#   chmod +x scripts/run-without-docker.sh
#   ./scripts/run-without-docker.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

sudo apt-get update -qq
sudo apt-get install -y -qq python3 python3-pip python3-venv \
  cmake build-essential libopenblas-dev liblapack-dev \
  libglib2.0-0 libsm6 libxext6 libxrender1

if [ ! -f .env ]; then
  echo "Create .env first (see scripts/deploy-vps.sh header)."
  exit 1
fi

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Starting server on port 8000..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
