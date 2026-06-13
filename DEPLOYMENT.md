# VPS Deployment Guide

Complete guide for deploying the Crypto Smart Money AI Agent on a Linux VPS.

## Prerequisites

- Ubuntu 20.04 LTS or later
- Minimum 2GB RAM
- 10GB disk space
- SSH access to VPS
- Domain name (optional, for API access)

## System Setup

### 1. Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y build-essential python3.11 python3-pip git curl wget
```

### 2. Create Application User
```bash
sudo useradd -m -s /bin/bash crypto
sudo usermod -aG sudo crypto
su - crypto
```

### 3. Install Python Requirements
```bash
# Install system dependencies
sudo apt-get install -y libpq-dev python3-dev

# Install Node.js for PM2 (optional)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2 globally
sudo npm install -g pm2
```

## Application Setup

### 4. Clone Repository
```bash
cd /home/crypto
git clone https://github.com/yourusername/crypto-smart-money-agent.git
cd crypto-smart-money-agent
```

### 5. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 6. Configure Environment
```bash
# Copy example configuration
cp .env.example .env

# Edit with your API keys
nano .env
```

Required environment variables:
```
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
OPENROUTER_API_KEY=your_api_key
DATABASE_URL=sqlite:///data/crypto_agent.db
```

### 7. Initialize Database
```bash
python -c "from app.database.models import Database; Database().initialize_schema()"
```

## Deployment Options

### Option A: PM2 (Recommended for Single Process)

#### 1. Create PM2 Configuration
```bash
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'crypto-agent',
    script: './main.py',
    interpreter: 'python3',
    instances: 1,
    autorestart: true,
    watch: ['app'],
    watch_delay: 1000,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'production',
      PYTHONUNBUFFERED: 1
    },
    error_file: 'logs/error.log',
    out_file: 'logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    autorestart: true,
    max_restarts: 10,
    min_uptime: '10s'
  }]
};
EOF
```

#### 2. Start with PM2
```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

#### 3. Monitor
```bash
# View logs
pm2 logs crypto-agent

# Status
pm2 status

# Restart
pm2 restart crypto-agent

# Stop
pm2 stop crypto-agent

# Delete
pm2 delete crypto-agent
```

### Option B: systemd Service (Recommended for Production)

#### 1. Create Service File
```bash
sudo tee /etc/systemd/system/crypto-agent.service > /dev/null << EOF
[Unit]
Description=Crypto Smart Money AI Agent
After=network.target

[Service]
Type=simple
User=crypto
WorkingDirectory=/home/crypto/crypto-smart-money-agent
Environment="PATH=/home/crypto/crypto-smart-money-agent/venv/bin"
ExecStart=/home/crypto/crypto-smart-money-agent/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

#### 2. Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable crypto-agent
sudo systemctl start crypto-agent
```

#### 3. Monitor Service
```bash
# Check status
sudo systemctl status crypto-agent

# View logs
sudo journalctl -u crypto-agent -f

# Restart
sudo systemctl restart crypto-agent

# Stop
sudo systemctl stop crypto-agent
```

### Option C: Docker Compose (Recommended for Production)

#### 1. Install Docker
```bash
sudo apt-get install -y docker.io docker-compose

# Add user to docker group
sudo usermod -aG docker crypto
newgrp docker
```

#### 2. Setup Environment
```bash
cd docker
cp ../.env.example ../.env
nano ../.env  # Configure
```

#### 3. Run Containers
```bash
docker-compose up -d

# View logs
docker-compose logs -f agent

# Stop
docker-compose down

# Restart
docker-compose restart agent
```

## PostgreSQL Setup (Optional, for Production)

### 1. Install PostgreSQL
```bash
sudo apt-get install -y postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql
```

### 2. Create Database
```bash
sudo -u postgres psql << EOF
CREATE USER crypto_user WITH PASSWORD 'secure_password';
CREATE DATABASE crypto_agent OWNER crypto_user;
GRANT ALL PRIVILEGES ON DATABASE crypto_agent TO crypto_user;
EOF
```

