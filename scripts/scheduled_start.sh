#!/bin/bash
# Scheduled start script for MinhOS

# Calculate target time (7 hours from now)
TARGET_TIME=$(date -d "+7 hours" "+%Y-%m-%d %H:%M:%S")
echo "MinhOS scheduled to start at: $TARGET_TIME"

# Sleep for 7 hours (25200 seconds)
echo "Waiting 7 hours before starting MinhOS..."
sleep 25200

# Change to MinhOS directory
cd /home/colindo/Sync/minh_v4

# Start MinhOS with monitoring
echo "Starting MinhOS at $(date)..."
python3 minh.py start --monitor