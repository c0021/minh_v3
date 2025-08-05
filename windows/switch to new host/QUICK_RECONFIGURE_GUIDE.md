# Quick Guide: Switching to a New Sierra Chart Windows Machine

## On the New Windows Machine:

1. **Copy the `/windows` folder** from your MinhOS installation
2. **Run PowerShell as Administrator**:
   ```powershell
   cd C:\path\to\windows
   .\setup_new_bridge.ps1
   ```
3. **Start Sierra Chart** with your trading charts
4. **Run the Bridge API**:
   ```batch
   C:\MinhOS_Bridge\start_bridge.bat
   ```

## On your Linux Machine (MinhOS):

1. **Switch to the new host** (use hostname or IP):
   ```bash
   # Using hostname
   ./scripts/switch_bridge_host.sh new-windows-pc
   
   # Using IP address
   ./scripts/switch_bridge_host.sh 192.168.1.100
   ```

2. **Verify it's working**:
   ```bash
   # Check service status
   sudo systemctl status minhos-sierra-client
   
   # View logs
   sudo journalctl -u minhos-sierra-client -f
   ```

## That's it! 🎉

The system will automatically:
- Update configuration files
- Restart services
- Test the connection

## Configuration Priority:

MinhOS checks for bridge host in this order:
1. Environment variable (`BRIDGE_HOSTNAME`)
2. `.env` file in MinhOS directory
3. Default fallback (`marypc`)

## Troubleshooting:

If connection fails:
- Check Windows Firewall (port 8765)
- Verify Bridge API is running
- Test with: `curl http://new-host:8765/health`
- Run diagnostics: `python3 scripts/diagnose_streaming.py`

## Manual Configuration:

If the script doesn't work, manually set:
```bash
# Option 1: Environment variable
export BRIDGE_HOSTNAME=new-windows-pc
export BRIDGE_PORT=8765

# Option 2: Create .env file
echo "BRIDGE_HOSTNAME=new-windows-pc" > .env
echo "BRIDGE_PORT=8765" >> .env

# Then restart the service
sudo systemctl restart minhos-sierra-client
```