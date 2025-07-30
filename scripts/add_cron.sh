#!/bin/bash
# Add MinhOS Sunday start to crontab

# Create temporary file with current crontab
crontab -l 2>/dev/null > /tmp/current_cron || true

# Add new cron job if not already present
if ! grep -q "minh.py start" /tmp/current_cron; then
    echo "# Start MinhOS every Sunday at 3:00 PM PST" >> /tmp/current_cron
    echo "0 15 * * 0 cd /home/colindo/Sync/minh_v4 && /usr/bin/python3 minh.py start --monitor >> /home/colindo/Sync/minh_v4/cron_start.log 2>&1" >> /tmp/current_cron
    
    # Install new crontab
    crontab /tmp/current_cron
    echo "Cron job added successfully!"
else
    echo "Cron job already exists"
fi

# Clean up
rm -f /tmp/current_cron

# Show current crontab
echo "Current crontab:"
crontab -l