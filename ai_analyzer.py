"""
AI analysis engine for generating detailed token analysis
"""

import logging
import aiohttp
import json
from typing import Optional, Dict, Tuple
from dataclasses import dataclass
from app.collectors.dexscreener import TokenData

logger = logging.getLogger(__name__)


@dataclass
class AIAnalysis:
    """AI analysis result"""
    bullish_score: float  # 0-100
    confidence_score: float  # 0-100
    risk_score: float  # 0-100
    reasoning: str
    risks: str
    potential_upside: str
    potential_downside: str
    smart_money_observations: str


class AIAnalyzer:
    """AI-powered token analyzer"""
    
    def __init__(self, api_key: str, provider: str = "openrouter", 
                 model: str = "meta-llama/llama-2-70b-chat"):
        """
        Initialize AI analyzer
        
        Args:
            api_key: API key for AI provider
            provider: "openrouter" or "gemini"
            model: Model name
        """
        self.api_key = api_key
        self.provider = provider
        self.model = model
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Initialize async session"""
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close async session"""
        if self.session:
            await self.session.close()
    
    async def analyze_token(self, token: TokenData,
                           screening_score: float) -> Optional[AIAnalysis]:
        """
        Analyze token using AI
        
        Args:
            token: TokenData object
            screening_score: Screening score from 0-100
            
        Returns:
            AIAnalysis object or None on error
        """
        try:
            if self.provider == "openrouter":
                return await self._analyze_with_openrouter(token, screening_score)
            elif self.provider == "gemini":
                return await self._analyze_with_gemini(token, screening_score)
            else:
                logger.error(f"Unknown AI provider: {self.provider}")
                return None
                
        except Exception as e:
            logger.error(f"❌ AI analysis error: {str(e)}")
            return None
    
    async def _analyze_with_openrouter(self, token: TokenData,
                                       screening_score: float) -> Optional[AIAnalysis]:
        """
        Analyze using OpenRouter API
        
        Args:
            token: TokenData object
            screening_score: Screening score
            
        Returns:
            AIAnalysis object
        """
        prompt = self._build_analysis_prompt(token, screening_score)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1000,
                "top_p": 0.9
            }
            
            async with self.session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=30
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    return self._parse_ai_response(content, token)
                else:
                    logger.error(f"OpenRouter API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"OpenRouter error: {str(e)}")
            return None
    
    async def _analyze_with_gemini(self, token: TokenData,
                                   screening_score: float) -> Optional[AIAnalysis]:
        """
        Analyze using Google Gemini API
        
        Args:
            token: TokenData object
            screening_score: Screening score
            
        Returns:
            AIAnalysis object
        """
        prompt = self._build_analysis_prompt(token, screening_score)
        
        try:
            headers = {
                "Content-Type": "application/json",
            }
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 1000,
                    "topP": 0.9
                }
            }
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_key}"
            
            async with self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data["candidates"][0]["content"]["parts"][0]["text"]
                    return self._parse_ai_response(content, token)
                else:
                    logger.error(f"Gemini API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Gemini error: {str(e)}")
            return None
    
    def _build_analysis_prompt(self, token: TokenData,
                              screening_score: float) -> str:
        """
        Build analysis prompt for AI
        
        Args:
            token: TokenData object
            screening_score: Screening score
            
        Returns:
            Prompt string
        """
        buy_sell_ratio = (token.buy_count / token.sell_count) if token.sell_count > 0 else token.buy_count
        
        prompt = f"""Analyze this cryptocurrency token for a smart money trading alert.

TOKEN DATA:
- Name: {token.token_name} ({token.symbol})
- Chain: {token.chain}
- Price: ${token.price:.8f}
- Market Cap: ${token.market_cap:,.0f}
- Liquidity: ${token.liquidity:,.0f}
- 1H Volume: ${token.volume_1h:,.0f}
- 24H Volume: ${token.volume_24h:,.0f}
- Buy/Sell Ratio: {buy_sell_ratio:.2f}x
- Pair Age: {token.pair_age} hours
- 1H Price Change: {token.price_change_pct}%
- Screening Score: {screening_score:.1f}/100

ANALYZE AND PROVIDE IN THIS EXACT JSON FORMAT:
{{
    "bullish_score": <0-100>,
    "confidence_score": <0-100>,
    "risk_score": <0-100>,
    "reasoning": "<Why this token is interesting (2-3 sentences)>",
    "risks": "<Key risks and concerns (2-3 sentences)>",
    "potential_upside": "<Realistic upside estimate>",
    "potential_downside": "<Realistic downside estimate>",
    "smart_money_observations": "<Smart money activity observations>"
}}

Return ONLY valid JSON, no additional text."""
        
        return prompt
    
    def _parse_ai_response(self, content: str, token: TokenData) -> Optional[AIAnalysis]:
        """
        Parse AI response
        
        Args:
            content: Raw AI response
            token: TokenData object
            
        Returns:
            AIAnalysis object
        """
        try:
            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("Could not find JSON in AI response")
                return self._get_fallback_analysis(token)
            
            json_str = content[json_start:json_end]
            data = json.loads(json_str)
            
            analysis = AIAnalysis(
                bullish_score=float(data.get("bullish_score", 50)),
                confidence_score=float(data.get("confidence_score", 50)),
                risk_score=float(data.get("risk_score", 50)),
                reasoning=data.get("reasoning", ""),
                risks=data.get("risks", ""),
                potential_upside=data.get("potential_upside", ""),
                potential_downside=data.get("potential_downside", ""),
                smart_money_observations=data.get("smart_money_observations", "")
            )
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON decode error: {str(e)}")
            return self._get_fallback_analysis(token)
    
    def _get_fallback_analysis(self, token: TokenData) -> AIAnalysis:
        """
        Get fallback analysis when AI fails
        
        Args:
            token: TokenData object
            
        Returns:
            AIAnalysis with estimated scores
        """
        # Simple heuristic-based analysis
        bullish_score = 0
        confidence_score = 50
        risk_score = 50
        
        # Increase bullish if good metrics
        if token.liquidity > 100000:
            bullish_score += 15
        if token.volume_1h > 50000:
            bullish_score += 15
        if token.price_change_pct > 5:
            bullish_score += 10
        
        # Check buy/sell ratio
        if token.sell_count > 0:
            buy_ratio = token.buy_count / (token.buy_count + token.sell_count)
            if buy_ratio > 0.6:
                bullish_score += 15
            elif buy_ratio < 0.4:
                bullish_score -= 15
        
        bullish_score = max(0, min(100, bullish_score + 35))
        
        return AIAnalysis(
            bullish_score=bullish_score,
            confidence_score=confidence_score,
            risk_score=risk_score,
            reasoning="Automated analysis: Token shows mixed indicators. Requires careful evaluation.",
            risks="Market is volatile. Rug pull risk exists for new tokens.",
            potential_upside="Early entry opportunity if momentum continues.",
            potential_downside="High risk of sharp decline or rug pull.",
            smart_money_observations="Monitor wallet accumulation patterns."
        )
