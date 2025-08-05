@echo off
echo Organizing bridge_installation folder...

REM Move startup scripts to scripts folder
move start_bridge_direct.py scripts\ 2>nul
move start_monitor.bat scripts\ 2>nul
move restart_bridge.py scripts\ 2>nul
move restart_bridge_with_new_endpoints.py scripts\ 2>nul

REM Move service and installation scripts to scripts folder
move install_service.bat scripts\ 2>nul
move uninstall_service.bat scripts\ 2>nul
move service_status.bat scripts\ 2>nul
move bridge_service.py scripts\ 2>nul
move service_wrapper.py scripts\ 2>nul
move PERMANENT_SOLUTION.bat scripts\ 2>nul
move final_permanent_solution.bat scripts\ 2>nul
move install_permanent_solution.bat scripts\ 2>nul

REM Move monitoring files to monitoring folder
move monitor_bridge.py monitoring\ 2>nul
move check_bridge_status.py monitoring\ 2>nul
move email_alerts.py monitoring\ 2>nul
move bridge_status_dashboard.html monitoring\ 2>nul

REM Move configuration files to config folder
move email_config.json config\ 2>nul
move bridge_symbols.json config\ 2>nul

REM Move diagnostic and test scripts to scripts folder
move check_port.bat scripts\ 2>nul
move check_sierra_chart.bat scripts\ 2>nul
move check_status.bat scripts\ 2>nul
move diagnose_bridge_data.bat scripts\ 2>nul
move test_bridge.py scripts\ 2>nul
move test_endpoints.ps1 scripts\ 2>nul
move test_import.py scripts\ 2>nul
move test_imports.py scripts\ 2>nul
move test_websocket_fix.py scripts\ 2>nul
move force_bridge_update.py scripts\ 2>nul

REM Move documentation to docs folder
move README.md docs\ 2>nul
move BRIDGE_FINAL_FIX_REPORT.md docs\ 2>nul
move BRIDGE_SYNTAX_ERROR_REPORT.md docs\ 2>nul
move CLEANUP_COMPLETE.md docs\ 2>nul
move WINDOWS_INSTALLATION_GUIDE.md docs\ 2>nul
move WINDOWS_SERVICE_SETUP.md docs\ 2>nul
move INSTALL_COMMANDS.txt docs\ 2>nul

REM Move old log files to logs_archive
move bridge.sync-conflict-*.log logs_archive\ 2>nul
move test_output*.log logs_archive\ 2>nul

REM Move setup scripts to scripts folder
move setup_email_alerts.bat scripts\ 2>nul

echo.
echo Organization complete!
echo.
echo Folder structure:
echo   scripts/     - All startup, service, and diagnostic scripts
echo   monitoring/  - Monitoring tools and dashboard
echo   config/      - Configuration files
echo   docs/        - Documentation and reports
echo   logs_archive/ - Old log files
echo   logs/        - Current logs (if exists)
echo   monitoring_logs/ - Monitor logs (if exists)
echo.
echo Core files remaining in root:
echo   bridge.py    - Main bridge application
echo   file_access_api.py - File API
echo   requirements.txt - Dependencies
echo   bridge.log   - Current bridge log
echo   bridge_startup.log - Startup log
echo.
