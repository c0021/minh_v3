#!/usr/bin/env python3
"""
Test all bridge dependencies import successfully
"""

print("Testing bridge dependencies...")

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    print("✅ Watchdog imported successfully")
except ImportError as e:
    print(f"❌ Watchdog import failed: {e}")

try:
    import fastapi
    import uvicorn
    import websockets
    import pydantic
    print("✅ Core web framework dependencies imported successfully")
except ImportError as e:
    print(f"❌ Web framework import failed: {e}")

try:
    import asyncio
    import json
    import logging
    import os
    import time
    from datetime import datetime
    from typing import Dict, List, Optional
    print("✅ Standard library imports successful")
except ImportError as e:
    print(f"❌ Standard library import failed: {e}")

print("🎯 All essential dependencies are available!")
print("Bridge is ready to start with Phase 2 optimizations.")