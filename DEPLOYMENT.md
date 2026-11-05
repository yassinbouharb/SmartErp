# SmartErp - Telegram Bot Deployment Guide

## 🚀 Deployment to Ubuntu Server (57.129.179.84)

### Option 1: Automated Script (Recommended)

Run from your local machine (Windows):
```bash
bash deploy.sh
```

### Option 2: Manual Deployment

**Step 1: Copy files to server**
```bash
scp -r . ubuntu@57.129.179.84:/home/ubuntu/smarterp/
```

**Step 2: SSH into server and setup**
```bash
ssh ubuntu@57.129.179.84
```

```bash
cd /home/ubuntu/smarterp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Create systemd service
sudo tee /etc/systemd/system/smarterp-bot.service > /dev/null << 'EOF'
[Unit]
Description=SmartErp Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/smarterp
ExecStart=/home/ubuntu/smarterp/venv/bin/python telegram/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable smarterp-bot
sudo systemctl start smarterp-bot

# Check status
sudo systemctl status smarterp-bot --no-pager
```

## 📋 Commands

| Command | Description |
|---------|-------------|
| `systemctl status smarterp-bot` | Check bot status |
| `journalctl -u smarterp-bot -f` | View logs |
| `systemctl restart smarterp-bot` | Restart bot |
| `systemctl stop smarterp-bot` | Stop bot |

## 🤖 Telegram Commands

- `/start` - Welcome message
- `/help` - Help
- `/products` - Product catalog
- `/invoices` - Recent invoices
- `/bl` - Delivery notes
- `/clients` - Client list
- `/balance` - Client balances
- `/stock` - Stock status
- `/stock_alerte` - Low stock alerts
- `/statistics` - Sales reports
- `/historique` - Client history
- `/bilan` - Accounting balance

## 📁 Project Structure

```
SmartErp/
├── telegram/
│   ├── bot.py           # Main bot file
│   └── config.py        # Bot token config
├── ai/agents/
│   ├── stock_agent.py          # Inventory module
│   ├── client_history_agent.py # Client history
│   ├── reports_agent.py        # Analytics
│   └── accounting_agent.py     # Accounting
├── repositories/
│   └── stock_repository.py     # Stock data layer
├── services/
│   └── stock_service.py        # Stock business logic
├── requirements.txt
├── deploy.sh                   # Deployment script
└── run_bot.py                 # Local launcher
```

## 🔧 Troubleshooting

**Bot not responding?**
```bash
sudo systemctl status smarterp-bot
sudo journalctl -u smarterp-bot -n 50
```

**Dependencies missing?**
```bash
cd /home/ubuntu/smarterp
source venv/bin/activate
pip install -r requirements.txt
```

**Playwright error?**
```bash
playwright install chromium
```

## 📝 Notes

- The bot uses Google Gemini AI (free tier)
- Data stored in Excel file: `ERP_Gestion.xlsx`
- Bot runs as a systemd service (auto-restart on failure)
- Logs available via `journalctl`
