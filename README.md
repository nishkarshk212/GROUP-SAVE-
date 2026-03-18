# 🛡️ Telegram NSFW Detection Bot

A powerful Telegram bot that automatically detects and moderates NSFW (Not Safe For Work) content in group members' names and usernames.

## ✨ Features

- **Real-time Monitoring**: Automatically checks new members as they join the group
- **Name & Username Detection**: Scans first name, last name, and username for inappropriate content
- **Categorized Detection**: Identifies multiple categories of NSFW content:
  - 🔴 Sexual content
  - 🟠 Offensive language
  - 🟡 Drug-related terms
  - 🟠 Violence and harm
  - 🟡 Hate speech
  - 🟢 Scams and suspicious activity
- **Severity Levels**: Classifies violations from low to critical
- **Automated Actions**: Takes appropriate action based on severity (warning, temporary ban, permanent ban)
- **Admin Commands**: Allows admins to scan groups and check specific users
- **Customizable Word List**: Easy to modify and extend the NSFW word database

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- A Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))

### Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your bot token**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your bot token:
     ```
     TELEGRAM_BOT_TOKEN=your_bot_token_here
     ```

4. **Run the bot**:
   ```bash
   python bot.py
   ```

## 📖 Setup Instructions

### Getting Your Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the API token provided by BotFather
5. Paste it in your `.env` file

### Adding Bot to Your Group

1. Open your Telegram group
2. Tap on the group name to view group info
3. Select "Add Members"
4. Search for your bot by username (e.g., `@YourBotName`)
5. Add the bot to the group
6. **Make the bot an admin** (required for automatic moderation):
   - Go to Group Settings > Administrators > Add Administrator
   - Select your bot
   - Enable permissions: "Ban Users", "Delete Messages"

### Bot Commands

- `/start` - Start the bot and see introduction
- `/help` - Display help message with all commands
- `/check` - Check a specific user's profile (reply to their message or mention them)
- `/scan` - Scan all group administrators for violations (admin only)
- `/clear` - Clear warning history (admin only)

## 🔧 Configuration

Edit the `.env` file to customize bot behavior:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
MONITOR_MESSAGES=false          # Enable to monitor message content
AUTO_DELETE_MESSAGES=false      # Auto-delete violating messages
LOG_CHANNEL_ID=@your_channel    # Log violations to a channel
```

## 🎯 How It Works

### Detection Process

1. **Member Joins**: When a user joins the group, the bot is triggered
2. **Profile Analysis**: Bot checks:
   - First name
   - Last name
   - Username (if available)
3. **Text Processing**: Names are cleaned and normalized
4. **Word Matching**: Compared against NSFW word database
5. **Severity Assessment**: Violations classified as:
   - 🟢 Low - Minor issues
   - 🟡 Medium - Moderate concerns
   - 🟠 High - Serious violations
   - 🔴 Critical - Zero tolerance offenses
6. **Action Taken**:
   - **Critical**: Immediate permanent ban
   - **High**: Temporary ban (1 minute warning)
   - **Medium/Low**: Warning notification

### Severity Examples

- **Critical**: Child exploitation, terrorism, severe violence
- **High**: Sexual content, explicit material
- **Medium**: Hate speech, drug references
- **Low**: Mild profanity, scam indicators

## 📝 Customizing NSFW Words

Edit `nsfw_words.py` to customize detection:

```python
NSFW_WORDS = {
    'sexual': ['word1', 'word2', ...],
    'offensive': ['word1', 'word2', ...],
    'drugs': ['word1', 'word2', ...],
    'violence': ['word1', 'word2', ...],
    'hate': ['word1', 'word2', ...],
    'scam': ['word1', 'word2', ...]
}

# Zero-tolerance words (immediate ban)
CRITICAL_WORDS = {'word1', 'word2', ...}
```

## 🛠️ Troubleshooting

### Bot doesn't respond to commands
- Make sure the bot has joined the group
- Check if the bot token is correct in `.env`
- Ensure the bot is not disabled in the group

### Bot can't ban users
- Make the bot an administrator with "Ban Users" permission
- Check bot's permissions in group settings

### Bot not detecting names
- Some special characters or emojis might bypass detection
- Consider adding variations to the word list

### False positives
- Review and adjust the word list in `nsfw_words.py`
- Use the `/clear` command to remove warnings

## 🔒 Privacy & Security

- The bot only processes public information (names and usernames)
- No personal data is stored or transmitted
- All processing happens locally on your server
- Environment variables keep your bot token secure

## 📄 License

This project is provided as-is for educational and moderation purposes.

## 🤝 Contributing

Feel free to:
- Add more NSFW words to the database
- Improve detection algorithms
- Add new features
- Report bugs and issues

## ⚠️ Disclaimer

Use this bot responsibly. It's designed to help maintain safe communities but may occasionally produce false positives. Always review automated actions and adjust the word list to fit your community's needs.

## 📞 Support

For issues, questions, or suggestions, please open an issue in the repository.

---

**Made with ❤️ for safer Telegram communities**
# GROUP-SAVE-
