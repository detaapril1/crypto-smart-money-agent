"""
Token screening and analysis module
"""

import logging
from typing import List, Optional, Dict
from dataclasses import dataclass
from app.collectors.dexscreener import TokenData

logger = logging.getLogger(__name__)


@dataclass
class ScreeningResult:
    """Result of token screening"""
    token_data: TokenData
    passes_basic_filters: bool
    rejection_reasons: List[str]
    bullish_signals: List[str]
    bearish_signals: List[str]
    risk_flags: List[str]
    overall_score: float


class TokenScreener:
    """Token screening and filtering"""
    
    def __init__(self, config: Dict = None):
        """
        Initialize screener with configuration
        
        Args:
            config: Configuration dictionary with thresholds
        """
        self.config = config or self._get_default_config()
    
    @staticmethod
    def _get_default_config() -> Dict:
        """Get default screening configuration"""
        return {
            "min_liquidity": 20000,
            "min_market_cap": 50000,
            "min_volume_1h": 1000,
            "max_sell_ratio": 0.7,  # Max 70% sells
            "min_pair_age_minutes": 5,
            "max_pair_age_hours": 48,
            "min_buy_sell_count": 5,
            "suspicious_wallet_concentration": 0.5,  # Max 50% in one wallet
        }
    
    def screen_token(self, token: TokenData) -> ScreeningResult:
        """
        Screen a token against filters
        
        Args:
            token: TokenData object to screen
            
        Returns:
            ScreeningResult object
        """
        rejection_reasons = []
        bullish_signals = []
        bearish_signals = []
        risk_flags = []
        
        # Basic filter checks
        
        # 1. Liquidity check
        if token.liquidity < self.config["min_liquidity"]:
            rejection_reasons.append(f"Low liquidity: ${token.liquidity:,.0f}")
        else:
            bullish_signals.append(f"Healthy liquidity: ${token.liquidity:,.0f}")
        
        # 2. Market cap check
        if token.market_cap < self.config["min_market_cap"]:
            rejection_reasons.append(f"Low market cap: ${token.market_cap:,.0f}")
        
        # 3. Volume check
        if token.volume_1h < self.config["min_volume_1h"]:
            rejection_reasons.append(f"Low 1h volume: ${token.volume_1h:,.0f}")
        else:
            bullish_signals.append(f"Strong 1h volume: ${token.volume_1h:,.0f}")
        
        # 4. Buy/Sell pressure
        total_transactions = token.buy_count + token.sell_count
        
        if total_transactions < self.config["min_buy_sell_count"]:
            risk_flags.append(f"Low trading activity: {total_transactions} txns")
        
        if total_transactions > 0:
            sell_ratio = token.sell_count / total_transactions
            if sell_ratio > self.config["max_sell_ratio"]:
                bearish_signals.append(f"High sell pressure: {sell_ratio:.1%} sells")
                risk_flags.append("Excessive selling")
            elif sell_ratio < 0.3:
                bullish_signals.append(f"Strong buy pressure: {sell_ratio:.1%} sells")
        
        # 5. Price momentum
        if token.price_change_pct > 10:
            bullish_signals.append(f"Positive momentum: +{token.price_change_pct:.1f}%")
        elif token.price_change_pct < -10:
            bearish_signals.append(f"Negative momentum: {token.price_change_pct:.1f}%")
        
        # 6. Pair age check
        pair_age_minutes = token.pair_age * 60
        
        if pair_age_minutes < self.config["min_pair_age_minutes"]:
            rejection_reasons.append(f"Pair too new: {pair_age_minutes} minutes old")
        
        if token.pair_age > self.config["max_pair_age_hours"]:
            rejection_reasons.append(f"Pair too old: {token.pair_age} hours")
        
        # 7. Volume growth analysis
        volume_ratio_24h_to_1h = token.volume_24h / token.volume_1h if token.volume_1h > 0 else 0
        
        if volume_ratio_24h_to_1h < 5:
            bullish_signals.append("Recent volume spike detected")
        
        # 8. Check for obvious rug pull indicators
        rug_pull_risk = self._check_rug_pull_indicators(token, risk_flags)
        if rug_pull_risk:
            rejection_reasons.append("⚠️ Potential rug pull indicators detected")
        
        # Determine if passes basic filters
        passes_basic_filters = len(rejection_reasons) == 0
        
        # Calculate overall score (0-100)
        overall_score = self._calculate_overall_score(
            token, bullish_signals, bearish_signals, risk_flags, passes_basic_filters
        )
        
        return ScreeningResult(
            token_data=token,
            passes_basic_filters=passes_basic_filters,
            rejection_reasons=rejection_reasons,
            bullish_signals=bullish_signals,
            bearish_signals=bearish_signals,
            risk_flags=risk_flags,
            overall_score=overall_score
        )
    
    def _check_rug_pull_indicators(self, token: TokenData, risk_flags: List[str]) -> bool:
        """
        Check for rug pull indicators
        
        Args:
            token: TokenData object
            risk_flags: List to append risk flags to
            
        Returns:
            True if rug pull risk detected
        """
        rug_risk = False
        
        # Extremely low liquidity relative to market cap
        if token.market_cap > 0:
            liquidity_ratio = token.liquidity / token.market_cap
            if liquidity_ratio < 0.01:  # Less than 1% liquidity
                risk_flags.append("Dangerously low liquidity ratio")
                rug_risk = True
        
        # No trading activity
        if token.buy_count == 0 and token.sell_count == 0:
            risk_flags.append("No trading activity")
            rug_risk = True
        
        # All buys, no sells (suspicious)
        if token.sell_count == 0 and token.buy_count > 0:
            risk_flags.append("No sells detected (suspicious)")
        
        # All sells, no buys (pump and dump)
        if token.buy_count == 0 and token.sell_count > 0:
            risk_flags.append("Only sells, no buys")
            rug_risk = True
        
        return rug_risk
    
    def _calculate_overall_score(self, token: TokenData, bullish: List[str],
                                bearish: List[str], risks: List[str],
                                passes_filters: bool) -> float:
        """
        Calculate overall screening score
        
        Args:
            token: TokenData object
            bullish: List of bullish signals
            bearish: List of bearish signals
            risks: List of risk flags
            passes_filters: Whether token passes basic filters
            
        Returns:
            Score from 0-100
        """
        score = 50.0  # Start at neutral
        
        if not passes_filters:
            return 20.0  # Low score if fails basic filters
        
        # Add points for bullish signals
        score += len(bullish) * 8
        
        # Subtract points for bearish signals
        score -= len(bearish) * 10
        
        # Subtract points for risk flags
        score -= len(risks) * 5
        
        # Liquidity bonus
        if token.liquidity > 100000:
            score += 10
        
        # Volume bonus
        if token.volume_1h > 50000:
            score += 8
        
        # Buy pressure bonus
        total_txns = token.buy_count + token.sell_count
        if total_txns > 0:
            buy_ratio = token.buy_count / total_txns
            if buy_ratio > 0.6:
                score += 10
        
        # Momentum bonus
        if token.price_change_pct > 5:
            score += 5
        
        # Cap score between 0-100
        return max(0, min(100, score))
    
    def filter_tokens(self, tokens: List[TokenData],
                     min_score: float = 50.0) -> List[ScreeningResult]:
        """
        Filter multiple tokens
        
        Args:
            tokens: List of TokenData objects
            min_score: Minimum screening score to include
            
        Returns:
            List of ScreeningResult objects
        """
        results = []
        
        for token in tokens:
            result = self.screen_token(token)
            if result.overall_score >= min_score:
                results.append(result)
        
        # Sort by score descending
        results.sort(key=lambda x: x.overall_score, reverse=True)
        
        return results
