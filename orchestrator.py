"""
Main orchestrator for the Crypto Smart Money AI Agent
Coordinates all components and runs the main loop
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Set
from collections import defaultdict

from app.utils.config import Config
from app.collectors.dexscreener import DexScreenerCollector
from app.analyzers.screening import TokenScreener
from app.analyzers.ai_analyzer import AIAnalyzer
from app.alerts.telegram import TelegramAlerts
from app.database.models import Database, Signal, Performance

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Main orchestrator for the AI trading agent"""
    
    def __init__(self, config: Config):
        """
        Initialize orchestrator
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.db = Database()
        self.collector = DexScreenerCollector()
        self.screener = TokenScreener()
        self.ai_analyzer = AIAnalyzer(
            api_key=config.openrouter_api_key,
            provider=config.ai_provider,
            model=config.ai_model
        )
        self.alerts = TelegramAlerts(
            bot_token=config.telegram_bot_token,
            chat_id=config.telegram_chat_id
        )
        
        # Tracking
        self.last_alert_time: Dict[str, datetime] = defaultdict(lambda: datetime.now() - timedelta(hours=1))
        self.daily_alert_count = 0
        self.processed_tokens: Set[str] = set()
    
    async def initialize(self):
        """Initialize all components"""
        logger.info("📋 Initializing agent components...")
        
        await self.collector.initialize()
        await self.ai_analyzer.initialize()
        await self.alerts.initialize()
        
        # Test Telegram connection
        if not await self.alerts.test_connection():
            logger.warning("⚠️ Telegram connection failed. Alerts will not be sent.")
        
        logger.info("✅ Agent components initialized")
    
    async def run(self):
        """Run the main agent loop"""
        logger.info("🔄 Starting main agent loop...")
        
        try:
            while True:
                try:
                    await self._scan_cycle()
                    await self._evaluate_signals()
                    
                    # Wait before next scan
                    logger.info(f"⏳ Waiting {self.config.scan_interval}s for next scan...")
                    await asyncio.sleep(self.config.scan_interval)
                    
                except Exception as e:
                    logger.error(f"❌ Error in scan cycle: {str(e)}", exc_info=True)
                    await asyncio.sleep(60)  # Wait before retry
                    
        except KeyboardInterrupt:
            logger.info("⏹️  Agent interrupted by user")
            await self.cleanup()
    
    async def _scan_cycle(self):
        """Execute one scan cycle"""
        logger.info("🔍 Starting scan cycle...")
        start_time = datetime.now()
        
        try:
            # Get trending tokens
            tokens = await self.collector.get_trending_tokens(limit=30)
            logger.info(f"📊 Retrieved {len(tokens)} tokens")
            
            if not tokens:
                logger.warning("No tokens retrieved")
                return
            
            # Screen tokens
            screened = self.screener.filter_tokens(tokens, min_score=40)
            logger.info(f"✅ Screened {len(screened)} tokens passed filters")
            
            # Analyze promising candidates
            for screening_result in screened[:self.config.max_concurrent_scans]:
                token = screening_result.token_data
                pair_id = f\"{token.chain}:{token.pair_address}\"
                
                # Skip if already processed recently
                if pair_id in self.processed_tokens:
                    continue
                
                # Skip if alert cooldown not passed
                if not self._check_alert_cooldown(pair_id):
                    continue
                
                # Skip if daily limit reached
                if self.daily_alert_count >= self.config.max_daily_alerts:
                    logger.info(f\"⚠️ Daily alert limit reached ({self.config.max_daily_alerts})\")
                    break
                
                # AI Analysis
                analysis = await self.ai_analyzer.analyze_token(
                    token, screening_result.overall_score
                )
                
                if analysis is None:
                    continue
                
                # Determine alert reason
                alert_reason = self._get_alert_reason(screening_result)
                
                # Send alert if scores are good
                if analysis.confidence_score >= 60 and analysis.bullish_score >= 50:
                    success = await self.alerts.send_alert(
                        token, analysis, screening_result.overall_score, alert_reason
                    )
                    
                    if success:
                        # Save signal to database
                        signal = Signal(
                            token_name=token.token_name,
                            symbol=token.symbol,
                            chain=token.chain,
                            pair_address=token.pair_address,
                            price=token.price,
                            market_cap=token.market_cap,
                            liquidity=token.liquidity,
                            volume_5m=token.volume_5m,
                            volume_1h=token.volume_1h,
                            volume_6h=token.volume_6h,
                            volume_24h=token.volume_24h,
                            buy_count=token.buy_count,
                            sell_count=token.sell_count,
                            buy_sell_ratio=screening_result.token_data.buy_count / max(screening_result.token_data.sell_count, 1),
                            pair_age=token.pair_age,
                            price_change_pct=token.price_change_pct,
                            ai_bullish_score=analysis.bullish_score,
                            ai_confidence_score=analysis.confidence_score,
                            ai_risk_score=analysis.risk_score,
                            ai_reasoning=analysis.reasoning,
                            risks=analysis.risks,
                            smart_money_data=analysis.smart_money_observations,
                            alert_reason=alert_reason,
                            status=\"open\"
                        )
                        
                        signal_id = self.db.insert_signal(signal)
                        logger.info(f\"💾 Signal saved with ID {signal_id}\")
                        
                        # Update tracking
                        self.last_alert_time[pair_id] = datetime.now()
                        self.daily_alert_count += 1
                        self.processed_tokens.add(pair_id)
                
                # Add small delay between analyses
                await asyncio.sleep(1)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f\"✅ Scan cycle completed in {elapsed:.1f}s\")
            
        except Exception as e:
            logger.error(f\"Scan cycle error: {str(e)}\", exc_info=True)
    
    async def _evaluate_signals(self):
        \"\"\"Evaluate performance of recent signals\"\"\"
        try:
            recent_signals = self.db.get_recent_signals(limit=10)
            
            for signal_dict in recent_signals:
                if signal_dict['status'] != 'open':
                    continue
                
                signal = self._dict_to_signal(signal_dict)
                
                # Check performance at each interval
                for interval in self.config.performance_check_intervals:
                    # Simple performance calculation (in real impl, fetch actual price)
                    performance = Performance(
                        signal_id=signal_dict['id'],
                        time_interval_minutes=interval,
                        entry_price=signal.price,
                        current_price=signal.price,  # Would fetch real price
                        highest_price=signal.price,
                        lowest_price=signal.price,
                        percentage_gain=0.0,
                        percentage_loss=0.0,
                        max_drawdown=0.0
                    )
                    
                    # Would save to database in real implementation
        
        except Exception as e:
            logger.error(f\"Signal evaluation error: {str(e)}\")
    
    def _check_alert_cooldown(self, pair_id: str) -> bool:
        \"\"\"Check if alert cooldown has passed\"\"\"
        last_alert = self.last_alert_time.get(pair_id, datetime.now() - timedelta(hours=1))
        cooldown = timedelta(seconds=self.config.alert_cooldown)
        return datetime.now() - last_alert >= cooldown
    
    def _get_alert_reason(self, screening_result) -> str:
        \"\"\"Generate alert reason from screening results\"\"\"
        if screening_result.bullish_signals:
            return screening_result.bullish_signals[0]
        return \"Favorable screening metrics detected\"
    
    def _dict_to_signal(self, signal_dict: Dict) -> Signal:
        \"\"\"Convert database dict to Signal object\"\"\"
        signal = Signal()
        for key, value in signal_dict.items():
            if hasattr(signal, key):
                setattr(signal, key, value)
        return signal
    
    async def cleanup(self):
        \"\"\"Cleanup and close all connections\"\"\"
        logger.info(\"🧹 Cleaning up...\")
        await self.collector.close()
        await self.ai_analyzer.close()
        await self.alerts.close()
        logger.info(\"✅ Cleanup complete\")
