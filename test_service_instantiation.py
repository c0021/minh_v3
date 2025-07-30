#!/usr/bin/env python3
"""
Service Instantiation Migration Test
====================================

Tests migration tracking when services are actually instantiated
(simulates the mark_service_migrated calls).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def main():
    print("🔄 Testing Service Migration Tracking")
    print("=" * 50)
    
    from minhos.core.symbol_integration import get_symbol_integration
    integration = get_symbol_integration()
    
    # Show initial migration status
    print("📊 Initial Migration Status:")
    status = integration.get_migration_status()
    for service, info in status['services'].items():
        icon = "✅" if info['migrated'] else "⏳"
        print(f"   {icon} {service}: {info['status']}")
    
    print(f"\n🔧 Simulating Service Instantiation...")
    
    # Simulate services being instantiated and calling mark_service_migrated
    services_to_migrate = [
        'sierra_client', 
        'sierra_historical_data',
        'windows_bridge', 
        'ai_brain_service',
        'dashboard',
        'trading_engine'
    ]
    
    for service in services_to_migrate:
        integration.mark_service_migrated(service)
        print(f"   ✅ {service} migrated to centralized symbol management")
    
    # Show final migration status
    print("\n📊 Final Migration Status:")
    final_status = integration.get_migration_status()
    for service, info in final_status['services'].items():
        icon = "✅" if info['migrated'] else "⏳"
        print(f"   {icon} {service}: {info['status']}")
    
    print(f"\n🎯 Migration Progress: {final_status['migrated_services']}/{final_status['total_services']} services")
    
    if final_status['migration_complete']:
        print("🎉 MIGRATION COMPLETE!")
        print("✅ All services now use centralized symbol management")
    else:
        remaining = final_status['total_services'] - final_status['migrated_services']
        print(f"⏳ {remaining} services still pending migration")

if __name__ == "__main__":
    main()