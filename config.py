#!/usr/bin/env python3
"""
MinhOS v3 Configuration - Network and Bridge Settings
"""

import os
from pathlib import Path

# Load environment variables from .env file if it exists
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    os.environ[key] = value
    except Exception as e:
        print(f"Warning: Failed to load .env file: {e}")

# Bridge Configuration  
# Updated to use MaryPC from .env or fallback to Tailscale IP
BRIDGE_HOSTNAME = os.getenv("BRIDGE_HOSTNAME", "100.123.37.79")
BRIDGE_PORT = int(os.getenv("BRIDGE_PORT", "8765"))
BRIDGE_URL = f"http://{BRIDGE_HOSTNAME}:{BRIDGE_PORT}"

# Alternative IPs if hostname doesn't work
BRIDGE_IPS = [
    "100.123.37.79", # MaryPC Tailscale IP (current working)
    "100.85.224.58", # MaryPC Tailscale IP (fallback)
    "172.21.128.1",  # Windows host IP from WSL (fallback)
    "marypc",        # MaryPC hostname (fallback)
    "marypc",     # MaryPC hostname (fallback)
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