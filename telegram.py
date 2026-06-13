"""
Telegram bot for sending trading alerts
"""

import logging
import aiohttp
from typing import Optional
from app.database.models import Signal
from app.analyzers.ai_analyzer import AIAnalysis
from app.collectors.dexscreener import TokenData

logger = logging.getLogger(__name__)


class TelegramAlerts:
    """Telegram alert manager"""
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize Telegram alert sender
        
        Args:
            bot_token: Telegram bot token
            chat_id: Target chat ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Initialize async session"""
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close async session"""
        if self.session:
            await self.session.close()
    
    async def send_alert(self, token: TokenData, analysis: AIAnalysis,
                        screening_score: float, alert_reason: str) -> bool:
        """
        Send trading alert to Telegram
        
        Args:
            token: TokenData object
            analysis: AIAnalysis object
            screening_score: Screening score
            alert_reason: Reason for the alert
            
        Returns:
            True if sent successfully
        """
        try:
            message = self._format_alert_message(
                token, analysis, screening_score, alert_reason
            )
            
            await self._send_message(message)
            logger.info(f"✅ Alert sent for {token.symbol}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send alert: {str(e)}")
            return False
    
    async def send_performance_update(self, signal: Signal, gains: float,
                                     time_interval: int) -> bool:
        """
        Send performance update for a signal
        
        Args:
            signal: Signal object
            gains: Percentage gain/loss
            time_interval: Time interval in minutes
            
        Returns:
            True if sent successfully
        """
        try:
            emoji = "📈" if gains > 0 else "📉"
            message = f\"{emoji} {signal.symbol} Performance Update\\n\\n\"
            message += f\"Time: {time_interval} minutes\\n\"
            message += f\"Entry: ${signal.price:.8f}\\n\"
            message += f\"Gain/Loss: {gains:+.2f}%\\n\"
            message += f\"Status: {'✅ WINNING' if gains > 0 else '❌ LOSING'}\"
            
            await self._send_message(message)
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send performance update: {str(e)}")
            return False
    
    def _format_alert_message(self, token: TokenData, analysis: AIAnalysis,
                             screening_score: float, alert_reason: str) -> str:
        """
        Format alert message for Telegram
        
        Args:
            token: TokenData object
            analysis: AIAnalysis object
            screening_score: Screening score
            alert_reason: Reason for alert
            
        Returns:
            Formatted message string
        """
        buy_sell_ratio = (token.buy_count / token.sell_count) if token.sell_count > 0 else token.buy_count
        
        message = f\"🚀 SMART MONEY ALERT\\n\"
        message += f\"{'='*40}\\n\\n\"
        
        message += f\"💰 Token: {token.token_name} ({token.symbol})\\n\"
        message += f\"🔗 Chain: {token.chain.upper()}\\n\"
        message += f\"💵 Price: ${token.price:.8f}\\n\"
        message += f\"📊 Market Cap: ${token.market_cap:,.0f}\\n\"
        message += f\"💧 Liquidity: ${token.liquidity:,.0f}\\n\"
        message += f\"📈 Volume 1H: ${token.volume_1h:,.0f}\\n\"
        message += f\"⏰ 1H Change: {token.price_change_pct:+.2f}%\\n\\n\"
        
        message += f\"🤖 AI Analysis\\n\"
        message += f\"{'─'*40}\\n\"
        message += f\"🔥 Bullish Score: {analysis.bullish_score:.0f}/100\\n\"
        message += f\"✅ Confidence: {analysis.confidence_score:.0f}/100\\n\"
        message += f\"⚠️ Risk Score: {analysis.risk_score:.0f}/100\\n\\n\"
        
        message += f\"💭 Reasoning:\\n\"
        message += f\"{analysis.reasoning}\\n\\n\"
        
        message += f\"📌 Risks:\\n\"
        message += f\"{analysis.risks}\\n\\n\"
        
        message += f\"🎯 Potential Upside:\\n\"
        message += f\"{analysis.potential_upside}\\n\\n\"
        
        message += f\"📉 Potential Downside:\\n\"
        message += f\"{analysis.potential_downside}\\n\\n\"
        
        message += f\"🐋 Smart Money Activity:\\n\"
        message += f\"{analysis.smart_money_observations}\\n\\n\"
        
        message += f\"Alert Reason: {alert_reason}\\n\"
        message += f\"{'='*40}\"
        
        return message
    
    async def _send_message(self, text: str) -> bool:
        """
        Send message via Telegram API
        
        Args:
            text: Message text
            
        Returns:
            True if sent successfully
        """
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            
            async with self.session.post(
                f\"{self.base_url}/sendMessage\",
                json=payload,
                timeout=10
            ) as response:
                if response.status == 200:
                    return True
                else:
                    logger.error(f\"Telegram API error: {response.status}\")
                    return False
                    
        except Exception as e:
            logger.error(f\"Failed to send Telegram message: {str(e)}\")
            return False
    
    async def test_connection(self) -> bool:
        \"\"\"
        Test Telegram bot connection
        
        Returns:
            True if connection successful
        \"\"\"
        try:
            async with self.session.get(
                f\"{self.base_url}/getMe\",
                timeout=5
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get(\"ok\"):
                        logger.info(f\"✅ Telegram bot connected: {data['result']['username']}\")
                        return True
                    
            logger.error(\"Telegram bot connection failed\")
            return False
            
        except Exception as e:
            logger.error(f\"Telegram connection error: {str(e)}\")
            return False
