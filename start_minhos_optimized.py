#!/usr/bin/env python3
"""
Start MinhOS with WebSocket Optimization
Starts MinhOS system and monitors for WebSocket optimization activation
"""

import subprocess
import sys
import os
import time
from datetime import datetime

def main():
    print("🚀 STARTING MINHOS WITH WEBSOCKET OPTIMIZATION")
    print("=" * 55)
    print(f"📅 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verify configuration
    print("🔧 Configuration Check:")
    
    # Check .env file
    env_file = "/mnt/c/Users/cong7/Sync/minh_v4/.env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('BRIDGE_HOSTNAME='):
                    hostname = line.split('=', 1)[1].strip()
                    print(f"   🌐 Bridge Hostname: {hostname}")
                elif line.startswith('BRIDGE_PORT='):
                    port = line.split('=', 1)[1].strip()
                    print(f"   🔌 Bridge Port: {port}")
    
    print(f"   ✅ WebSocket Optimization: ENABLED by default")
    print(f"   📊 Expected: Event-driven market data streaming")
    print()
    
    print("🎯 Starting MinhOS System...")
    print("=" * 30)
    print()
    print("📋 MONITOR FOR THESE LOG MESSAGES:")
    print("   🚀 '[OPTIMIZED] Market data streaming via optimized WebSocket'")
    print("   🔗 WebSocket connection messages for symbols")
    print("   📈 Delta update messages")
    print("   💾 Client-side caching statistics")
    print()
    print("⚠️  If you see 'Falling back to HTTP polling mode', there may be connectivity issues")
    print()
    print("🔴 Press Ctrl+C to stop MinhOS")
    print("=" * 55)
    print()
    
    # Change to MinhOS directory and start
    os.chdir("/mnt/c/Users/cong7/Sync/minh_v4")
    
    try:
        # Start MinhOS with Python
        result = subprocess.run([
            sys.executable, "minh.py"
        ], check=False)
        
        print(f"\n🏁 MinhOS stopped (exit code: {result.returncode})")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  MinhOS stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting MinhOS: {e}")
        return 1
    
    print("✅ MinhOS session complete")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)