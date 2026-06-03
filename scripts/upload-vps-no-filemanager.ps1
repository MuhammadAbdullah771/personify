# Upload face-match API to Hostinger VPS (no domain, no file manager)
# Needs: OpenSSH Client on Windows (Settings → Optional features → OpenSSH Client)
#
# Run in PowerShell:
#   cd C:\Users\abdul\Developer\personify\backend\scripts
#   .\upload-vps-no-filemanager.ps1

param(
  [string]$VpsIp = "62.72.20.81",
  [string]$User = "root",
  [string]$ZipPath = "C:\Users\abdul\Developer\personify\personify-api-deploy.zip"
)

if (-not (Test-Path $ZipPath)) {
  Write-Host "Zip missing. Run from project root first or recreate zip."
  exit 1
}

Write-Host "Connecting to ${User}@${VpsIp} ..."
Write-Host "You will be asked for the VPS root password (typed in YOUR window only)."
Write-Host ""

ssh "${User}@${VpsIp}" "mkdir -p /root/personify/backend"
scp $ZipPath "${User}@${VpsIp}:/root/personify/backend/personify-api-deploy.zip"

if ($LASTEXITCODE -eq 0) {
  Write-Host ""
  Write-Host "Upload OK. Now in Hostinger WEB TERMINAL run:"
  Write-Host ""
  Write-Host @"
cd /root/personify/backend
apt update && apt install -y unzip nano curl docker.io docker-compose-plugin
systemctl enable --now docker
unzip -o personify-api-deploy.zip
chmod +x scripts/*.sh
nano .env
docker compose up -d --build
curl http://127.0.0.1:8000/health
"@
} else {
  Write-Host "Upload failed. Try WinSCP (Method 2 in HOSTINGER_UPLOAD.txt) or GitHub (Method 3)."
}
