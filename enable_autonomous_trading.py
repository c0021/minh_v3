#!/usr/bin/env python3
"""
Enable Fully Autonomous Trading
===============================

This script enables fully autonomous trading by removing all manual approval requirements.
Trade opportunities will be executed in real-time when confidence thresholds are met.
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add path for imports
sys.path.insert(0, str(Path(__file__).parent))

from minhos.services.ml_trading_workflow import get_ml_trading_workflow
from minhos.services.trading_engine import get_trading_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def enable_autonomous_trading():
    """Enable fully autonomous trading across all services"""
    
    logger.info("🚀 Enabling Fully Autonomous Trading...")
    
    # Get services
    ml_workflow = get_ml_trading_workflow()
    trading_engine = get_trading_engine()
    
    # Enable auto trading in ML workflow
    ml_workflow.config['enable_auto_trading'] = True
    logger.info("✅ ML Workflow: Auto-trading ENABLED")
    
    # Enable auto execution in trading engine
    trading_engine.config['auto_execution_enabled'] = True
    logger.info("✅ Trading Engine: Auto-execution ENABLED")
    
    # Show current configuration
    logger.info("\n📊 Current Trading Configuration:")
    logger.info(f"   ML Auto-trading: {ml_workflow.config['enable_auto_trading']}")
    logger.info(f"   Trading Auto-execution: {trading_engine.config['auto_execution_enabled']}")
    logger.info(f"   Min Confidence Threshold: {ml_workflow.config['min_confidence_threshold']}")
    logger.info(f"   Max Position Size: {ml_workflow.config['max_position_size']}")
    logger.info(f"   Max Daily Trades: {ml_workflow.config['max_daily_trades']}")
    
    logger.info("\n⚡ AUTONOMOUS TRADING IS NOW ACTIVE!")
    logger.info("⚠️  WARNING: The system will execute trades automatically without human approval")
    logger.info("📌 Trades will execute when:")
    logger.info("   - ML confidence >= 65%")
    logger.info("   - Risk manager approves")
    logger.info("   - Position limits not exceeded")
    
    return True

async def main():
    """Main entry point"""
    success = await enable_autonomous_trading()
    
    if success:
        logger.info("\n✅ Configuration Updated Successfully")
        logger.info("🏁 System ready for fully autonomous trading")
    else:
        logger.error("\n❌ Configuration update failed")
        
    return 0 if success else 1

if __name__ == "__main__":
    exit(asyncio.run(main()))