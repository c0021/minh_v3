# Reconfiguring MinhOS v3 for a Different Sierra Chart Windows Machine

This guide helps you switch your MinhOS installation to connect to Sierra Chart on a different Windows machine.

## Current Configuration

- **Current Bridge Host**: `cthinkpad` (100.85.224.58)
- **Bridge Port**: 8765
- **Bridge URL**: http://cthinkpad:8765

## Steps to Reconfigure for New Windows Machine

### Step 1: Prepare the New Windows Machine

On your new Windows machine with Sierra Chart:

1. **Copy the Bridge API files**:
   - Copy the entire `/windows` folder from your MinhOS installation
   - Key files needed:
     - `bridge.py` - The Bridge API server
     - `tcp_optimize_windows.bat` - TCP optimizations
     - `MinhOSBridgeStudy.cpp` - Sierra Chart study
     - `requirements.txt` - Python dependencies

2. **Install Python and dependencies**:
   ```batch
   # Install Python 3.8+ if not already installed
   # Then install dependencies:
   cd C:\path\to\windows
   pip install -r requirements.txt
   ```

3. **Apply TCP optimizations** (Run as Administrator):
   ```batch
   cd C:\path\to\windows
   tcp_optimize_windows.bat
   ```

4. **Configure Sierra Chart**:
   - Load the `MinhOSBridgeStudy.cpp` study in Sierra Chart
   - Ensure Sierra Chart is running with the charts you need

5. **Start the Bridge API**:
   ```batch
   cd C:\path\to\windows
   python bridge.py
   ```

6. **Note the new machine's hostname or IP**:
   ```batch
   hostname
   ipconfig
   ```

### Step 2: Update MinhOS Configuration

You have several options for updating the bridge host:

#### Option A: Environment Variables (Recommended)

1. **Create a `.env` file**:
   ```bash
   echo "BRIDGE_HOSTNAME=new-windows-pc" > /home/colindo/Sync/minh_v3/.env
   echo "BRIDGE_PORT=8765" >> /home/colindo/Sync/minh_v3/.env
   ```

2. **Or set system environment variables**:
   ```bash
   export BRIDGE_HOSTNAME=new-windows-pc
   export BRIDGE_PORT=8765
   ```

3. **Make it permanent** (add to `~/.bashrc`):
   ```bash
   echo 'export BRIDGE_HOSTNAME=new-windows-pc' >> ~/.bashrc
   echo 'export BRIDGE_PORT=8765' >> ~/.bashrc
   source ~/.bashrc
   ```

#### Option B: Update /etc/hosts (If using hostname)

If your new Windows machine has a hostname:
```bash
sudo nano /etc/hosts
# Add line:
192.168.1.100  new-windows-pc  # Replace with actual IP
```

#### Option C: Direct IP Address

Use the IP address directly:
```bash
export BRIDGE_HOSTNAME=192.168.1.100  # Replace with actual IP
```

### Step 3: Update Service Configuration

1. **Update the systemd service**:
   ```bash
   sudo nano /etc/systemd/system/minhos-sierra-client.service
   ```

2. **Add or modify the Environment variables**:
   ```ini
   Environment="BRIDGE_HOSTNAME=new-windows-pc"
   Environment="BRIDGE_PORT=8765"
   ```

3. **Reload and restart**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart minhos-sierra-client
   ```

### Step 4: Test the New Connection

1. **Test basic connectivity**:
   ```bash
   # Test with curl
   curl http://new-windows-pc:8765/health
   
   # Or with IP
   curl http://192.168.1.100:8765/health
   ```

2. **Run the diagnostic script**:
   ```bash
   python3 /home/colindo/Sync/minh_v3/scripts/diagnose_streaming.py --url http://new-windows-pc:8765/api/market_data
   ```

3. **Test the optimized client**:
   ```bash
   BRIDGE_HOSTNAME=new-windows-pc python3 /home/colindo/Sync/minh_v3/scripts/test_optimized_client.py
   ```

### Step 5: Verify Everything is Working

1. **Check service status**:
   ```bash
   sudo systemctl status minhos-sierra-client
   ```

2. **Monitor logs**:
   ```bash
   sudo journalctl -u minhos-sierra-client -f
   ```

3. **Verify data flow**:
   - Check if market data is being received
   - Verify database is being updated
   - Ensure dashboard shows live data

## Quick Configuration Script

Here's a script to quickly switch between bridge hosts:

```bash
#!/bin/bash
# save as: /home/colindo/Sync/minh_v3/scripts/switch_bridge_host.sh

NEW_HOST=$1
NEW_PORT=${2:-8765}

if [ -z "$NEW_HOST" ]; then
    echo "Usage: $0 <hostname-or-ip> [port]"
    echo "Example: $0 192.168.1.100"
    echo "Example: $0 new-windows-pc 8765"
    exit 1
fi

echo "Switching to Bridge Host: $NEW_HOST:$NEW_PORT"

# Update environment
export BRIDGE_HOSTNAME=$NEW_HOST
export BRIDGE_PORT=$NEW_PORT

# Test connection
echo "Testing connection..."
if curl -s -f "http://$NEW_HOST:$NEW_PORT/health" > /dev/null; then
    echo "✓ Connection successful!"
    
    # Update .env file
    echo "BRIDGE_HOSTNAME=$NEW_HOST" > /home/colindo/Sync/minh_v3/.env
    echo "BRIDGE_PORT=$NEW_PORT" >> /home/colindo/Sync/minh_v3/.env
    
    # Restart service
    echo "Restarting service..."
    sudo systemctl restart minhos-sierra-client
    
    echo "Configuration updated successfully!"
else
    echo "✗ Connection failed! Please check:"
    echo "  1. Bridge API is running on $NEW_HOST"
    echo "  2. Port $NEW_PORT is accessible"
    echo "  3. No firewall blocking the connection"
fi
```

## Troubleshooting

### Common Issues:

1. **Connection Refused**:
   - Ensure Bridge API is running on Windows
   - Check Windows Firewall settings
   - Verify port 8765 is open

2. **Name Resolution Failed**:
   - Use IP address instead of hostname
   - Add entry to /etc/hosts
   - Check DNS settings

3. **High Latency**:
   - Ensure TCP optimizations are applied on new Windows machine
   - Check network path between machines
   - Verify no VPN or proxy interference

4. **Service Won't Start**:
   - Check environment variables are set correctly
   - Verify Python path in service file
   - Review journal logs for errors

## Network Requirements

- **Port**: 8765 (default) must be open on Windows
- **Protocol**: HTTP (TCP)
- **Latency**: Should be <10ms on local network
- **Bandwidth**: Minimal (< 1 Mbps for market data)

## Security Considerations

1. **Firewall**: Only allow connections from MinhOS machine
2. **Authentication**: Consider adding API key authentication
3. **Encryption**: Use HTTPS if over public network
4. **Network**: Preferably use isolated trading network

## Summary

Switching to a new Windows machine requires:
1. Setting up Bridge API on new Windows machine
2. Updating BRIDGE_HOSTNAME environment variable
3. Restarting MinhOS services
4. Testing connectivity and performance

The system is designed to be flexible - just point it to the new bridge host!