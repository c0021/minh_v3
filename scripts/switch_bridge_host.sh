#!/bin/bash
# Switch MinhOS Bridge Host Configuration
# Usage: ./switch_bridge_host.sh <hostname-or-ip> [port]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
DEFAULT_PORT=8765
MINHOS_DIR="/home/colindo/Sync/minh_v3"

# Get arguments
NEW_HOST=$1
NEW_PORT=${2:-$DEFAULT_PORT}

# Show usage if no arguments
if [ -z "$NEW_HOST" ]; then
    echo "MinhOS Bridge Host Configuration Tool"
    echo "====================================="
    echo ""
    echo "Usage: $0 <hostname-or-ip> [port]"
    echo ""
    echo "Examples:"
    echo "  $0 192.168.1.100          # Use IP address with default port 8765"
    echo "  $0 new-windows-pc 8765    # Use hostname with custom port"
    echo "  $0 localhost              # Use local machine"
    echo ""
    echo "Current configuration:"
    echo "  BRIDGE_HOSTNAME: ${BRIDGE_HOSTNAME:-not set}"
    echo "  BRIDGE_PORT: ${BRIDGE_PORT:-not set}"
    echo ""
    exit 1
fi

echo -e "${YELLOW}Switching to Bridge Host: $NEW_HOST:$NEW_PORT${NC}"
echo ""

# Test connection first
echo -n "Testing connection to $NEW_HOST:$NEW_PORT... "
if curl -s -f -m 5 "http://$NEW_HOST:$NEW_PORT/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Success!${NC}"
    
    # Get bridge info if available
    BRIDGE_INFO=$(curl -s "http://$NEW_HOST:$NEW_PORT/health" 2>/dev/null || echo "{}")
    echo "Bridge API Status: $(echo $BRIDGE_INFO | grep -o '"status":"[^"]*"' | cut -d'"' -f4 || echo "Unknown")"
    
else
    echo -e "${RED}✗ Failed!${NC}"
    echo ""
    echo -e "${RED}Error: Cannot connect to Bridge API at http://$NEW_HOST:$NEW_PORT${NC}"
    echo ""
    echo "Please check:"
    echo "  1. Bridge API is running on $NEW_HOST"
    echo "  2. Port $NEW_PORT is open and accessible"
    echo "  3. No firewall is blocking the connection"
    echo "  4. The hostname/IP is correct"
    echo ""
    echo "You can test manually with:"
    echo "  curl http://$NEW_HOST:$NEW_PORT/health"
    exit 1
fi

echo ""
echo "Updating configuration..."

# Update .env file
ENV_FILE="$MINHOS_DIR/.env"
if [ -f "$ENV_FILE" ]; then
    # Backup existing .env
    cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "  → Backed up existing .env file"
fi

# Create or update .env file
cat > "$ENV_FILE" << EOF
# MinhOS v3 Environment Configuration
# Updated: $(date)

# Sierra Chart Bridge Configuration
BRIDGE_HOSTNAME=$NEW_HOST
BRIDGE_PORT=$NEW_PORT

# Add other configuration as needed
EOF

echo "  → Updated .env file"

# Update environment for current session
export BRIDGE_HOSTNAME=$NEW_HOST
export BRIDGE_PORT=$NEW_PORT

# Update systemd service if it exists
SERVICE_FILE="/etc/systemd/system/minhos-sierra-client.service"
if [ -f "$SERVICE_FILE" ] && [ "$EUID" -eq 0 -o $(sudo -n true 2>/dev/null; echo $?) -eq 0 ]; then
    echo "  → Updating systemd service..."
    
    # Check if service file has Environment lines
    if grep -q "Environment=\"BRIDGE_HOSTNAME" "$SERVICE_FILE"; then
        sudo sed -i "s/Environment=\"BRIDGE_HOSTNAME=.*/Environment=\"BRIDGE_HOSTNAME=$NEW_HOST\"/" "$SERVICE_FILE"
    else
        # Add after [Service] section
        sudo sed -i "/\[Service\]/a Environment=\"BRIDGE_HOSTNAME=$NEW_HOST\"" "$SERVICE_FILE"
    fi
    
    if grep -q "Environment=\"BRIDGE_PORT" "$SERVICE_FILE"; then
        sudo sed -i "s/Environment=\"BRIDGE_PORT=.*/Environment=\"BRIDGE_PORT=$NEW_PORT\"/" "$SERVICE_FILE"
    else
        sudo sed -i "/\[Service\]/a Environment=\"BRIDGE_PORT=$NEW_PORT\"" "$SERVICE_FILE"
    fi
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    # Restart service if running
    if systemctl is-active --quiet minhos-sierra-client; then
        echo "  → Restarting sierra client service..."
        sudo systemctl restart minhos-sierra-client
        sleep 2
        
        # Check if service is running
        if systemctl is-active --quiet minhos-sierra-client; then
            echo -e "  → Service restarted ${GREEN}successfully${NC}"
        else
            echo -e "  → Service restart ${RED}failed${NC}"
            echo "    Check logs: sudo journalctl -u minhos-sierra-client -n 50"
        fi
    fi
else
    echo "  → Skipping systemd update (service not found or no sudo access)"
fi

echo ""
echo -e "${GREEN}Configuration updated successfully!${NC}"
echo ""
echo "New Bridge Configuration:"
echo "  Host: $NEW_HOST"
echo "  Port: $NEW_PORT"
echo "  URL: http://$NEW_HOST:$NEW_PORT"
echo ""

# Test the optimized client
echo "Testing optimized client connection..."
if python3 -c "import sys; sys.path.insert(0, '$MINHOS_DIR'); from minhos.services.sierra_client import SierraClient; print('✓ Client module loaded successfully')" 2>/dev/null; then
    echo ""
    echo "You can now:"
    echo "  1. Monitor service logs: sudo journalctl -u minhos-sierra-client -f"
    echo "  2. Run diagnostics: python3 $MINHOS_DIR/scripts/diagnose_streaming.py"
    echo "  3. Test client: python3 $MINHOS_DIR/scripts/test_optimized_client.py"
else
    echo -e "${YELLOW}Note: Could not load client module for testing${NC}"
fi

echo ""
echo "Configuration complete!"