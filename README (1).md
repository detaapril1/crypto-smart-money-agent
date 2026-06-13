# 🚀 Crypto Smart Money AI Agent

A production-ready Python application that runs continuously on a VPS, scans cryptocurrency markets in real-time, detects high-probability trading opportunities using AI, and sends alerts via Telegram.

## 📋 Features

### Core Capabilities
- **Real-time Market Scanning**: Monitors trending tokens using DexScreener API
- **Intelligent Token Screening**: Filters tokens based on 10+ technical criteria
- **AI-Powered Analysis**: Uses OpenRouter/Gemini to generate detailed trade analysis
- **Smart Money Tracking**: Detects whale activity and smart money movements
- **Telegram Alerts**: Sends formatted alerts with AI analysis and risk scores
- **Automatic Performance Tracking**: Monitors signal profitability at multiple timeframes
- **Learning System**: Records performance metrics for continuous improvement

### Technical Features
- ✅ Asynchronous architecture for high performance
- ✅ Database support for SQLite (development) and PostgreSQL (production)
- ✅ Docker containerization for easy deployment
- ✅ GitHub Actions CI/CD pipeline
- ✅ Comprehensive logging and error handling
- ✅ Modular, scalable architecture
- ✅ Environment variable configuration
- ✅ API rate limiting and retry logic

## 🏗️ Architecture

```
project/
├── app/
│   ├── collectors/           # Data collection modules
│   │   ├── dexscreener.py   # DexScreener API client
│   │   └── __init__.py
│   ├── analyzers/            # Analysis engines
│   │   ├── screening.py      # Token screening logic
│   │   ├── ai_analyzer.py    # AI-powered analysis
│   │   └── __init__.py
│   ├── alerts/               # Alert systems
│   │   ├── telegram.py       # Telegram bot integration
│   │   └── __init__.py
│   ├── database/             # Database layer
│   │   ├── models.py         # Data models
│   │   └── __init__.py
│   ├── services/             # Business logic
│   │   ├── orchestrator.py   # Main coordinator
│   │   └── __init__.py
│   ├── api/                  # API endpoints
│   │   ├── dashboard.py      # Dashboard API
│   │   └── __init__.py
│   ├── utils/                # Utilities
│   │   ├── config.py         # Configuration management
│   │   ├── logger.py         # Logging setup
│   │   └── __init__.py
│   └── __init__.py
├── tests/                    # Test suite
├── docker/                   # Docker files
│   ├── Dockerfile
│   └── docker-compose.yml
├── scripts/                  # Utility scripts
├── data/                     # SQLite database
├── logs/                     # Application logs
├── main.py                   # Entry point
├── requirements.txt          # Python dependencies
├── .env.example              # Configuration template
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (optional, for production)
- Telegram Bot Token
- OpenRouter API Key (for AI analysis)

### Installation

1. **Clone and setup**
```bash
git clone https://github.com/yourusername/crypto-smart-money-agent.git
cd crypto-smart-money-agent
```

2. **Create environment file**
```bash
cp .env.example .env
# Edit .env with your API keys
nano .env
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the agent**
```bash
python main.py
```

### Docker Deployment

1. **Build and run with Docker Compose**
```bash
cd docker
docker-compose up -d
```

2. **View logs**
```bash
docker-compose logs -f agent
```

3. **Stop the agent**
```bash
docker-compose down
```

## 📝 Configuration

### Environment Variables

**Essential:**
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `TELEGRAM_CHAT_ID`: Target chat ID for alerts
- `OPENROUTER_API_KEY`: OpenRouter API key for AI analysis

**Optional:**
- `GEMINI_API_KEY`: Google Gemini API key (alternative to OpenRouter)
- `DEXSCREENER_API_KEY`: DexScreener API key
- `HELIUS_API_KEY`: Helius API for Solana
- `BIRDEYE_API_KEY`: Birdeye API for token analytics

**Scanning:**
- `SCAN_INTERVAL`: Seconds between scans (default: 300)
- `MIN_LIQUIDITY`: Minimum liquidity in USD (default: 20000)
- `MIN_MARKET_CAP`: Minimum market cap in USD (default: 50000)

**Database:**
- `DATABASE_URL`: Database connection string
- `DATABASE_TYPE`: "sqlite" or "postgresql"

### Screening Filters

The agent applies intelligent filters to avoid scams and rug pulls:

**Rejection Criteria:**
- Liquidity < $20,000
- Extremely low trading volume
- Dangerous wallet concentration
- Suspicious contract behavior
- All-sell or no-buy patterns

