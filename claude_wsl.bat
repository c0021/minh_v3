@echo off
REM Wrapper to run Claude CLI from WSL using Windows installation
cd /d "C:\Users\colin\Sync\minh_v4"
node "C:\Users\colin\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\cli.js" %*
