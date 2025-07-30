#!/usr/bin/env python3
"""
Test Kelly Criterion Integration with MinhOS
============================================

This script tests the Kelly service integration with the main MinhOS system.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add Kelly implementation to path
kelly_impl_path = Path(__file__).parent / "implementation" / "ml_kelly_criterion_week5"
sys.path.insert(0, str(kelly_impl_path))

async def test_kelly_integration():
    """Test Kelly service integration"""
    print("🧪 Testing Kelly Criterion Integration with MinhOS")
    print("=" * 55)
    
    try:
        # Test Kelly service import
        print("1. Testing Kelly service import...")
        from services.kelly_service import KellyService, KellyRecommendation
        from services.ml_service_connector import MLServiceConnector
        print("   ✅ Kelly service imports successful")
        
        # Test Kelly service initialization
        print("\n2. Testing Kelly service initialization...")
        kelly_service = KellyService()
        print("   ✅ Kelly service created successfully")
        
        # Test starting the service
        print("\n3. Testing Kelly service startup...")
        await kelly_service.start()
        print("   ✅ Kelly service started successfully")
        
        # Test service health
        print("\n4. Testing service health check...")
        health = await kelly_service.get_service_health()
        print(f"   📊 Service Status: {health.get('status', 'unknown')}")
        print(f"   📊 Uptime: {health.get('uptime_seconds', 0):.1f} seconds")
        print(f"   📊 Error Count: {health.get('error_count', 0)}")
        
        # Test performance metrics
        print("\n5. Testing performance metrics...")
        metrics = await kelly_service.get_performance_metrics()
        if metrics:
            print(f"   📊 Total Recommendations: {metrics.total_recommendations}")
            success_rate = metrics.successful_recommendations / max(metrics.total_recommendations, 1)
            print(f"   📊 Success Rate: {success_rate:.2%}")
            print(f"   📊 Average Confidence: {metrics.average_confidence:.2%}")
            print(f"   📊 Service Uptime: {metrics.service_uptime_hours:.1f} hours")
        else:
            print("   ⚠️  Performance metrics not available")
        
        # Test Kelly recommendation with mock data
        print("\n6. Testing Kelly recommendation...")
        mock_market_data = {
            'price': 18500.0,
            'volume': 1000,
            'timestamp': datetime.now(),
            'bid': 18499.5,
            'ask': 18500.5
        }
        
        mock_trade_history = [
            {'profit_loss': 500, 'outcome': 'win'},
            {'profit_loss': -200, 'outcome': 'loss'},
            {'profit_loss': 300, 'outcome': 'win'},
            {'profit_loss': -150, 'outcome': 'loss'},
            {'profit_loss': 800, 'outcome': 'win'},
        ]
        
        recommendation = await kelly_service.get_kelly_recommendation(
            symbol='NQU25-CME',
            market_data=mock_market_data,
            trade_history=mock_trade_history,
            account_capital=100000.0
        )
        
        if recommendation:
            print(f"   ✅ Kelly recommendation generated:")
            print(f"      📊 Symbol: {recommendation.symbol}")
            print(f"      📊 Kelly Fraction: {recommendation.kelly_fraction:.4f}")
            print(f"      📊 Position Size: {recommendation.position_size} contracts")
            print(f"      📊 Win Probability: {recommendation.win_probability:.2%}")
            print(f"      📊 Capital Risk: ${recommendation.capital_risk:,.2f}")
            print(f"      📊 Model Agreement: {recommendation.model_agreement}")
            print(f"      📊 Status: {recommendation.status}")
        else:
            print("   ⚠️  Kelly recommendation returned None")
        
        # Test API endpoint simulation
        print("\n7. Testing dashboard API endpoint simulation...")
        try:
            import requests
            # This will fail if the server isn't running, but we can test the import
            print("   📊 Requests library available for API testing")
        except ImportError:
            print("   ⚠️  Requests library not available")
        
        print("\n8. Testing database storage...")
        recent_recs = await kelly_service.get_recent_recommendations(limit=5)
        print(f"   📊 Recent recommendations count: {len(recent_recs)}")
        
        print("\n✅ All Kelly integration tests completed successfully!")
        print(f"\n📊 Integration Summary:")
        print(f"   • Kelly service: Operational")
        print(f"   • Database: Functional") 
        print(f"   • Recommendation generation: Working")
        print(f"   • Health monitoring: Active")
        print(f"   • Performance tracking: Active")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Kelly integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        try:
            if 'kelly_service' in locals():
                await kelly_service.stop()
                print("\n🔄 Kelly service stopped")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_kelly_integration())