**Bullish Signals:**
- Rapid volume increase
- More buys than sells
- Healthy liquidity
- Smart money accumulation
- Rising holder count
- Strong price momentum

## 📊 Alert Format

```
🚀 SMART MONEY ALERT

Token: TokenName (SYMBOL)
Chain: SOLANA
Price: $0.00123456
Market Cap: $1,234,567
Liquidity: $45,000
Volume 1H: $123,456
1H Change: +5.25%

🤖 AI Analysis
Bullish Score: 75/100
Confidence: 82/100
Risk Score: 35/100

💭 Reasoning:
[AI-generated analysis]

📌 Risks:
[Risk assessment]

... [Full analysis]
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v --cov=app
```

Generate coverage report:
```bash
pytest tests/ --cov=app --cov-report=html
```

## 📈 Database Schema

### signals table
- `id`: Primary key
- `timestamp`: When signal was generated
- `token_name`, `symbol`, `chain`: Token info
- `pair_address`: Smart contract address
- `price`, `market_cap`, `liquidity`: Token metrics
- `volume_5m` to `volume_24h`: Trading volume
- `buy_count`, `sell_count`: Transaction counts
- `ai_bullish_score`, `ai_confidence_score`, `ai_risk_score`: AI scores
- `ai_reasoning`: Detailed explanation
- `risks`: Risk assessment
- `status`: "open", "closed", or "rug_pull"

### signal_performance table
- Tracks performance at 15m, 1h, 4h, 24h intervals
- Records entry/exit prices, gains/losses, drawdowns

### alert_logs table
- Records all sent alerts and delivery status

## 🔧 VPS Deployment

### Using PM2 (Recommended)

1. **Install PM2**
```bash
npm install -g pm2
```

2. **Create ecosystem config** (`ecosystem.config.js`):
```javascript
module.exports = {
  apps: [{
    name: 'crypto-agent',
    script: './main.py',
    interpreter: 'python3',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    },
    error_file: 'logs/error.log',
    out_file: 'logs/out.log',
    log_file: 'logs/pm2.log',
  }]
};
```

3. **Start with PM2**
```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### Using systemd Service

Create `/etc/systemd/system/crypto-agent.service`:
```ini
[Unit]
Description=Crypto Smart Money AI Agent
After=network.target

[Service]
Type=simple
User=crypto
WorkingDirectory=/home/crypto/crypto-smart-money-agent
ExecStart=/usr/bin/python3 /home/crypto/crypto-smart-money-agent/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable crypto-agent
sudo systemctl start crypto-agent
sudo systemctl status crypto-agent
```

## 📚 API Endpoints

The agent runs a FastAPI server on port 8000 for dashboard access:

- `GET /health` - Health check
- `GET /api/signals` - Recent signals
- `GET /api/signals/{id}` - Signal details
- `GET /api/performance` - Performance statistics
- `GET /api/stats` - Overall statistics

## 🔐 Security

- All API keys stored in environment variables
- No hardcoded secrets
- Rate limiting on API calls
- Error logging without exposing sensitive data
- Database connection pooling
- TLS/SSL ready for HTTPS deployment

## 📖 Documentation

- `ARCHITECTURE.md` - Detailed architecture guide
- `SETUP.md` - Complete setup guide
- `DEPLOYMENT.md` - VPS deployment guide
- `API.md` - API documentation
- `CONTRIBUTING.md` - Contribution guidelines

## 🗺️ Roadmap

### Version 1.0 (Current)
- ✅ DexScreener Scanner
- ✅ Telegram Alerts
- ✅ AI Analysis Engine
- ✅ Smart Money Tracking
- ✅ Performance Evaluation

### Version 1.1
- Dashboard with React frontend
- Email alerts
- Discord integration
- Performance charts

### Version 2.0
- SMC (Smart Money Concepts) detection
- BOS/CHoCH pattern detection
- Fair Value Gap identification
- Order block analysis

### Version 3.0
- Semi-automated trading
- Portfolio tracking
- Strategy backtesting
- Signal machine learning

## 🤝 Contributing

Contributions are welcome! Please read our Contributing Guide for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and informational purposes only. Trading cryptocurrency is risky and can result in loss of funds. Always do your own research and never invest more than you can afford to lose. The authors are not responsible for any financial losses.

## 💬 Support

- GitHub Issues for bug reports
- GitHub Discussions for questions
- Telegram community for general chat

## 🙏 Acknowledgments

- DexScreener for market data
- OpenRouter for AI services
- The crypto community for feedback

---

**Made with ❤️ for the crypto trading community**
