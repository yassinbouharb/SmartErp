"""
SmartErp Telegram Bot Launcher
Run this file to start the bot: python run_bot.py
"""
import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(str(PROJECT_ROOT))

from telegram.bot import main

if __name__ == "__main__":
    print("🤖 SmartErp Telegram Bot")
    print("=" * 40)
    print("Bot token: 8722693842:AAF4Jkyyhn5EnDKTp9-UMy3_aMcsDeG-oHQ")
    print("Bot username: @lyna_services_BOT")
    print("\nSend /start on Telegram to begin!")
    print("-" * 40)
    main()
