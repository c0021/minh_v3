@echo off
echo MinhOS Historical Data API Test Suite
echo =====================================
echo.

echo Testing bridge health...
curl -s http://localhost:8765/health
echo.
echo.

echo Testing directory listing...
curl -s "http://localhost:8765/api/file/list?path=C:\SierraChart\Data"
echo.
echo.

echo Testing security (should be denied)...
curl -s "http://localhost:8765/api/file/list?path=C:\Windows"
echo.
echo.

echo Testing file info...
curl -s "http://localhost:8765/api/file/info?path=C:\SierraChart\Data"
echo.
echo.

echo Test complete! Check responses above.
pause