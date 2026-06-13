# Architecture Documentation

## System Overview

The Crypto Smart Money AI Agent is a modular, asynchronous Python application designed for continuous operation on VPS infrastructure. It employs a multi-stage pipeline for token discovery, analysis, and alerting.

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    SCAN CYCLE (every 5 min)                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. DATA COLLECTION                                          │
│     ↓                                                         │
│     DexScreener Collector ──→ Trending Tokens               │
│                                                               │
│  2. INITIAL SCREENING                                        │
│     ↓                                                         │
│     TokenScreener ──→ Filters (liquidity, volume, etc)      │
│     ↓                                                         │
│     Candidates (top 10-20 tokens)                           │
│                                                               │
│  3. AI ANALYSIS                                              │
│     ↓                                                         │
│     AIAnalyzer ──→ OpenRouter/Gemini ──→ Scores & Reasoning │
│     ↓                                                         │
│     High Confidence Signals                                  │
│                                                               │
│  4. ALERT GENERATION                                         │
│     ↓                                                         │
│     TelegramAlerts ──→ Format & Send ──→ User Notification  │
│                                                               │
│  5. DATA PERSISTENCE                                         │
│     ↓                                                         │
│     Database ──→ SQLite/PostgreSQL ──→ Historical Record     │
│                                                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│            PERFORMANCE EVALUATION (continuous)               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Monitor signals at:                                         │
│  • 15 minutes                                                │
│  • 1 hour                                                    │
│  • 4 hours                                                   │
│  • 24 hours                                                  │
│                                                               │
│  Track:                                                      │
│  • Actual price changes                                      │
│  • Maximum profit/loss                                       │
│  • Win rate                                                  │
│  • AI accuracy                                               │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Data Collection Layer (collectors/)

**DexScreenerCollector**
- Fetches trending tokens from DexScreener API
- Gets new pairs by chain
- Retrieves specific token data
- Parses market data into TokenData objects

**Data Returned:**
```python
TokenData {
    token_name: str
    symbol: str
    chain: str
    pair_address: str
    price: float
    market_cap: float
    liquidity: float
    volume_5m/1h/6h/24h: float
    buy_count: int
    sell_count: int
    pair_age: int
    price_change_pct: float
}
```

### 2. Analysis Layer (analyzers/)

**TokenScreener**
- Implements 10+ filtering criteria
- Rejects obvious scams and rug pulls
- Scores tokens on 0-100 scale
- Identifies bullish/bearish signals

**Screening Output:**
```python
ScreeningResult {
    token_data: TokenData
    passes_basic_filters: bool
    rejection_reasons: List[str]
    bullish_signals: List[str]
    bearish_signals: List[str]
    risk_flags: List[str]
    overall_score: float  # 0-100
}
```

**AIAnalyzer**
- Sends tokens to OpenRouter or Gemini
- Generates detailed analysis
- Produces scoring metrics
- Explains reasoning and risks

**AI Analysis Output:**
```python
AIAnalysis {
    bullish_score: float  # 0-100
    confidence_score: float  # 0-100
    risk_score: float  # 0-100
    reasoning: str
    risks: str
    potential_upside: str
    potential_downside: str
    smart_money_observations: str
}
```

### 3. Alert System (alerts/)

**TelegramAlerts**
- Formats signals into readable messages
- Sends to Telegram via Bot API
- Tracks delivery status
- Handles errors gracefully

**Message Format:**
- Token information (price, volume, metrics)
- AI scores and reasoning
- Risk assessment
- Actionable insights

### 4. Data Persistence (database/)

**Database**
- SQLite for development
- PostgreSQL for production
- Automatic schema initialization
- Support for migrations

**Schema:**
```
signals table:
├── id (PK)
├── timestamp
├── token_name, symbol, chain
├── pair_address (UNIQUE)
├── price, market_cap, liquidity
├── volume metrics
├── buy/sell counts
├── AI scores (bullish, confidence, risk)
├── analysis text fields
└── status (open, closed, rug_pull)

signal_performance table:
├── id (PK)
├── signal_id (FK)
├── check_timestamp
├── time_interval_minutes
├── entry/current/high/low prices
├── gains/losses
└── max_drawdown

alert_logs table:
├── id (PK)
├── signal_id (FK)
├── timestamp
├── message_id
├── status
└── error_message
```

### 5. Orchestration (services/)

**AgentOrchestrator**
- Coordinates all components
- Manages async tasks
- Controls scan cycles
- Tracks performance
- Enforces rate limits and cooldowns

**Key Responsibilities:**
- Initialize all services
- Run scan cycles on schedule
- Apply alert cooldown logic
- Monitor daily alert limits
- Evaluate signal performance
- Graceful error handling and recovery

