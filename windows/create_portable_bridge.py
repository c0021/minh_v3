#!/usr/bin/env python3
"""
MinhOS Bridge Portable Package Creator
=====================================

Creates a portable, self-contained bridge installation package that can be 
deployed on any new Windows machine.

Usage:
    python3 create_portable_bridge.py [output_directory]

Output:
    Creates a complete bridge installation package with:
    - All required Python files
    - Installation scripts
    - Documentation
    - Testing tools
"""

import shutil
import os
import zipfile
from pathlib import Path
import tempfile
from datetime import datetime

def create_portable_bridge(output_dir=None):
    """Create portable bridge installation package"""
    
    # Get current directory (should be minh_v3/windows)
    current_dir = Path(__file__).parent
    
    # Default output directory
    if output_dir is None:
        output_dir = current_dir / "portable_packages"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True)
    
    # Create timestamp for package
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"MinhOS_Bridge_v3_{timestamp}"
    package_dir = output_dir / package_name
    
    print(f"🚀 Creating portable bridge package: {package_name}")
    print("="*60)
    
    # Create package directory
    package_dir.mkdir(exist_ok=True)
    
    # Core files to include
    core_files = [
        "bridge_installation/bridge.py",
        "bridge_installation/file_access_api.py", 
        "bridge_installation/requirements.txt",
        "bridge_installation/start_bridge.bat"
    ]
    
    # Documentation files
    doc_files = [
        "README.md",
        "CLEAN_INSTALLATION_GUIDE.md",
        "WINDSURF_IMPLEMENTATION_GUIDE.md"
    ]
    
    # Testing files
    test_files = [
        "test_file_api.bat",
        "test_file_api.ps1"
    ]
    
    # Copy core files
    print("📁 Copying core bridge files...")
    for file_path in core_files:
        src = current_dir / file_path
        dst = package_dir / Path(file_path).name
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✅ {Path(file_path).name}")
        else:
            print(f"  ❌ {file_path} not found")
    
    # Copy documentation
    print("\n📖 Copying documentation...")
    docs_dir = package_dir / "docs"
    docs_dir.mkdir(exist_ok=True)
    
    for file_path in doc_files:
        src = current_dir / file_path
        dst = docs_dir / Path(file_path).name
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✅ {Path(file_path).name}")
    
    # Copy testing tools
    print("\n🧪 Copying testing tools...")
    tests_dir = package_dir / "tests"
    tests_dir.mkdir(exist_ok=True)
    
    for file_path in test_files:
        src = current_dir / file_path
        dst = tests_dir / Path(file_path).name
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✅ {Path(file_path).name}")
    
    # Create installation script
    print("\n🔧 Creating installation script...")
    create_install_script(package_dir)
    
    # Create setup verification script
    create_verify_script(package_dir)
    
    # Create package README
    create_package_readme(package_dir, package_name)
    
    # Create ZIP archive
    print("\n📦 Creating ZIP package...")
    zip_path = output_dir / f"{package_name}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(package_dir)
                zipf.write(file_path, arc_path)
    
    # Clean up temporary directory
    shutil.rmtree(package_dir)
    
    print(f"\n✅ Portable package created: {zip_path}")
    print(f"📊 Package size: {zip_path.stat().st_size // 1024} KB")
    print("\n🎯 Deployment Instructions:")
    print("1. Copy ZIP file to new Windows machine")
    print("2. Extract to \\Sync\\minh_v3\\windows\\bridge_installation\\")
    print("3. Run install.bat as Administrator")
    print("4. Run verify.bat to test installation")
    print("5. Run start_bridge.bat to start bridge")
    
    return zip_path

def create_install_script(package_dir):
    """Create automated installation script"""
    install_script = package_dir / "install.bat"
    
    script_content = '''@echo off
echo MinhOS Bridge - Automated Installation
echo =====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.8+ first.
    echo Download from: https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo ✅ Python found: 
python --version

REM Create virtual environment
echo.
echo 📦 Creating Python virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment and install dependencies
echo.
echo 📚 Installing dependencies...
call venv\\Scripts\\activate
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ✅ Installation completed successfully!
echo.
echo 🎯 Next steps:
echo   1. Run verify.bat to test the installation
echo   2. Configure Tailscale on this machine
echo   3. Update Linux MinhOS config with this machine's hostname
echo   4. Run start_bridge.bat to start the bridge
echo.
pause
'''
    
    install_script.write_text(script_content)
    print("  ✅ install.bat")

