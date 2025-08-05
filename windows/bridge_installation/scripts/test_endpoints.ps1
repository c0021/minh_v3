#!/usr/bin/env powershell
# Bridge Optimization Endpoint Testing Script
# Tests all Phase 2 optimization endpoints

Write-Host "=== MINHOS BRIDGE OPTIMIZATION ENDPOINT TESTING ===" -ForegroundColor Green
Write-Host "Testing all Phase 2 optimization endpoints..." -ForegroundColor Yellow
Write-Host ""

$baseUrl = "http://localhost:8765"
$endpoints = @(
    @{Name="Health Check"; Path="/health"; Description="Basic health status"},
    @{Name="Market Data"; Path="/api/market_data"; Description="Current market data"},
    @{Name="Bridge Stats"; Path="/api/bridge/stats"; Description="Performance statistics"},
    @{Name="Health Monitoring"; Path="/api/bridge/health_monitoring"; Description="Comprehensive health with circuit breaker"},
    @{Name="Detailed Health"; Path="/api/bridge/health_detailed"; Description="Detailed health metrics"},
    @{Name="Symbols API"; Path="/api/symbols"; Description="Available symbols"},
    @{Name="SSE Dashboard Stream"; Path="/api/stream/dashboard"; Description="Server-Sent Events for dashboard"}
)

foreach ($endpoint in $endpoints) {
    Write-Host "Testing: $($endpoint.Name)" -ForegroundColor Cyan
    Write-Host "  URL: $baseUrl$($endpoint.Path)" -ForegroundColor Gray
    Write-Host "  Description: $($endpoint.Description)" -ForegroundColor Gray
    
    try {
        if ($endpoint.Path -eq "/api/stream/dashboard") {
            # SSE endpoint - just test connection
            $response = Invoke-WebRequest -Uri "$baseUrl$($endpoint.Path)" -TimeoutSec 5 -ErrorAction Stop
            Write-Host "  Status: $($response.StatusCode) - SSE Stream Connected" -ForegroundColor Green
        } else {
            # Regular JSON endpoints
            $response = Invoke-RestMethod -Uri "$baseUrl$($endpoint.Path)" -TimeoutSec 10 -ErrorAction Stop
            Write-Host "  Status: SUCCESS" -ForegroundColor Green
            
            # Show key data for important endpoints
            if ($endpoint.Path -eq "/api/bridge/stats") {
                $cache = $response.file_cache
                $ws = $response.websocket_connections
                Write-Host "    Cache Hit Rate: $([math]::Round($cache.hit_rate * 100, 1))%" -ForegroundColor White
                Write-Host "    WebSocket Connections: $($ws.total_connections)" -ForegroundColor White
            } elseif ($endpoint.Path -eq "/api/bridge/health_monitoring") {
                $health = $response.health
                $circuit = $response.circuit_breaker
                Write-Host "    Health Score: $($health.health_score)/100 ($($health.status))" -ForegroundColor White
                Write-Host "    Circuit Breaker: $($circuit.state)" -ForegroundColor White
                Write-Host "    Production Ready: $($response.production_ready)" -ForegroundColor White
            } elseif ($endpoint.Path -eq "/api/market_data") {
                $symbols = ($response | Get-Member -MemberType NoteProperty).Count
                Write-Host "    Active Symbols: $symbols" -ForegroundColor White
            }
        }
    } catch {
        Write-Host "  Status: FAILED - $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
}

Write-Host "=== WEBSOCKET ENDPOINTS ===" -ForegroundColor Green
Write-Host "Optimized WebSocket: ws://localhost:8765/ws/live_data/{symbol}" -ForegroundColor Yellow
Write-Host "Legacy WebSocket: ws://localhost:8765/ws/market_data" -ForegroundColor Yellow
Write-Host ""
Write-Host "Use a WebSocket client to test real-time streaming." -ForegroundColor Gray
Write-Host ""
Write-Host "=== TESTING COMPLETE ===" -ForegroundColor Green