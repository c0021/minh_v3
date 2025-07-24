#!/bin/bash
# MinhOS v3.1 Data Backup Script
# Backs up all critical MinhOS data with timestamps

set -e

MINHOS_ROOT="/home/colindo/Sync/minh_v3"
BACKUP_DIR="/home/colindo/Sync/minh_v3/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_PATH="$BACKUP_DIR/minhos_backup_$TIMESTAMP"

# Create backup directory
mkdir -p "$BACKUP_PATH"

echo "🔄 Starting MinhOS Data Backup - $TIMESTAMP"

# Backup SQLite databases
echo "📊 Backing up databases..."
cp "$MINHOS_ROOT/data"/*.db "$BACKUP_PATH/" 2>/dev/null || echo "⚠️ No databases found in data/"

# Backup configuration files
echo "⚙️ Backing up configuration..."
cp "$MINHOS_ROOT/minhos/core/config.py" "$BACKUP_PATH/config_backup.py"
[ -f "$MINHOS_ROOT/.env" ] && cp "$MINHOS_ROOT/.env" "$BACKUP_PATH/env_backup"

# Backup logs (last 7 days)
echo "📝 Backing up recent logs..."
find "$MINHOS_ROOT/logs" -name "*.log" -mtime -7 -exec cp {} "$BACKUP_PATH/" \; 2>/dev/null || echo "⚠️ No recent logs found"

# Create backup summary
echo "📋 Creating backup summary..."
cat > "$BACKUP_PATH/backup_info.txt" << EOF
MinhOS v3.1 Data Backup
Timestamp: $TIMESTAMP
Backup Path: $BACKUP_PATH

Files Backed Up:
$(ls -la "$BACKUP_PATH/")

System Status at Backup:
$(ps aux | grep python | grep minh || echo "MinhOS not running")

Data Directory Status:
$(ls -la "$MINHOS_ROOT/data/" 2>/dev/null || echo "Data directory not found")
EOF

# Compress the backup
echo "🗜️ Compressing backup..."
cd "$BACKUP_DIR"
tar -czf "minhos_backup_$TIMESTAMP.tar.gz" "minhos_backup_$TIMESTAMP"
rm -rf "minhos_backup_$TIMESTAMP"

# Clean up old backups (keep last 30 days)
echo "🧹 Cleaning up old backups..."
find "$BACKUP_DIR" -name "minhos_backup_*.tar.gz" -mtime +30 -delete

echo "✅ Backup completed: $BACKUP_DIR/minhos_backup_$TIMESTAMP.tar.gz"
echo "📊 Backup size: $(du -h "$BACKUP_DIR/minhos_backup_$TIMESTAMP.tar.gz" | cut -f1)"
echo "💾 Available backups: $(ls -1 "$BACKUP_DIR"/minhos_backup_*.tar.gz | wc -l)"