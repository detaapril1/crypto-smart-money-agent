# Quick Start Setup Guide

Get the Crypto Smart Money AI Agent up and running in 10 minutes.

## Prerequisites

- Python 3.11 or higher
- Telegram Bot (get token from @BotFather)
- OpenRouter or Gemini API key
- Git

## Step 1: Get API Credentials (2 minutes)

### Telegram Bot Token
1. Open Telegram and search for @BotFather
2. Send `/newbot`
3. Follow the prompts and copy your token
4. Add the bot to a chat
5. Send a test message
6. Visit `https://api.telegram.org/bot{TOKEN}/getUpdates` (replace {TOKEN})
7. Copy the `chat_id` from the response

### OpenRouter API Key
1. Visit https://openrouter.ai
2. Sign up for free account
3. Go to API keys section
4. Create new API key
5. Copy the key (starts with `sk-`)

## Step 2: Clone Repository (1 minute)

```bash
git clone https://github.com/yourusername/crypto-smart-money-agent.git
cd crypto-smart-money-agent
```

## Step 3: Setup Environment (2 minutes)

```bash
# Copy environment template
cp .env.example .env

# Open and edit with your credentials
nano .env
```

Fill in:
```
TELEGRAM_BOT_TOKEN=your_token_from_botfather
TELEGRAM_CHAT_ID=your_chat_id_from_getUpdates
OPENROUTER_API_KEY=your_openrouter_key
```

## Step 4: Install Dependencies (3 minutes)

```bash
# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 5: Run the Agent (2 minutes)

```bash
python main.py
```

You should see output like:
```
🚀 Starting Crypto Smart Money AI Agent...
Configuration loaded: Crypto Smart Money AI Agent v1.0.0
✅ Agent initialized successfully
📊 Starting continuous market scanning...
🔍 Starting scan cycle...
```

## Verify It's Working

1. **Check Telegram**: You should receive alerts as the agent detects promising tokens
2. **Check Logs**: Open `logs/crypto_agent.log` to verify operations
3. **Check Database**: SQLite database created at `data/crypto_agent.db`

## Next Steps

### For Development
- Review code structure in `app/` directory
- Check `CONTRIBUTING.md` for development guidelines
- Run tests: `pytest tests/`

### For Production
- Follow `DEPLOYMENT.md` for VPS setup
- Use `docker-compose up -d` for Docker deployment
- Configure PM2 or systemd for auto-restart
- Setup monitoring and backups

### For Customization
- Adjust screening thresholds in `SCAN_INTERVAL`, `MIN_LIQUIDITY`, etc.
- Modify AI model in `.env` (try different OpenRouter models)
- Change alert format in `app/alerts/telegram.py`
- Add custom screening logic in `app/analyzers/screening.py`

## Troubleshooting

### "No module named 'app'"
```bash
# Make sure you're in the project root directory
cd crypto-smart-money-agent
```

### "Telegram bot token invalid"
1. Copy token correctly from @BotFather (no spaces)
2. Verify in .env file
3. Test with: `curl "https://api.telegram.org/bot{TOKEN}/getMe"`

### "API key invalid"
1. Verify key from OpenRouter dashboard
2. Has the key been revoked? Generate new one
3. Check if you have available credits

### No alerts received
1. Check logs: `tail logs/crypto_agent.log`
2. Verify Telegram chat ID is correct
3. Check if scanning is working: look for "scan cycle" in logs
4. Verify API keys are working

## Common Commands

```bash
# View logs in real-time
tail -f logs/crypto_agent.log

# Count total alerts
grep "Alert sent for" logs/crypto_agent.log | wc -l

# Check database size
du -h data/crypto_agent.db

# Reset database (careful!)
rm data/crypto_agent.db

# Run tests
pytest tests/ -v

# Format code
black app/ tests/

# Check code style
flake8 app/ tests/
```

## Configuration Reference

Key environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| SCAN_INTERVAL | 300 | Seconds between scans |
| MIN_LIQUIDITY | 20000 | Min liquidity in USD |
| MIN_MARKET_CAP | 50000 | Min market cap in USD |
| MAX_DAILY_ALERTS | 50 | Max alerts per day |
| ALERT_COOLDOWN | 300 | Seconds between alerts for same token |
| LOG_LEVEL | INFO | Logging level |

## Performance Tips

1. **Increase Scan Interval**: Change to 600 (10 min) for slower scanning
2. **Reduce Token Limit**: Change `get_trending_tokens(limit=30)` to lower number
3. **Increase Min Liquidity**: Reduces false positives
4. **Use PostgreSQL**: Better performance for large databases

## Security Reminder

⚠️ **Important:**
- Never commit `.env` file to Git
- Use strong API keys from trusted sources
- Rotate API keys regularly
- Use read-only database accounts in production
- Enable firewall on VPS
- Use HTTPS for API access

## Getting Help

- 📖 Read full documentation: `README.md`, `DEPLOYMENT.md`, `ARCHITECTURE.md`
- 🐛 Report bugs: GitHub Issues
- 💬 Ask questions: GitHub Discussions
- 🤝 Contribute: See `CONTRIBUTING.md`

## Next: Production Deployment

When you're ready for production:

1. **VPS Setup**: Follow `DEPLOYMENT.md`
2. **Docker**: Run `cd docker && docker-compose up -d`
3. **Monitoring**: Setup PM2 or systemd
4. **Backups**: Configure automatic database backups
5. **Security**: Harden firewall and SSH

---

**You're all set!** 🎉

Your Crypto Smart Money AI Agent is now scanning markets and sending alerts via Telegram. Enjoy!
