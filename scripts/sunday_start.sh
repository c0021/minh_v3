#!/bin/bash
# Sunday 3PM PST automatic start script for MinhOS

# Function to calculate seconds until next Sunday 3PM PST
calculate_seconds_until_sunday() {
    # Get current day of week (0=Sunday, 6=Saturday)
    current_day=$(date +%w)
    current_hour=$(date +%H)
    current_min=$(date +%M)
    
    # Calculate days until Sunday
    if [ $current_day -eq 0 ] && [ $(date +%H%M) -lt 1500 ]; then
        # It's Sunday but before 3PM
        days_until_sunday=0
    else
        # Calculate days until next Sunday
        days_until_sunday=$((7 - current_day))
        if [ $current_day -eq 0 ]; then
            days_until_sunday=7
        fi
    fi
    
    # Calculate target timestamp for next Sunday 3PM
    target_date=$(date -d "next Sunday 15:00:00" +%s)
    current_date=$(date +%s)
    
    # If it's already Sunday and past 3PM, add 7 days
    if [ $current_day -eq 0 ] && [ $(date +%H%M) -ge 1500 ]; then
        target_date=$(date -d "next Sunday 15:00:00 + 7 days" +%s)
    fi
    
    # Calculate seconds until target
    seconds_until=$((target_date - current_date))
    echo $seconds_until
}

# Main loop
while true; do
    # Calculate time until next Sunday 3PM
    seconds_to_wait=$(calculate_seconds_until_sunday)
    
    # Convert to human readable format
    days=$((seconds_to_wait / 86400))
    hours=$(((seconds_to_wait % 86400) / 3600))
    minutes=$(((seconds_to_wait % 3600) / 60))
    
    echo "Next start scheduled for Sunday 3:00 PM PST"
    echo "Waiting $days days, $hours hours, $minutes minutes..."
    echo "Target time: $(date -d "@$(($(date +%s) + seconds_to_wait))" "+%Y-%m-%d %H:%M:%S")"
    
    # Sleep until target time
    sleep $seconds_to_wait
    
    # Start MinhOS
    echo "Starting MinhOS at $(date)..."
    cd /home/colindo/Sync/minh_v4
    python3 minh.py start --monitor &
    
    # Wait a bit before checking for next Sunday
    sleep 60
done