#!/bin/bash
# MinhOS v3.1 Data Restore Script
# Restores MinhOS data from backup

set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    echo "Available backups:"
    ls -1 /home/colindo/Sync/minh_v3/backups/minhos_backup_*.tar.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"
MINHOS_ROOT="/home/colindo/Sync/minh_v3"
RESTORE_DIR="/tmp/minhos_restore_$$"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "🔄 Starting MinhOS Data Restore from: $BACKUP_FILE"

# Extract backup
mkdir -p "$RESTORE_DIR"
cd "$RESTORE_DIR"
tar -xzf "$BACKUP_FILE"

EXTRACTED_DIR=$(ls -1 | head -1)
cd "$EXTRACTED_DIR"

echo "📋 Backup contents:"
cat backup_info.txt

read -p "Continue with restore? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Restore cancelled"
    rm -rf "$RESTORE_DIR"
    exit 1
fi

# Stop MinhOS if running
echo "🛑 Stopping MinhOS..."
pkill -f "python3 minh.py start" || echo "MinhOS not running"
sleep 2

# Backup current data
echo "💾 Backing up current data..."
CURRENT_BACKUP_DIR="$MINHOS_ROOT/backups/pre_restore_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$CURRENT_BACKUP_DIR"
cp -r "$MINHOS_ROOT/data" "$CURRENT_BACKUP_DIR/" 2>/dev/null || echo "No current data to backup"

# Restore databases
echo "📊 Restoring databases..."
mkdir -p "$MINHOS_ROOT/data"
cp *.db "$MINHOS_ROOT/data/" 2>/dev/null || echo "No databases to restore"

# Restore configuration (with confirmation)
if [ -f "config_backup.py" ]; then
    read -p "Restore configuration file? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp config_backup.py "$MINHOS_ROOT/minhos/core/config.py"
        echo "✅ Configuration restored"
    fi
fi

# Clean up
rm -rf "$RESTORE_DIR"

echo "✅ MinhOS data restore completed"
echo "🚀 You can now restart MinhOS with: python3 minh.py start"