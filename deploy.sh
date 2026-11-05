#!/bin/bash
# Quick deploy script for Ubuntu server
# Run from your local machine: bash deploy.sh

SERVER="ubuntu@57.129.179.84"
REMOTE_DIR="/home/ubuntu/smarterp"
PASSWORD="c181Jmt1622"

echo "🚀 Deploying SmartErp to $SERVER..."

# Create remote directory
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER "mkdir -p $REMOTE_DIR && cd $REMOTE_DIR && git init"

# Copy all project files
echo "📁 Copying project files..."
sshpass -p "$PASSWORD" scp -r -o StrictHostKeyChecking=no \
  /c/Users/yassi/Desktop/SmartErp/. \
  $SERVER:$REMOTE_DIR/

# Install dependencies and setup
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'SSH_EOF'
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
sudo tee /etc/systemd/system/smarterp-bot.service > /dev/null <<EOF
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
SSH_EOF

echo "✅ Deployment complete!"
echo "Check bot status: ssh $SERVER 'systemctl status smarterp-bot'"
echo "View logs: ssh $SERVER 'journalctl -u smarterp-bot -f'"
