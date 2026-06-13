"""
Crypto Smart Money AI Agent - Main Entry Point
Runs the agent continuously on a VPS
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.orchestrator import AgentOrchestrator
from app.utils.logger import setup_logger
from app.utils.config import load_config

logger = setup_logger(__name__)


async def main():
    """Main entry point for the agent"""
    try:
        logger.info("🚀 Starting Crypto Smart Money AI Agent...")
        
        # Load configuration
        config = load_config()
        logger.info(f"Configuration loaded: {config.app_name} v{config.version}")
        
        # Initialize and run orchestrator
        orchestrator = AgentOrchestrator(config)
        await orchestrator.initialize()
        
        logger.info("✅ Agent initialized successfully")
        logger.info("📊 Starting continuous market scanning...")
        
        # Run the agent
        await orchestrator.run()
        
    except KeyboardInterrupt:
        logger.info("⏹️  Shutting down agent...")
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
