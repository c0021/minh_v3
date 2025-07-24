# MinhOS Windows Bridge Directory

This directory contains the Windows bridge components for MinhOS trading system integration with Sierra Chart.

## 🚀 Quick Start - Installation

**For clean installation on any Windows machine:**

```cmd
cd bridge_installation
start_bridge.bat
```

**All installation files and documentation are located in:**
```
📁 bridge_installation/
```

## 📁 Directory Structure

```
windows/
├── bridge_installation/          ⭐ MAIN INSTALLATION
│   ├── README.md                # Complete installation guide
│   ├── bridge.py                # Main bridge application  
│   ├── file_access_api.py       # Historical data access
│   ├── requirements.txt         # Python dependencies
│   ├── start_bridge.bat        # Windows startup script
│   └── start_bridge.ps1        # PowerShell startup script
│
├── create_portable_bridge.py    # Create portable installation package
├── test_file_api.bat           # Test file access API
├── test_file_api.ps1           # Test file access API (PowerShell)
└── switch to new host/         # Host reconfiguration guides
```

## 📖 Documentation

**Primary Documentation:** [bridge_installation/README.md](bridge_installation/README.md)

This contains complete:
- Installation instructions
- API documentation  
- Configuration details
- Troubleshooting guide

## 🔧 Additional Tools

### Testing
- `test_file_api.bat` - Quick batch test of file access API
- `test_file_api.ps1` - Comprehensive PowerShell test suite

### Deployment
- `create_portable_bridge.py` - Creates portable ZIP package for deployment

### Configuration
- `switch to new host/` - Guides for reconfiguring bridge for different machines

## ⚡ Quick Commands

```cmd
# Start bridge (recommended method)
cd bridge_installation && start_bridge.bat

# Test file access API
test_file_api.bat

# Create portable package
python create_portable_bridge.py
```

---

**Note:** All obsolete and confusing documentation has been removed. Use only the files in `bridge_installation/` for current deployment.