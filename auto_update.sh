#!/bin/bash
# Auto-update script for NSFW Bot
# This script pulls latest changes from Git and restarts the bot

cd /root/nsfw-bot

echo "🔄 Checking for updates..."

# Pull latest changes
git pull origin main

if [ $? -eq 0 ]; then
    echo "✅ Updates pulled successfully!"
    
    # Install any new dependencies
    source .venv/bin/activate
    pip install -r requirements.txt
    
    echo "🔄 Restarting bot service..."
    systemctl restart nsfw-bot
    
    echo "✅ Bot updated and restarted successfully!"
else
    echo "❌ No updates available or git pull failed"
fi
