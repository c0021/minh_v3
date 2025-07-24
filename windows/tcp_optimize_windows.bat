@echo off
REM TCP Optimization Script for Windows (Sierra Chart PC)
REM Run as Administrator

echo ============================================
echo TCP Optimization for Sierra Chart Bridge API
echo ============================================
echo.

REM Disable Nagle's Algorithm system-wide
echo Disabling Nagle's Algorithm...
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v TcpAckFrequency /t REG_DWORD /d 1 /f
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v TcpNoDelay /t REG_DWORD /d 1 /f

REM Optimize TCP settings for low latency
echo.
echo Optimizing TCP settings for low latency...
netsh int tcp set global autotuninglevel=normal
netsh int tcp set global chimney=disabled
netsh int tcp set global timestamps=enabled

REM Additional optimizations for real-time data
echo.
echo Applying additional real-time optimizations...
netsh int tcp set global rss=enabled
netsh int tcp set global rsc=disabled
netsh int tcp set heuristics disabled

REM Set TCP keep-alive parameters
echo.
echo Setting TCP keep-alive parameters...
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v KeepAliveTime /t REG_DWORD /d 30000 /f
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v KeepAliveInterval /t REG_DWORD /d 1000 /f

echo.
echo ============================================
echo TCP optimizations applied successfully!
echo.
echo IMPORTANT: Please restart the Bridge API service
echo and reboot the system for all changes to take effect.
echo ============================================
pause