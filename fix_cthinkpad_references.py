#!/usr/bin/env python3
"""
Fix all cthinkpad references in documentation and replace with marypc
"""

import os
import re
from pathlib import Path

def replace_cthinkpad_references():
    """Replace all cthinkpad references with marypc in documentation files"""
    
    # Files that contain cthinkpad references (from grep search)
    files_to_fix = [
        "implementation/sierra_chart_data_enhancement/QUICK_START_NEXT_SESSION.md",
        "implementation/sierra_chart_data_enhancement/phase1_immediate_fixes/HANDOFF_PROMPT.md",
        "implementation/sierra_chart_data_enhancement/phase1_immediate_fixes/task_1_1_1_results.md",
        "implementation/sierra_chart_data_enhancement/SESSION_SUMMARY_2025_07_24.md",
        "User/MINHOS_COMPLETE_SYSTEM_DOCUMENTATION.md",
        "PHASE_3_PRODUCTION_DEPLOYMENT_COMPLETE.md",
        "PRODUCTION_DEPLOYMENT_TODO.md",
        "MONDAY_DEPLOYMENT_CHECKLIST.md",
        "NEXT_SESSION_ROADMAP.md",
        "windows/acsil_studies/README.md",
        "windows/acsil_studies/TRADE_EXECUTION_GUIDE.md",
        "windows/switch to new host/RECONFIGURE_SIERRA_HOST.md",
        "windows/switch to new host/QUICK_RECONFIGURE_GUIDE.md",
        "docs/SESSION_SUMMARY_2025_01_24.md",
        "docs/technical/STREAMING_FIX_GUIDE.md",
        "docs/archive/implementation/sierra_chart_data_enhancement/SESSION_SUMMARY_2025_07_24.md",
        "docs/archive/implementation/sierra_chart_data_enhancement/QUICK_START_NEXT_SESSION.md",
        "docs/archive/implementation/sierra_chart_data_enhancement/phase1_immediate_fixes/task_1_1_1_results.md",
        "docs/archive/implementation/sierra_chart_data_enhancement/phase1_immediate_fixes/HANDOFF_PROMPT.md",
        "docs/archive/implementation/service_architecture_redesign_v2/IMPLEMENTATION_V2_FEATURE_MAPPING.md",
        "docs/archive/implementation/service_architecture_redesign_v2/IMPLEMENTATION_V2_COMPLETE.md",
        "REAL_DATA_STATUS_REPORT.md"
    ]
    
    base_dir = Path(__file__).parent
    replacements_made = 0
    files_updated = 0
    
    print("🔧 Fixing cthinkpad references...")
    print("=" * 50)
    
    for file_path in files_to_fix:
        full_path = base_dir / file_path
        
        if not full_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue
            
        try:
            # Read file content
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Replace all variations of cthinkpad references
            replacements = [
                (r'cthinkpad:8765', 'marypc:8765'),
                (r'http://cthinkpad:8765', 'http://marypc:8765'),
                (r'ws://cthinkpad:8765', 'ws://marypc:8765'),
                (r'`cthinkpad`', '`marypc`'),
                (r'"cthinkpad"', '"marypc"'),
                (r"'cthinkpad'", "'marypc'"),
                (r'cthinkpad\.', 'marypc.'),
                (r'cthinkpad\s', 'marypc '),
                (r'cthinkpad\)', 'marypc)'),
                (r'cthinkpad\]', 'marypc]'),
                (r'cthinkpad$', 'marypc'),
                # Handle IP address references that might be outdated
                (r'100\.85\.224\.58', '100.123.37.79'),  # Update to current marypc IP
            ]
            
            file_replacements = 0
            for pattern, replacement in replacements:
                new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                if new_content != content:
                    matches = len(re.findall(pattern, content, flags=re.IGNORECASE))
                    file_replacements += matches
                    content = new_content
            
            # Write back if changes were made
            if content != original_content:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                files_updated += 1
                replacements_made += file_replacements
                print(f"✅ Updated {file_path} ({file_replacements} replacements)")
            else:
                print(f"⏭️  No changes needed: {file_path}")
                
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    print("=" * 50)
    print(f"🎉 Complete! Updated {files_updated} files with {replacements_made} replacements")
    
    return files_updated, replacements_made

def verify_current_config():
    """Verify current configuration settings"""
    print("\n🔍 Current Configuration Status:")
    print("=" * 50)
    
    # Check .env file
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print("✅ .env file exists")
        try:
            with open(env_file, 'r') as f:
                env_content = f.read()
            
            # Look for bridge-related settings
            if 'BRIDGE_HOSTNAME' in env_content:
                for line in env_content.split('\n'):
                    if 'BRIDGE_HOSTNAME' in line and not line.strip().startswith('#'):
                        print(f"   {line.strip()}")
            
            if 'SIERRA_HOST' in env_content:
                for line in env_content.split('\n'):
                    if 'SIERRA_HOST' in line and not line.strip().startswith('#'):
                        print(f"   {line.strip()}")
                        
        except Exception as e:
            print(f"❌ Error reading .env: {e}")
    else:
        print("⚠️  .env file not found")
    
    # Check .env.example
    env_example = Path(__file__).parent / ".env.example"
    if env_example.exists():
        print("✅ .env.example shows SIERRA_HOST=trading-pc")
    
    # Check main config.py
    config_file = Path(__file__).parent / "config.py"
    if config_file.exists():
        print("✅ config.py uses environment variables with marypc IP fallback")
    
    print("\n🎯 Recommended Next Steps:")
    print("1. Ensure .env file has: BRIDGE_HOSTNAME=marypc")
    print("2. Verify marypc bridge service is running on port 8765")
    print("3. Test connection: curl http://marypc:8765/health")
    print("4. Restart Minh OS")

if __name__ == "__main__":
    # Fix all documentation references
    files_updated, replacements_made = replace_cthinkpad_references()
    
    # Verify current configuration
    verify_current_config()
    
    print(f"\n🚀 Ready to test! Run: python minh.py")
