#!/usr/bin/env python3
"""
Simple Alert System Test
========================
Test the alert system functionality without complex setup.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_alert_system():
    """Test basic alert system functionality"""
    print("🧪 Testing MinhOS Alert System")
    print("=" * 40)
    
    try:
        # Import alert system
        from minhos.services.alert_system import AlertSystem
        
        print("✅ Alert system imported successfully")
        
        # Create instance
        alert_system = AlertSystem()
        print("✅ Alert system instance created")
        
        # Test initialization
        await alert_system._initialize()
        print("✅ Alert system initialized")
        
        # Test process finding
        await alert_system._find_minhos_process()
        if alert_system.minhos_pid:
            print(f"✅ Found MinhOS process: PID {alert_system.minhos_pid}")
        else:
            print("⚠️ MinhOS process not found (this is OK if not running)")
        
        # Test basic monitoring functions
        print("\n🔍 Testing monitoring functions...")
        
        # Test process health check
        await alert_system._check_process_health()
        print("✅ Process health check completed")
        
        # Test service health check
        await alert_system._check_service_health()
        print("✅ Service health check completed")
        
        # Test bridge connectivity check
        await alert_system._check_bridge_connectivity()
        print("✅ Bridge connectivity check completed")
        
        # Show active alerts
        active_alerts = alert_system.get_active_alerts()
        print(f"\n📊 Active alerts: {len(active_alerts)}")
        
        if active_alerts:
            for alert in active_alerts:
                print(f"  • {alert['severity'].upper()}: {alert['title']}")
        
        print("\n✅ Alert system test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Alert system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    success = await test_alert_system()
    
    if success:
        print("\n🎉 Alert System is working!")
        print("\n📋 To enable email notifications:")
        print("1. Set environment variables:")
        print("   export MINHOS_ALERT_EMAIL_USER='your-email@gmail.com'")
        print("   export MINHOS_ALERT_EMAIL_PASSWORD='your-app-password'")
        print("   export MINHOS_ALERT_RECIPIENT_EMAIL='recipient@email.com'")
        print("\n2. Start the alert system:")
        print("   python3 -c \"import asyncio; from minhos.services.alert_system import create_alert_system; asyncio.run(create_alert_system())\"")
        
        print("\n📧 Gmail App Password Setup:")
        print("1. Go to Google Account settings")
        print("2. Enable 2-factor authentication")
        print("3. Generate an App Password for 'Mail'")
        print("4. Use that password (not your regular password)")
    else:
        print("\n❌ Alert system needs fixes before it can be used")

if __name__ == "__main__":
    asyncio.run(main())