def create_verify_script(package_dir):
    """Create installation verification script"""
    verify_script = package_dir / "verify.bat"
    
    script_content = '''@echo off
echo MinhOS Bridge - Installation Verification
echo ========================================
echo.

REM Check Python virtual environment
if not exist "venv\\Scripts\\python.exe" (
    echo ❌ Virtual environment not found
    echo Run install.bat first
    pause
    exit /b 1
)

echo ✅ Virtual environment found

REM Check Python packages
echo.
echo 📦 Checking installed packages...
call venv\\Scripts\\activate
pip list | findstr fastapi >nul
if %errorlevel% neq 0 (
    echo ❌ FastAPI not installed
    pause
    exit /b 1
)
echo ✅ FastAPI installed

pip list | findstr uvicorn >nul  
if %errorlevel% neq 0 (
    echo ❌ Uvicorn not installed
    pause
    exit /b 1
)
echo ✅ Uvicorn installed

REM Check required files
echo.
echo 📁 Checking required files...
if not exist "bridge.py" (
    echo ❌ bridge.py not found
    pause
    exit /b 1
)
echo ✅ bridge.py found

if not exist "file_access_api.py" (
    echo ❌ file_access_api.py not found  
    pause
    exit /b 1
)
echo ✅ file_access_api.py found

echo.
echo ✅ All verification checks passed!
echo.
echo 🚀 Ready to start bridge with: start_bridge.bat
echo.
pause
'''
    
    verify_script.write_text(script_content)
    print("  ✅ verify.bat")

def create_package_readme(package_dir, package_name):
    """Create package-specific README"""
    readme_path = package_dir / "PACKAGE_README.md"
    
    readme_content = f'''# {package_name}
## Portable MinhOS Bridge Installation Package

This package contains everything needed to install the MinhOS Windows Bridge on a new machine.

## 🚀 Quick Installation (5 minutes)

### Step 1: Extract Package
Extract this ZIP file to `\\Sync\\minh_v3\\windows\\bridge_installation\\` (replacing existing files)

### Step 2: Install Python (if not already installed)
1. Download Python 3.8+ from https://python.org/downloads/
2. **IMPORTANT**: Check "Add Python to PATH" during installation

### Step 3: Run Automated Installation
```cmd
install.bat
```

### Step 4: Verify Installation
```cmd
verify.bat
```

### Step 5: Start Bridge
```cmd
start_bridge.bat
```

## 📁 Package Contents

- **bridge.py** - Main bridge application with historical data support
- **file_access_api.py** - Sierra Chart file access API
- **requirements.txt** - Python dependencies
- **start_bridge.bat** - Bridge startup script
- **install.bat** - Automated installation script
- **verify.bat** - Installation verification script
- **docs/** - Complete documentation
- **tests/** - Testing scripts

## 🔧 Network Configuration

After installation, update your Linux MinhOS configuration:

```python
# In minhos/core/config.py
SIERRA_HOST = "your-windows-machine-name"  # Update this
```

## ✅ Success Indicators

Bridge is working when you see:
```
INFO:     Sierra Chart File Access API initialized
INFO:     Uvicorn running on http://0.0.0.0:8765
```

## 📖 Documentation

See `docs/` folder for:
- **CLEAN_INSTALLATION_GUIDE.md** - Complete setup guide
- **README.md** - General overview
- **WINDSURF_IMPLEMENTATION_GUIDE.md** - Development guide

## 🧪 Testing

Use scripts in `tests/` folder:
- **test_file_api.bat** - Quick API test
- **test_file_api.ps1** - Comprehensive test suite

## 🎯 Expected Results

Once installed, this bridge enables:
- Real-time market data streaming from Sierra Chart
- Historical data access (.dly and .scid files)
- Secure file system API with path validation
- Integration with Linux MinhOS system via Tailscale

**Total setup time: 5-10 minutes**
**Result: Complete bridge installation ready for production use** 🚀
'''
    
    readme_path.write_text(readme_content)
    print("  ✅ PACKAGE_README.md")

if __name__ == "__main__":
    import sys
    
    output_dir = sys.argv[1] if len(sys.argv) > 1 else None
    package_path = create_portable_bridge(output_dir)
    
    print(f"\n🎉 Portable bridge package ready: {package_path}")