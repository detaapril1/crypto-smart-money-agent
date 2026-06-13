"""
DexScreener API collector for market data
"""

import aiohttp
import logging
from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class TokenData:
    """Token market data from DexScreener"""
    token_name: str
    symbol: str
    chain: str
    pair_address: str
    price: float
    market_cap: float
    liquidity: float
    volume_5m: float
    volume_1h: float
    volume_6h: float
    volume_24h: float
    buy_count: int
    sell_count: int
    pair_age: int
    price_change_pct: float
    raw_data: Dict = None


class DexScreenerCollector:
    """Collector for DexScreener API"""
    
    BASE_URL = "https://api.dexscreener.com/latest/dex"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize collector"""
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Initialize async session"""
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close async session"""
        if self.session:
            await self.session.close()
    
    async def get_trending_tokens(self, limit: int = 20) -> List[TokenData]:
        """
        Get trending tokens from DexScreener
        
        Args:
            limit: Number of tokens to retrieve
            
        Returns:
            List of TokenData objects
        """
        try:
            url = f"{self.BASE_URL}/search"
            params = {
                "order": "volume_24h",
                "direction": "desc",
                "limit": limit
            }
            
            tokens = []
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for pair in data.get("pairs", []):
                        try:
                            token_data = self._parse_pair_data(pair)
                            if token_data:
                                tokens.append(token_data)
                        except Exception as e:
                            logger.warning(f"Error parsing pair {pair.get('address')}: {str(e)}")
                            continue
            
            logger.info(f"✅ Retrieved {len(tokens)} trending tokens from DexScreener")
            return tokens
            
        except Exception as e:
            logger.error(f"❌ Error fetching trending tokens: {str(e)}")
            return []
    
    async def get_token_by_address(self, chain: str, address: str) -> Optional[TokenData]:
        """
        Get specific token data by address
        
        Args:
            chain: Blockchain network (e.g., 'solana', 'ethereum')
            address: Token contract address
            
        Returns:
            TokenData object or None
        """
        try:
            url = f"{self.BASE_URL}/tokens/{address}"
            
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for pair in data.get("pairs", []):
                        if pair.get("chainId") == chain:
                            return self._parse_pair_data(pair)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error fetching token {address}: {str(e)}")
            return None
    
    async def get_tokens_by_chain(self, chain: str, limit: int = 50) -> List[TokenData]:
        """
        Get tokens from a specific chain ordered by volume
        
        Args:
            chain: Blockchain network
            limit: Number of tokens
            
        Returns:
            List of TokenData objects
        """
        try:
            url = f"{self.BASE_URL}/search"
            params = {
                "chain": chain,
                "order": "volume_1h",
                "direction": "desc",
                "limit": limit
            }
            
            tokens = []
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for pair in data.get("pairs", []):
                        try:
                            token_data = self._parse_pair_data(pair)
                            if token_data:
                                tokens.append(token_data)
                        except Exception as e:
                            logger.warning(f"Error parsing pair {pair.get('address')}: {str(e)}")
                            continue
            
            logger.info(f"✅ Retrieved {len(tokens)} tokens from {chain}")
            return tokens
            
        except Exception as e:
            logger.error(f"❌ Error fetching tokens from {chain}: {str(e)}")
            return []
    
    def _parse_pair_data(self, pair: Dict) -> Optional[TokenData]:
        """
        Parse pair data from DexScreener API response
        
        Args:
            pair: Pair data dictionary
            
        Returns:
            TokenData object or None
        """
        try:
            # Extract base token info
            base_token = pair.get("baseToken", {})
            quote_token = pair.get("quoteToken", {})
            
            # Extract prices and volumes
            price_usd = float(pair.get("priceUsd", 0) or 0)
            market_cap = float(pair.get("marketCap", 0) or 0)
            liquidity = float(pair.get("liquidity", {}).get("usd", 0) or 0)
            
            # Volume data
            volume_5m = float(pair.get("volume", {}).get("m5", 0) or 0)
            volume_1h = float(pair.get("volume", {}).get("h1", 0) or 0)
            volume_6h = float(pair.get("volume", {}).get("h6", 0) or 0)
            volume_24h = float(pair.get("volume", {}).get("h24", 0) or 0)
            
            # Buy/Sell counts
            txns = pair.get("txns", {})
            buy_5m = txns.get("m5", {}).get("buys", 0)
            sell_5m = txns.get("m5", {}).get("sells", 0)
            buy_count = buy_5m
            sell_count = sell_5m
            
            # Calculate pair age in hours
            pair_created = pair.get("pairCreatedAt", 0)
            current_time = datetime.now().timestamp() * 1000
            pair_age = int((current_time - pair_created) / (1000 * 3600))
            
            # Price change
            price_change = pair.get("priceChange", {})
            price_change_pct = float(price_change.get("h1", 0) or 0)
            
            token_data = TokenData(
                token_name=base_token.get("name", "Unknown"),
                symbol=base_token.get("symbol", "???"),
                chain=pair.get("chainId", "unknown"),
                pair_address=pair.get("pairAddress", ""),
                price=price_usd,
                market_cap=market_cap,
                liquidity=liquidity,
                volume_5m=volume_5m,
                volume_1h=volume_1h,
                volume_6h=volume_6h,
                volume_24h=volume_24h,
                buy_count=buy_count,
                sell_count=sell_count,
                pair_age=pair_age,
                price_change_pct=price_change_pct,
                raw_data=pair
            )
            
            return token_data
            
        except Exception as e:
            logger.warning(f"Error parsing pair data: {str(e)}")
            return None
    
    async def get_new_pairs(self, chain: str, min_age_hours: int = 1, 
                           max_age_hours: int = 24, limit: int = 20) -> List[TokenData]:
        """
        Get newly created trading pairs
        
        Args:
            chain: Blockchain network
            min_age_hours: Minimum pair age in hours
            max_age_hours: Maximum pair age in hours
            limit: Number of pairs
            
        Returns:
            List of TokenData objects
        """
        try:
            url = f"{self.BASE_URL}/search"
            params = {
                "chain": chain,
                "order": "createdAt",
                "direction": "desc",
                "limit": limit * 2
            }
            
            tokens = []
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for pair in data.get("pairs", []):
                        try:
                            token_data = self._parse_pair_data(pair)
                            if token_data and min_age_hours <= token_data.pair_age <= max_age_hours:
                                tokens.append(token_data)
                                if len(tokens) >= limit:
                                    break
                        except Exception as e:
                            logger.warning(f"Error parsing pair: {str(e)}")
                            continue
            
            logger.info(f"✅ Retrieved {len(tokens)} new pairs from {chain}")
            return tokens
            
        except Exception as e:
            logger.error(f"❌ Error fetching new pairs: {str(e)}")
            return []