### 3. Update Configuration
```bash
# Edit .env
DATABASE_URL=postgresql://crypto_user:secure_password@localhost:5432/crypto_agent
DATABASE_TYPE=postgresql
```

## Nginx Reverse Proxy (For API Access)

### 1. Install Nginx
```bash
sudo apt-get install -y nginx
```

### 2. Create Configuration
```bash
sudo tee /etc/nginx/sites-available/crypto-agent > /dev/null << 'EOF'
upstream crypto_agent {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://crypto_agent;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/crypto/crypto-smart-money-agent/static/;
    }
}
EOF
```

### 3. Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/crypto-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. SSL Certificate (Let's Encrypt)
```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## Monitoring and Logging

### 1. Log Rotation
```bash
sudo tee /etc/logrotate.d/crypto-agent > /dev/null << 'EOF'
/home/crypto/crypto-smart-money-agent/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 crypto crypto
    sharedscripts
}
EOF
```

### 2. System Monitoring
```bash
# Install monitoring tools
sudo apt-get install -y htop iotop nethogs

# Monitor in real-time
htop
```

### 3. Setup Alerts
```bash
# Email on service failure
sudo apt-get install -y ssmtp mailutils

# Configure in PM2 or systemd watch scripts
```

## Backup Strategy

### 1. Database Backup
```bash
# SQLite
cp /home/crypto/crypto-smart-money-agent/data/crypto_agent.db \
   /backup/crypto_agent_$(date +%Y%m%d_%H%M%S).db

# PostgreSQL
pg_dump crypto_agent > /backup/crypto_agent_$(date +%Y%m%d_%H%M%S).sql
```

### 2. Automated Backup Script
```bash
cat > /home/crypto/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
cp /home/crypto/crypto-smart-money-agent/data/crypto_agent.db \
   $BACKUP_DIR/crypto_agent_$DATE.db

# Keep only last 30 days
find $BACKUP_DIR -name "crypto_agent_*.db" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/crypto_agent_$DATE.db"
EOF

chmod +x /home/crypto/backup.sh
```

### 3. Schedule Backup
```bash
# Add to crontab
crontab -e

# Run daily at 2 AM
0 2 * * * /home/crypto/backup.sh >> /var/log/crypto_backup.log 2>&1
```

## Troubleshooting

### Agent Not Running
```bash
# Check logs
pm2 logs crypto-agent
# or
sudo journalctl -u crypto-agent -f

# Check process
ps aux | grep main.py

# Check port
netstat -tlnp | grep 8000
```

### API Key Errors
```bash
# Verify .env file
cat .env

# Check environment is loaded
echo $TELEGRAM_BOT_TOKEN
```

### Database Connection Issues
```bash
# Test connection
python3 -c "from app.database.models import Database; db = Database(); print('OK')"

# Check PostgreSQL
sudo systemctl status postgresql
```

### Performance Issues
```bash
# Monitor resources
htop

# Check network
nethogs

# Check disk
df -h
```

## Security Hardening

### 1. Firewall Setup
```bash
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw status
```

### 2. SSH Hardening
```bash
# Generate SSH key
ssh-keygen -t ed25519

# Edit SSH config
sudo nano /etc/ssh/sshd_config

# Settings:
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

### 3. File Permissions
```bash
# Secure .env file
chmod 600 /home/crypto/crypto-smart-money-agent/.env

# Secure logs
chmod 750 /home/crypto/crypto-smart-money-agent/logs
```

## Maintenance

### Regular Updates
```bash
# Update system monthly
sudo apt-get update
sudo apt-get upgrade -y

# Update Python packages
source venv/bin/activate
pip install --upgrade pip setuptools
pip list --outdated
pip install --upgrade package_name
```

### Health Checks
```bash
# Monitor logs weekly
pm2 logs crypto-agent --lines 100

# Check database
du -sh /home/crypto/crypto-smart-money-agent/data/

# Test alerts
python3 -c "# Test code here"
```

## Support

For deployment issues:
1. Check logs thoroughly
2. Review this guide
3. Open GitHub issue with logs
4. Contact maintainers

---

**Deployment completed!** 🎉

Your Crypto Smart Money AI Agent should now be running and continuously scanning the markets.
