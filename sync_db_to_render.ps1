# Card Scout DB Sync - PowerShell
# Run from C:\Users\J\Documents\LLM\card-scout
#
# Usage: Right-click in PowerShell -> Paste -> Press Enter
# This will:
#   1. Generate a random SYNC_DB_SECRET
#   2. Show it for you to add to Render Environment
#   3. Wait for you to confirm Render has redeployed
#   4. Upload card_scout.db to Render

# Step 1: Generate a strong secret
$Secret = -join ((1..64) | ForEach-Object { Get-Random -InputObject ([char[]]'abcdef0123456789') })
Write-Host "Generated sync secret: $Secret" -ForegroundColor Cyan
Write-Host ""
Write-Host "STEP 1: Add this to Render Environment as SYNC_DB_SECRET:" -ForegroundColor Yellow
Write-Host "  Key:   SYNC_DB_SECRET"
Write-Host "  Value: $Secret"
Write-Host ""
Write-Host "Render dashboard: https://dashboard.render.com/web/srv-XXXXX -> Environment tab"
Write-Host "Add the variable, save, wait ~60-90 sec for redeploy"
Write-Host ""
Write-Host "Press Enter when Render is back up..."
Read-Host

# Step 2: Upload the local DB
Write-Host ""
Write-Host "Uploading card_scout.db to Render..."
Write-Host ""

$DBPath = Join-Path $PSScriptRoot "card_scout.db"
if (-not (Test-Path $DBPath)) {
    Write-Host "ERROR: card_scout.db not found at $DBPath" -ForegroundColor Red
    exit 1
}

$DBSize = (Get-Item $DBPath).Length
Write-Host "Local DB size: $DBSize bytes"

try {
    $response = Invoke-WebRequest `
        -Uri "https://cardscout.pro/admin/sync_db" `
        -Method POST `
        -Headers @{
            "X-Sync-Secret"   = $Secret
            "Content-Type"    = "application/octet-stream"
        } `
        -InFile $DBPath `
        -UseBasicParsing `
        -TimeoutSec 120

    Write-Host ""
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host "Status:   $($response.StatusCode)"
    Write-Host "Response: $($response.Content)"
}
catch {
    $errorResponse = $_.Exception.Response
    if ($errorResponse) {
        $statusCode = [int]$errorResponse.StatusCode
        Write-Host ""
        Write-Host "FAILED with HTTP $statusCode" -ForegroundColor Red
        $reader = New-Object System.IO.StreamReader($errorResponse.GetResponseStream())
        Write-Host "Response body: $($reader.ReadToEnd())"
    }
    else {
        Write-Host ""
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Press Enter to exit..."
Read-Host
