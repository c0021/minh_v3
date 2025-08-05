#!/usr/bin/env python
"""Start the MinhOS Bridge directly"""
import os
import sys
import subprocess

# Change to the bridge installation directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Use the virtual environment Python
venv_python = os.path.join("venv", "Scripts", "python.exe")

if os.path.exists(venv_python):
    # Run bridge.py with the venv Python
    subprocess.run([venv_python, "bridge.py"])
else:
    print("Virtual environment not found. Running with system Python...")
    subprocess.run([sys.executable, "bridge.py"])