"""
Database models for the Crypto Smart Money AI Agent
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
import json


@dataclass
class Signal:
    """Trading signal model"""
    id: Optional[int] = None
    timestamp: Optional[datetime] = None
    token_name: str = ""
    symbol: str = ""
    chain: str = ""
    pair_address: str = ""
    price: float = 0.0
    market_cap: float = 0.0
    liquidity: float = 0.0
    volume_5m: float = 0.0
    volume_1h: float = 0.0
    volume_6h: float = 0.0
    volume_24h: float = 0.0
    buy_count: int = 0
    sell_count: int = 0
    buy_sell_ratio: float = 0.0
    pair_age: int = 0
    price_change_pct: float = 0.0
    ai_bullish_score: float = 0.0
    ai_confidence_score: float = 0.0
    ai_risk_score: float = 0.0
    ai_reasoning: str = ""
    risks: str = ""
    smart_money_data: str = ""
    alert_reason: str = ""
    status: str = "open"  # open, closed, rug_pull


@dataclass
class Performance:
    """Signal performance tracking model"""
    id: Optional[int] = None
    signal_id: int = 0
    check_timestamp: Optional[datetime] = None
    time_interval_minutes: int = 0
    entry_price: float = 0.0
    current_price: float = 0.0
    highest_price: float = 0.0
    lowest_price: float = 0.0
    percentage_gain: float = 0.0
    percentage_loss: float = 0.0
    max_drawdown: float = 0.0


class Database:
    """Database manager for SQLite"""
    
    def __init__(self, db_path: str = "data/crypto_agent.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.initialize_schema()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def initialize_schema(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Signals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                token_name TEXT NOT NULL,
                symbol TEXT NOT NULL,
                chain TEXT NOT NULL,
                pair_address TEXT UNIQUE NOT NULL,
                price REAL,
                market_cap REAL,
                liquidity REAL,
                volume_5m REAL,
                volume_1h REAL,
                volume_6h REAL,
                volume_24h REAL,
                buy_count INTEGER,
                sell_count INTEGER,
                buy_sell_ratio REAL,
                pair_age INTEGER,
                price_change_pct REAL,
                ai_bullish_score REAL,
                ai_confidence_score REAL,
                ai_risk_score REAL,
                ai_reasoning TEXT,
                risks TEXT,
                smart_money_data TEXT,
                alert_reason TEXT,
                status TEXT DEFAULT 'open'
            )
        """)
        
        # Performance tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signal_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id INTEGER NOT NULL,
                check_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                time_interval_minutes INTEGER,
                entry_price REAL,
                current_price REAL,
                highest_price REAL,
                lowest_price REAL,
                percentage_gain REAL,
                percentage_loss REAL,
                max_drawdown REAL,
                FOREIGN KEY (signal_id) REFERENCES signals(id)
            )
        """)
        
        # Alert log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                telegram_message_id TEXT,
                status TEXT,
                error_message TEXT,
                FOREIGN KEY (signal_id) REFERENCES signals(id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_chain ON signals(chain)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_performance_signal ON signal_performance(signal_id)")
        
        conn.commit()
        conn.close()
    
    def insert_signal(self, signal: Signal) -> int:
        """Insert a new signal"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO signals (
                token_name, symbol, chain, pair_address, price, market_cap,
                liquidity, volume_5m, volume_1h, volume_6h, volume_24h,
                buy_count, sell_count, buy_sell_ratio, pair_age, price_change_pct,
                ai_bullish_score, ai_confidence_score, ai_risk_score,
                ai_reasoning, risks, smart_money_data, alert_reason, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            signal.token_name, signal.symbol, signal.chain, signal.pair_address,
            signal.price, signal.market_cap, signal.liquidity, signal.volume_5m,
            signal.volume_1h, signal.volume_6h, signal.volume_24h, signal.buy_count,
            signal.sell_count, signal.buy_sell_ratio, signal.pair_age,
            signal.price_change_pct, signal.ai_bullish_score, signal.ai_confidence_score,
            signal.ai_risk_score, signal.ai_reasoning, signal.risks,
            signal.smart_money_data, signal.alert_reason, signal.status
        ))
        
        signal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return signal_id
    
    def get_recent_signals(self, limit: int = 20) -> List[dict]:
        """Get recent signals"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM signals 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_signal_by_id(self, signal_id: int) -> Optional[dict]:
        """Get signal by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM signals WHERE id = ?", (signal_id,))
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    def update_signal_status(self, signal_id: int, status: str):
        """Update signal status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE signals SET status = ? WHERE id = ?",
            (status, signal_id)
        )
        
        conn.commit()
        conn.close()
    
    def insert_performance(self, performance: Performance):
        """Insert performance record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO signal_performance (
                signal_id, time_interval_minutes, entry_price, current_price,
                highest_price, lowest_price, percentage_gain, percentage_loss,
                max_drawdown
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            performance.signal_id, performance.time_interval_minutes,
            performance.entry_price, performance.current_price,
            performance.highest_price, performance.lowest_price,
            performance.percentage_gain, performance.percentage_loss,
            performance.max_drawdown
        ))
        
        conn.commit()
        conn.close()
    
    def get_performance_stats(self) -> dict:
        """Get overall performance statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total signals
        cursor.execute("SELECT COUNT(*) as count FROM signals")
        total_signals = cursor.fetchone()['count']
        
        # Win rate calculation
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT s.id) as winners
            FROM signals s
            LEFT JOIN signal_performance p ON s.id = p.signal_id
            WHERE p.percentage_gain > 0
        """)
        winners = cursor.fetchone()['winners'] or 0
        
        # Average scores
        cursor.execute("""
            SELECT 
                AVG(ai_bullish_score) as avg_bullish,
                AVG(ai_confidence_score) as avg_confidence,
                AVG(ai_risk_score) as avg_risk
            FROM signals
        """)
        scores = cursor.fetchone()
        
        conn.close()
        
        win_rate = (winners / total_signals * 100) if total_signals > 0 else 0
        
        return {
            "total_signals": total_signals,
            "winners": winners,
            "win_rate": round(win_rate, 2),
            "avg_bullish_score": round(scores['avg_bullish'] or 0, 2),
            "avg_confidence_score": round(scores['avg_confidence'] or 0, 2),
            "avg_risk_score": round(scores['avg_risk'] or 0, 2),
        }
