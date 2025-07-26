# Sierra Chart Data Structure Investigation (PowerShell version)
# More advanced analysis with better formatting and error handling

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Sierra Chart Data Structure Investigation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Date/Time: $(Get-Date)"
Write-Host ""

# Define common Sierra Chart locations
$sierraLocations = @(
    "C:\SierraChart",
    "C:\Program Files\Sierra Chart",
    "C:\Program Files (x86)\Sierra Chart",
    "D:\SierraChart",
    "$env:APPDATA\SierraChart",
    "$env:LOCALAPPDATA\SierraChart"
)

Write-Host "1. SEARCHING FOR SIERRA CHART INSTALLATIONS..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

$foundInstallations = @()
foreach ($location in $sierraLocations) {
    if (Test-Path $location) {
        Write-Host "[FOUND] $location" -ForegroundColor Green
        $foundInstallations += $location
        
        # Show directory contents
        Get-ChildItem $location -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Host "  $($_.Name)" -ForegroundColor Gray
        }
        Write-Host ""
    }
}

if ($foundInstallations.Count -eq 0) {
    Write-Host "[ERROR] No Sierra Chart installations found" -ForegroundColor Red
    
    # Search entire C: drive
    Write-Host "Searching C: drive for SierraChart folders..." -ForegroundColor Yellow
    Get-ChildItem C:\ -Recurse -Directory -Name "*sierra*" -ErrorAction SilentlyContinue | Where-Object { $_ -match "sierra" }
}

Write-Host "2. INVESTIGATING DATA DIRECTORIES..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

$dataDirectories = @()
foreach ($installation in $foundInstallations) {
    $dataPath = Join-Path $installation "Data"
    if (Test-Path $dataPath) {
        Write-Host "[FOUND] Data directory: $dataPath" -ForegroundColor Green
        $dataDirectories += $dataPath
        
        # Show subdirectories
        $subdirs = Get-ChildItem $dataPath -Directory -ErrorAction SilentlyContinue
        if ($subdirs) {
            Write-Host "  Subdirectories:" -ForegroundColor Cyan
            $subdirs | ForEach-Object { Write-Host "    $($_.Name)" -ForegroundColor Gray }
        }
        
        # Count files
        $dlyCount = (Get-ChildItem $dataPath -Filter "*.dly" -Recurse -ErrorAction SilentlyContinue).Count
        $scidCount = (Get-ChildItem $dataPath -Filter "*.scid" -Recurse -ErrorAction SilentlyContinue).Count
        
        Write-Host "  File counts:" -ForegroundColor Cyan
        Write-Host "    .dly files: $dlyCount" -ForegroundColor Gray
        Write-Host "    .scid files: $scidCount" -ForegroundColor Gray
        Write-Host ""
    } else {
        Write-Host "[NOT FOUND] $dataPath" -ForegroundColor Red
    }
}

Write-Host "3. ANALYZING HISTORICAL DATA FILES..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

