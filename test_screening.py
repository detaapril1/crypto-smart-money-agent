"""
Unit tests for token screening module
"""

import pytest
from app.collectors.dexscreener import TokenData
from app.analyzers.screening import TokenScreener


@pytest.fixture
def screener():
    """Create screener instance"""
    return TokenScreener()


@pytest.fixture
def good_token():
    """Create a good token sample"""
    return TokenData(
        token_name="GoodToken",
        symbol="GOOD",
        chain="solana",
        pair_address="0x1234567890",
        price=0.00123,
        market_cap=500000,
        liquidity=100000,
        volume_5m=10000,
        volume_1h=50000,
        volume_6h=200000,
        volume_24h=500000,
        buy_count=150,
        sell_count=50,
        pair_age=24,
        price_change_pct=15.5
    )


@pytest.fixture
def bad_token():
    """Create a bad token sample"""
    return TokenData(
        token_name="BadToken",
        symbol="BAD",
        chain="solana",
        pair_address="0x0987654321",
        price=0.000001,
        market_cap=5000,
        liquidity=1000,
        volume_5m=10,
        volume_1h=50,
        volume_6h=100,
        volume_24h=200,
        buy_count=0,
        sell_count=100,
        pair_age=2,
        price_change_pct=-50.0
    )


def test_good_token_passes(screener, good_token):
    """Test that good token passes screening"""
    result = screener.screen_token(good_token)
    assert result.passes_basic_filters
    assert len(result.rejection_reasons) == 0
    assert result.overall_score >= 60


def test_bad_token_fails(screener, bad_token):
    """Test that bad token fails screening"""
    result = screener.screen_token(bad_token)
    assert not result.passes_basic_filters
    assert len(result.rejection_reasons) > 0


def test_low_liquidity_rejection(screener):
    """Test that low liquidity is rejected"""
    token = TokenData(
        token_name="LowLiq",
        symbol="LL",
        chain="solana",
        pair_address="0xtest",
        price=1.0,
        market_cap=100000,
        liquidity=5000,
        volume_5m=1000,
        volume_1h=5000,
        volume_6h=20000,
        volume_24h=50000,
        buy_count=50,
        sell_count=20,
        pair_age=12,
        price_change_pct=5.0
    )
    
    result = screener.screen_token(token)
    assert not result.passes_basic_filters
    assert any("liquidity" in reason.lower() for reason in result.rejection_reasons)


def test_rug_pull_detection(screener):
    """Test rug pull detection"""
    token = TokenData(
        token_name="RugToken",
        symbol="RUG",
        chain="solana",
        pair_address="0xrug",
        price=1.0,
        market_cap=1000000,
        liquidity=1000,  # Extremely low vs market cap
        volume_5m=0,
        volume_1h=0,
        volume_6h=0,
        volume_24h=0,
        buy_count=0,
        sell_count=0,
        pair_age=1,
        price_change_pct=0.0
    )
    
    result = screener.screen_token(token)
    assert not result.passes_basic_filters
    assert any("rug" in reason.lower() for reason in result.rejection_reasons)


def test_bullish_signals_detection(screener, good_token):
    """Test detection of bullish signals"""
    result = screener.screen_token(good_token)
    assert len(result.bullish_signals) > 0
    assert any("liquidity" in signal.lower() for signal in result.bullish_signals)
    assert any("volume" in signal.lower() for signal in result.bullish_signals)


def test_filter_multiple_tokens(screener):
    """Test filtering multiple tokens"""
    tokens = [
        TokenData(
            token_name=f"Token{i}",
            symbol=f"TK{i}",
            chain="solana",
            pair_address=f"0x{i}",
            price=0.1 * i,
            market_cap=100000 * i,
            liquidity=50000 * i,
            volume_5m=5000 * i,
            volume_1h=25000 * i,
            volume_6h=100000 * i,
            volume_24h=250000 * i,
            buy_count=50 + i * 10,
            sell_count=20 + i * 5,
            pair_age=12 + i,
            price_change_pct=5.0 + i
        )
        for i in range(1, 4)
    ]
    
    results = screener.filter_tokens(tokens, min_score=40)
    assert len(results) > 0
    # Results should be sorted by score
    scores = [r.overall_score for r in results]
    assert scores == sorted(scores, reverse=True)
