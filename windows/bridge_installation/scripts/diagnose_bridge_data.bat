@echo off
echo === Bridge Data Flow Diagnosis ===
echo.

echo 1. Checking if bridge is running...
curl -s http://localhost:8765/health
echo.
echo.

echo 2. Checking available symbols...
curl -s http://localhost:8765/api/symbols
echo.
echo.

echo 3. Checking NQ market data from bridge...
curl -s http://localhost:8765/api/data/NQU25-CME
echo.
echo.

echo 4. Checking ACSIL JSON output...
type "C:\SierraChart\Data\ACSILOutput\NQU25_CME.json" 2>NUL || echo No ACSIL data found
echo.
echo.

echo 5. Checking SCID file modification time...
dir "C:\SierraChart\Data\NQU25-CME.scid" | find "NQU25"
echo.

echo 6. Checking bridge cache status...
curl -s http://localhost:8765/api/bridge/stats
echo.
echo.

pause