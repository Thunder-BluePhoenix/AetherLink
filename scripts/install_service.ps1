# Copyright (c) 2024 Thunder-BluePhoenix <bluephoenix00995@gmail.com>
#
# Licensed under the Apache License 2.0 / GPL 3.0 (dual license).
#
# scripts/install_service.ps1
#
# One-shot script to install the AetherLink Windows Service with:
#   - Automatic startup on boot
#   - Recovery policy: restart on each of the first 3 failures (60s delay)
#   - Firewall rule for TCP 58008 (idempotent)
#
# Run as Administrator:
#   powershell -ExecutionPolicy Bypass -File scripts\install_service.ps1

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$Python     = (Get-Command python -ErrorAction Stop).Source
$ServicePy  = Join-Path $ProjectDir "AetherLinkService.py"

Write-Host ""
Write-Host "=== AetherLink Service Installer ===" -ForegroundColor Cyan
Write-Host "Project : $ProjectDir"
Write-Host "Python  : $Python"
Write-Host "Service : $ServicePy"
Write-Host ""

# ---------------------------------------------------------------------------
# 1. Install pywin32 post-install step (needed once after pip install)
# ---------------------------------------------------------------------------

Write-Host "[1/5] Running pywin32 post-install..." -ForegroundColor Yellow
$pywin32Scripts = Join-Path (Split-Path $Python) "Scripts"
$postInstall    = Join-Path $pywin32Scripts "pywin32_postinstall.py"

if (Test-Path $postInstall) {
    & $Python $postInstall -install
    Write-Host "      pywin32 post-install done." -ForegroundColor Green
} else {
    Write-Host "      pywin32_postinstall.py not found — skipping (may already be done)." -ForegroundColor DarkYellow
}

# ---------------------------------------------------------------------------
# 2. Register the Windows Service
# ---------------------------------------------------------------------------

Write-Host "[2/5] Installing AetherLink service..." -ForegroundColor Yellow

# Remove existing installation if present
$existing = Get-Service -Name "AetherLink" -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "      Existing service found — removing first." -ForegroundColor DarkYellow
    & $Python $ServicePy remove
    Start-Sleep -Seconds 2
}

& $Python $ServicePy install
Write-Host "      Service registered." -ForegroundColor Green

# ---------------------------------------------------------------------------
# 3. Set startup type to Automatic
# ---------------------------------------------------------------------------

Write-Host "[3/5] Setting startup type to Automatic..." -ForegroundColor Yellow
Set-Service -Name "AetherLink" -StartupType Automatic
Write-Host "      Done." -ForegroundColor Green

# ---------------------------------------------------------------------------
# 4. Configure recovery actions
#    reset=86400 (reset failure count after 24h)
#    actions=restart/60000 three times (restart after 60s on each failure)
# ---------------------------------------------------------------------------

Write-Host "[4/5] Configuring failure recovery (restart after 60s, x3)..." -ForegroundColor Yellow
sc.exe failure AetherLink reset= 86400 actions= restart/60000/restart/60000/restart/60000 | Out-Null
Write-Host "      Done." -ForegroundColor Green

# ---------------------------------------------------------------------------
# 5. Ensure firewall rule exists (idempotent — same logic as setup_firewall.ps1)
# ---------------------------------------------------------------------------

Write-Host "[5/5] Ensuring firewall rule for TCP 58008..." -ForegroundColor Yellow
$ruleName = "AetherLink-58008"
$existing = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "      Rule already exists — skipping." -ForegroundColor DarkYellow
} else {
    New-NetFirewallRule `
        -DisplayName  $ruleName `
        -Direction    Inbound `
        -Protocol     TCP `
        -LocalPort    58008 `
        -Action       Allow `
        -Profile      Any | Out-Null
    Write-Host "      Firewall rule created." -ForegroundColor Green
}

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

Write-Host ""
Write-Host "=== Installation complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Start the service now:" -ForegroundColor White
Write-Host "    sc start AetherLink" -ForegroundColor Gray
Write-Host ""
Write-Host "Check status:" -ForegroundColor White
Write-Host "    sc query AetherLink" -ForegroundColor Gray
Write-Host "    Get-Content '$ProjectDir\logs\aetherlink.log' -Tail 30" -ForegroundColor Gray
Write-Host ""
Write-Host "Stop / uninstall:" -ForegroundColor White
Write-Host "    sc stop AetherLink" -ForegroundColor Gray
Write-Host "    python AetherLinkService.py remove" -ForegroundColor Gray
Write-Host ""