foreach ($dataDir in $dataDirectories) {
    Write-Host "Analyzing: $dataDir" -ForegroundColor Cyan
    
    # Find .dly files
    Write-Host "  Daily (.dly) files:" -ForegroundColor White
    $dlyFiles = Get-ChildItem $dataDir -Filter "*.dly" -Recurse -ErrorAction SilentlyContinue | 
                Sort-Object LastWriteTime -Descending | 
                Select-Object -First 10
    
    if ($dlyFiles) {
        $dlyFiles | ForEach-Object {
            $sizeKB = [math]::Round($_.Length / 1KB, 1)
            Write-Host "    $($_.Name) - ${sizeKB}KB - $($_.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))" -ForegroundColor Gray
        }
    } else {
        Write-Host "    No .dly files found" -ForegroundColor Red
    }
    
    # Find .scid files
    Write-Host "  Intraday (.scid) files:" -ForegroundColor White
    $scidFiles = Get-ChildItem $dataDir -Filter "*.scid" -Recurse -ErrorAction SilentlyContinue | 
                 Sort-Object LastWriteTime -Descending | 
                 Select-Object -First 10
    
    if ($scidFiles) {
        $scidFiles | ForEach-Object {
            $sizeMB = [math]::Round($_.Length / 1MB, 1)
            Write-Host "    $($_.Name) - ${sizeMB}MB - $($_.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))" -ForegroundColor Gray
        }
    } else {
        Write-Host "    No .scid files found" -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host "4. TRADING SYMBOL ANALYSIS..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

$symbols = @("NQ", "ES", "YM", "RTY", "CL", "GC", "SI", "ZB", "ZN")

foreach ($symbol in $symbols) {
    Write-Host "Symbol: $symbol" -ForegroundColor Cyan
    
    foreach ($dataDir in $dataDirectories) {
        $symbolFiles = Get-ChildItem $dataDir -Filter "$symbol*.*" -ErrorAction SilentlyContinue | 
                       Where-Object { $_.Extension -eq ".dly" -or $_.Extension -eq ".scid" }
        
        if ($symbolFiles) {
            Write-Host "  In $dataDir:" -ForegroundColor White
            $symbolFiles | Sort-Object Name | ForEach-Object {
                $sizeInfo = if ($_.Extension -eq ".dly") { 
                    "$([math]::Round($_.Length / 1KB, 1))KB" 
                } else { 
                    "$([math]::Round($_.Length / 1MB, 1))MB" 
                }
                Write-Host "    $($_.Name) - $sizeInfo" -ForegroundColor Gray
            }
        }
    }
    Write-Host ""
}

Write-Host "5. FILE NAMING PATTERN ANALYSIS..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

foreach ($dataDir in $dataDirectories) {
    Write-Host "Analyzing naming patterns in: $dataDir" -ForegroundColor Cyan
    
    # Get unique file name patterns
    $allFiles = Get-ChildItem $dataDir -Filter "*.*" -ErrorAction SilentlyContinue | 
                Where-Object { $_.Extension -eq ".dly" -or $_.Extension -eq ".scid" }
    
    if ($allFiles) {
        # Group by naming pattern
        $patterns = @{}
        $allFiles | ForEach-Object {
            $name = $_.BaseName
            
            # Detect pattern
            if ($name -match '^[A-Z]{1,3}[FGHJKMNQUVXZ]\d{2}$') {
                $pattern = "Futures Contract (e.g., NQU25)"
            } elseif ($name -match '^[A-Z]{1,3}\s\d{2}-\d{2}$') {
                $pattern = "Date Format (e.g., NQ 03-25)"
            } elseif ($name -match '^[A-Z]{1,3}_\d+$') {
                $pattern = "Underscore Format (e.g., NQ_1)"
            } elseif ($name -match '^[A-Z]{1,3}$') {
                $pattern = "Simple Symbol (e.g., NQ)"
            } else {
                $pattern = "Other Format"
            }
            
            if (-not $patterns[$pattern]) {
                $patterns[$pattern] = @()
            }
            $patterns[$pattern] += $_.Name
        }
        
        # Display patterns
        foreach ($pattern in $patterns.Keys) {
            Write-Host "  Pattern: $pattern" -ForegroundColor White
            $patterns[$pattern] | Select-Object -First 5 | ForEach-Object {
                Write-Host "    Example: $_" -ForegroundColor Gray
            }
        }
    }
    Write-Host ""
}

Write-Host "6. DIRECTORY STRUCTURE SUMMARY..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

foreach ($dataDir in $dataDirectories) {
    Write-Host "Structure of: $dataDir" -ForegroundColor Cyan
    
    # Show tree structure
    Get-ChildItem $dataDir -Recurse -Directory -ErrorAction SilentlyContinue | 
    ForEach-Object {
        $relativePath = $_.FullName.Replace($dataDir, "")
        Write-Host "  $relativePath" -ForegroundColor Gray
        
        # Count files in each subdirectory
        $fileCount = (Get-ChildItem $_.FullName -File -ErrorAction SilentlyContinue).Count
        if ($fileCount -gt 0) {
            Write-Host "    ($fileCount files)" -ForegroundColor DarkGray
        }
    }
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Investigation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "SUMMARY FOR MINHOS BRIDGE CONFIGURATION:" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

if ($dataDirectories.Count -gt 0) {
    Write-Host "Primary data directory: $($dataDirectories[0])" -ForegroundColor Green
    Write-Host ""
    Write-Host "Use these paths in your bridge file_access_api.py:" -ForegroundColor Cyan
    foreach ($dataDir in $dataDirectories) {
        Write-Host "  '$dataDir'" -ForegroundColor White
    }
} else {
    Write-Host "No Sierra Chart data directories found!" -ForegroundColor Red
    Write-Host "Please check Sierra Chart installation and configuration." -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")