## Configuration Management

**Environment Variables (.env)**
- API credentials
- Database configuration
- Scanning parameters
- AI settings
- Alert thresholds

**Config Object**
```python
Config {
    # API Keys
    telegram_bot_token: str
    openrouter_api_key: str
    
    # Scanning
    scan_interval: int (seconds)
    min_liquidity: float
    min_market_cap: float
    
    # AI
    ai_provider: str
    ai_model: str
    
    # Database
    database_url: str
    database_type: str
    
    # Alerts
    alert_cooldown: int
    max_daily_alerts: int
}
```

## Async Architecture

Uses Python's `asyncio` for concurrent operations:

```
Event Loop
├── DexScreener API calls (async)
├── Screening evaluation (parallel)
├── AI API requests (concurrent)
├── Database writes (async)
└── Telegram alerts (non-blocking)
```

Benefits:
- Single-threaded, efficient
- Handles multiple concurrent operations
- Non-blocking I/O for API calls
- Responsive error handling

## Error Handling Strategy

```
Try
├─→ Success: Continue
├─→ API Error: Log, retry, fallback
├─→ Database Error: Log, recover
└─→ Fatal Error: Log, exit gracefully
```

**Resilience:**
- API rate limit handling
- Retry logic with exponential backoff
- Fallback AI analysis when API fails
- Database connection pooling
- Logging and monitoring integration

## Scalability Considerations

### Horizontal Scaling
- Multiple agents can run independently
- Shared PostgreSQL database
- Each agent has independent scanning cycle
- Alert deduplication via database

### Vertical Scaling
- Increase token analysis batch size
- Optimize database queries
- Cache frequently accessed data
- Use connection pooling

### Performance Optimization
- Async/await throughout
- Batch API requests
- Index database tables
- Cache configuration
- Connection pooling

## API Integration Points

### DexScreener API
- Rate: Generous free tier
- Data: Real-time market data
- Reliability: Established service

### OpenRouter / Gemini API
- Rate: API key based
- Data: AI analysis
- Reliability: Redundancy support

### Telegram Bot API
- Rate: High throughput
- Reliability: Official service
- Security: Token-based

## Database Design

### Normalization
- Signal table: One record per detected opportunity
- Performance table: Normalized tracking of outcomes
- Alert logs: Audit trail of notifications

### Indexing Strategy
```
signals:
├── idx_signals_timestamp (scan queries)
├── idx_signals_symbol (lookup)
└── idx_signals_chain (filtering)

signal_performance:
├── idx_performance_signal (joins)
```

### Query Patterns
- Recent signals (ORDER BY timestamp DESC LIMIT)
- Statistics (aggregate functions)
- Status filtering (WHERE status = ?)
- Date range queries (timestamp BETWEEN)

## Deployment Architecture

### Docker
- Single container with Python environment
- Alpine Linux for small footprint
- PostgreSQL as separate service
- Volumes for data persistence

### VPS/Systemd
- Python virtual environment
- Systemd service for auto-restart
- PM2 for process management
- Nginx reverse proxy (optional)

### Monitoring
- Log rotation (daily, 14-day retention)
- Health checks (systemd watchdog)
- Process monitoring (PM2 or systemd)
- Alerting (log analysis)

## Security Architecture

**Data Security:**
- All secrets in environment variables
- No hardcoded credentials
- .env files in .gitignore
- HTTPS ready for API

**API Security:**
- Rate limiting per API
- Request validation
- Error handling without data leaks
- Telegram token protection

**Database Security:**
- Connection string parameterized
- Database user with limited privileges
- Encrypted password storage
- Backup encryption ready

## Extension Points

### Adding New Collectors
```python
class NewSourceCollector:
    async def initialize(self): pass
    async def fetch_data(self): pass
    async def close(self): pass
```

### Adding New Analyzers
```python
class NewAnalyzer:
    def analyze(self, token): 
        return AnalysisResult
```

### Adding New Alerts
```python
class NewAlertSystem:
    async def send_alert(self, signal): pass
```

## Performance Metrics

**Target Performance:**
- Token retrieval: <1s
- Screening: <10ms per token
- AI analysis: 5-10s per token
- Alert sending: <1s
- Database write: <50ms
- Full cycle: 5-10 minutes

**Monitoring:**
- Operation timing logs
- Error rate tracking
- Success rate per component
- API quota usage
- Database query performance

## Roadmap for Enhancements

1. **v1.1**: Dashboard visualization
2. **v2.0**: Pattern detection (SMC, BOS, etc)
3. **v3.0**: Trading automation
4. **v4.0**: Machine learning optimization
