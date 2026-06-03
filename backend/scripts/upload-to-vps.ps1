# Upload backend from your PC to Hostinger VPS (run in PowerShell on Windows)
# Usage:
#   cd C:\Users\abdul\Developer\personify\backend\scripts
#   .\upload-to-vps.ps1
#
# You will be asked for the VPS root password once (do not share it in chat).

param(
  [string]$VpsIp = "62.72.20.81",
  [string]$VpsUser = "root",
  [string]$RemoteDir = "/root/personify/backend"
)

$BackendRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Parent = Split-Path $BackendRoot -Parent

Write-Host "Uploading backend to ${VpsUser}@${VpsIp}:${RemoteDir} ..."

ssh "${VpsUser}@${VpsIp}" "mkdir -p $RemoteDir"

# Upload backend files (exclude .venv)
scp -r `
  "$BackendRoot\main.py" `
  "$BackendRoot\app" `
  "$BackendRoot\requirements.txt" `
  "$BackendRoot\Dockerfile" `
  "$BackendRoot\docker-compose.yml" `
  "$BackendRoot\.dockerignore" `
  "$BackendRoot\scripts" `
  "${VpsUser}@${VpsIp}:${RemoteDir}/"

Write-Host ""
Write-Host "Next steps ON THE VPS (SSH in):"
Write-Host "  1. nano $RemoteDir/.env   (paste SUPABASE_URL + SECRET key)"
Write-Host "  2. cd $RemoteDir && chmod +x scripts/deploy-vps.sh && ./scripts/deploy-vps.sh"
Write-Host ""
Write-Host "Never commit .env or paste passwords in Cursor chat."
