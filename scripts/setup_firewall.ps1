# scripts/setup_firewall.ps1 — AetherLink Windows Firewall Setup
# Run once in an elevated PowerShell (right-click -> Run as Administrator)

$RuleName = "AetherLink-58008"
$Port     = 58008

$existing = Get-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue

if ($existing) {
    Write-Host "Rule '$RuleName' already exists. Skipping."
} else {
    New-NetFirewallRule `
        -DisplayName $RuleName `
        -Direction   Inbound `
        -Protocol    TCP `
        -LocalPort   $Port `
        -Action      Allow `
        -Profile     Any
    Write-Host "Firewall rule '$RuleName' created for TCP port $Port."
}
