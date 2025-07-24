# MinhOS Historical Data API Test Suite
# PowerShell version for comprehensive testing

Write-Host "MinhOS Historical Data API Test Suite" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""

# Test 1: Health Check
Write-Host "Test 1: Bridge Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8765/health" -Method Get
    Write-Host "✅ Health Check: " -NoNewline -ForegroundColor Green
    Write-Host $response.status
} catch {
    Write-Host "❌ Health Check Failed: " -NoNewline -ForegroundColor Red
    Write-Host $_.Exception.Message
}
Write-Host ""

# Test 2: Directory Listing
Write-Host "Test 2: Directory Listing" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8765/api/file/list?path=C:\SierraChart\Data" -Method Get
    if ($response.success) {
        Write-Host "✅ Directory Listing: " -NoNewline -ForegroundColor Green
        Write-Host "$($response.total_files) files found"
        
        # Show file types
        $dlyFiles = ($response.files | Where-Object { $_.extension -eq ".dly" }).Count
        $scidFiles = ($response.files | Where-Object { $_.extension -eq ".scid" }).Count
        Write-Host "   📊 Daily files (.dly): $dlyFiles"
        Write-Host "   📈 Tick files (.scid): $scidFiles"
    } else {
        Write-Host "❌ Directory listing failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Directory Listing Failed: " -NoNewline -ForegroundColor Red
    Write-Host $_.Exception.Message
}
Write-Host ""

# Test 3: Security Validation
Write-Host "Test 3: Security Validation (should be denied)" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8765/api/file/list?path=C:\Windows" -Method Get
    Write-Host "❌ Security Test Failed: Access should be denied" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 403) {
        Write-Host "✅ Security Test Passed: Access correctly denied" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Unexpected security response: " -NoNewline -ForegroundColor Yellow
        Write-Host $_.Exception.Message
    }
}
Write-Host ""

# Test 4: File Reading (if .dly files exist)
Write-Host "Test 4: File Reading Test" -ForegroundColor Yellow
try {
    # First get directory listing to find a .dly file
    $dirResponse = Invoke-RestMethod -Uri "http://localhost:8765/api/file/list?path=C:\SierraChart\Data" -Method Get
    $dlyFile = $dirResponse.files | Where-Object { $_.extension -eq ".dly" } | Select-Object -First 1
    
    if ($dlyFile) {
        $filePath = "C:\SierraChart\Data\$($dlyFile.name)"
        $fileResponse = Invoke-RestMethod -Uri "http://localhost:8765/api/file/read?path=$filePath" -Method Get
        
        if ($fileResponse.success) {
            $lines = $fileResponse.content.Split("`n").Count
            Write-Host "✅ File Reading: " -NoNewline -ForegroundColor Green
            Write-Host "$($dlyFile.name) - $lines lines read"
        } else {
            Write-Host "❌ File reading failed" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠️ No .dly files found for testing" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ File Reading Failed: " -NoNewline -ForegroundColor Red
    Write-Host $_.Exception.Message
}
Write-Host ""

# Summary
Write-Host "Test Summary Complete!" -ForegroundColor Green
Write-Host "=====================" -ForegroundColor Green
Write-Host ""
Write-Host "If all tests passed, the historical data integration is working correctly." -ForegroundColor Cyan
Write-Host "You can now notify the Linux side that Windows implementation is complete." -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")