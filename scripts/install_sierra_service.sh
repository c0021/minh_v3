#!/bin/bash
# Install and configure MinhOS Sierra Client service

echo "============================================"
echo "Installing MinhOS Sierra Client Service"
echo "============================================"
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (sudo $0)"
    exit 1
fi

# Copy service file
echo "Installing systemd service..."
cp /home/colindo/Sync/minh_v3/systemd/minhos-sierra-client.service /etc/systemd/system/

# Reload systemd
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable service
echo "Enabling service to start on boot..."
systemctl enable minhos-sierra-client.service

# Show status
echo
echo "Service installed successfully!"
echo
echo "Available commands:"
echo "  sudo systemctl start minhos-sierra-client    # Start the service"
echo "  sudo systemctl stop minhos-sierra-client     # Stop the service"
echo "  sudo systemctl restart minhos-sierra-client  # Restart the service"
echo "  sudo systemctl status minhos-sierra-client   # Check service status"
echo "  sudo journalctl -u minhos-sierra-client -f   # View live logs"
echo
echo "============================================"