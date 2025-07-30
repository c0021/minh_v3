#!/usr/bin/env python3
"""
MinhOS v3 Configuration - Network and Bridge Settings
"""

import os
from pathlib import Path

# Bridge Configuration  
# Updated to use MaryPC Tailscale IP (100.123.37.79)
BRIDGE_HOSTNAME = os.getenv("BRIDGE_HOSTNAME", "100.123.37.79")
BRIDGE_PORT = int(os.getenv("BRIDGE_PORT", "8765"))
BRIDGE_URL = f"http://{BRIDGE_HOSTNAME}:{BRIDGE_PORT}"

# Alternative IPs if hostname doesn't work
BRIDGE_IPS = [
    "100.123.37.79", # MaryPC Tailscale IP (current working)
    "100.85.224.58", # CThinkPad Tailscale IP (fallback)
    "172.21.128.1",  # Windows host IP from WSL (fallback)
    "marypc",        # MaryPC hostname (fallback)
    "cthinkpad",     # CThinkPad hostname (fallback)
]

# Connection settings
CONNECTION_TIMEOUT = 10  # seconds
RETRY_ATTEMPTS = 3
RETRY_DELAY = 2  # seconds

# Market data settings
MARKET_DATA_REFRESH_RATE = 1.0  # seconds
WEBSOCKET_RECONNECT_DELAY = 5  # seconds

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = Path("minhos_client.log")

print(f"Bridge URL configured as: {BRIDGE_URL}")
print("To change, set environment variables:")
print("  export BRIDGE_HOSTNAME='your-tailscale-hostname'")
print("  export BRIDGE_PORT=8765")