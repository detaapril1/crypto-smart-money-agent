"""
Configuration management for the Crypto Smart Money AI Agent
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Application configuration"""
    
    # App Info
    app_name: str = "Crypto Smart Money AI Agent"
    version: str = "1.0.0"
    environment: str = "production"
    
    # API Keys
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    dexscreener_api_key: str = ""
    openrouter_api_key: str = ""
    gemini_api_key: str = ""
    helius_api_key: str = ""
    birdeye_api_key: str = ""
    
    # Database
    database_url: str = "sqlite:///data/crypto_agent.db"
    database_type: str = "sqlite"
    
    # Scanning Configuration
    scan_interval: int = 300  # 5 minutes
    max_concurrent_scans: int = 10
    min_liquidity: float = 20000
    min_market_cap: float = 50000
    
    # AI Configuration
    ai_provider: str = "openrouter"  # or "gemini"
    ai_model: str = "meta-llama/llama-2-70b-chat"
    ai_temperature: float = 0.7
    ai_max_tokens: int = 1000
    
    # Performance Tracking
    performance_check_intervals: list = None  # [15, 60, 240, 1440] minutes
    performance_retention_days: int = 90
    
    # Telegram Alert Configuration
    alert_cooldown: int = 300  # 5 minutes between same token alerts
    max_daily_alerts: int = 50
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/crypto_agent.log"
    
    # VPS Configuration
    vps_host: str = "localhost"
    vps_port: int = 8000
    enable_api: bool = True
    
    def __post_init__(self):
        """Initialize default performance check intervals"""
        if self.performance_check_intervals is None:
            self.performance_check_intervals = [15, 60, 240, 1440]
        
        # Create logs directory if it doesn't exist
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)


def load_config() -> Config:
    """Load configuration from environment variables"""
    
    # Read from .env file if it exists
    env_file = Path(".env")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    config = Config(
        # App Config
        app_name=os.getenv("APP_NAME", "Crypto Smart Money AI Agent"),
        version=os.getenv("VERSION", "1.0.0"),
        environment=os.getenv("ENVIRONMENT", "production"),
        
        # API Keys
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
        dexscreener_api_key=os.getenv("DEXSCREENER_API_KEY", ""),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        helius_api_key=os.getenv("HELIUS_API_KEY", ""),
        birdeye_api_key=os.getenv("BIRDEYE_API_KEY", ""),
        
        # Database
        database_url=os.getenv("DATABASE_URL", "sqlite:///data/crypto_agent.db"),
        database_type=os.getenv("DATABASE_TYPE", "sqlite"),
        
        # Scanning
        scan_interval=int(os.getenv("SCAN_INTERVAL", "300")),
        max_concurrent_scans=int(os.getenv("MAX_CONCURRENT_SCANS", "10")),
        min_liquidity=float(os.getenv("MIN_LIQUIDITY", "20000")),
        min_market_cap=float(os.getenv("MIN_MARKET_CAP", "50000")),
        
        # AI
        ai_provider=os.getenv("AI_PROVIDER", "openrouter"),
        ai_model=os.getenv("AI_MODEL", "meta-llama/llama-2-70b-chat"),
        ai_temperature=float(os.getenv("AI_TEMPERATURE", "0.7")),
        ai_max_tokens=int(os.getenv("AI_MAX_TOKENS", "1000")),
        
        # Telegram
        alert_cooldown=int(os.getenv("ALERT_COOLDOWN", "300")),
        max_daily_alerts=int(os.getenv("MAX_DAILY_ALERTS", "50")),
        
        # Logging
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_file=os.getenv("LOG_FILE", "logs/crypto_agent.log"),
        
        # VPS
        vps_host=os.getenv("VPS_HOST", "localhost"),
        vps_port=int(os.getenv("VPS_PORT", "8000")),
        enable_api=os.getenv("ENABLE_API", "true").lower() == "true",
    )
    
    # Validate required keys
    required_keys = [
        "telegram_bot_token",
        "telegram_chat_id",
        "openrouter_api_key"
    ]
    
    missing_keys = [key for key in required_keys if not getattr(config, key)]
    if missing_keys:
        logger.warning(f"⚠️  Missing required environment variables: {', '.join(missing_keys)}")
    
    return config


def save_config_template():
    """Save a .env.example template file"""
    template = """# ============================================
# Crypto Smart Money AI Agent Configuration
# ============================================

# Application
APP_NAME=Crypto Smart Money AI Agent
VERSION=1.0.0
ENVIRONMENT=production

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# API Keys
DEXSCREENER_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
HELIUS_API_KEY=your_key_here
BIRDEYE_API_KEY=your_key_here

# Database
DATABASE_URL=sqlite:///data/crypto_agent.db
DATABASE_TYPE=sqlite

# Scanning Configuration
SCAN_INTERVAL=300
MAX_CONCURRENT_SCANS=10
MIN_LIQUIDITY=20000
MIN_MARKET_CAP=50000

# AI Configuration
AI_PROVIDER=openrouter
AI_MODEL=meta-llama/llama-2-70b-chat
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=1000

# Telegram Alerts
ALERT_COOLDOWN=300
MAX_DAILY_ALERTS=50

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/crypto_agent.log

# VPS Configuration
VPS_HOST=localhost
VPS_PORT=8000
ENABLE_API=true
"""
    
    with open(".env.example", "w") as f:
        f.write(template)
    
    logger.info("📝 .env.example template created")
