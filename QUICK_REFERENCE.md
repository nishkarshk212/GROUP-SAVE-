# 🛡️ NSFW Detection Bot - Quick Reference

## ✅ Bot is Running!

Your bot is now active and monitoring both **member names** AND **group messages**.

---

## 🔍 What the Bot Monitors

### 1. **Member Profiles** (Automatic)
- ✅ First Name
- ✅ Last Name  
- ✅ Username
- ✅ Checked when user joins or is promoted to admin

### 2. **Group Messages** (Real-time)
- ✅ All text messages in the group
- ✅ Automatically deleted if they contain NSFW content
- ✅ Warning sent to the user
- ✅ Repeat offenders get temporary bans

---

## ⚡ Message Monitoring Features

### Detection Categories:
- 🔴 **Sexual Content** - Explicit material, adult content
- 🟠 **Offensive Language** - Profanity, insults
- 🟡 **Drug References** - Illegal substances
- 🟠 **Violence** - Harm, threats, gore
- 🟡 **Hate Speech** - Racism, discrimination
- 🟢 **Scams** - Crypto schemes, fraud

### Automatic Actions:
- **Critical Severity**: Message deleted + User banned permanently
- **High Severity**: Message deleted + Final warning
- **Medium Severity**: Message deleted + Warning (auto-deleted after 30s)
- **Low Severity**: Message deleted + Warning (auto-deleted after 30s)

### Strike System:
- **1st offense**: Warning message
- **2nd offense** (medium/high): 10-minute temporary ban
- **Critical offense**: Immediate permanent ban

---

## 📋 Bot Commands

### For All Users:
- `/start` - Introduction message
- `/help` - Full help and instructions

### For Group Members:
- `/check` (reply to user) - Check someone's profile for NSFW content

### For Admins Only:
- `/scan` - Scan all group administrators
- `/clear` - Clear warning history for the group

---

## 🎯 Setup Checklist

✅ Bot token configured  
✅ Bot running in terminal  
✅ Dependencies installed  

### To Add to Your Group:

1. **Add bot to group** from Telegram
2. **Make bot an admin** with these permissions:
   - ✅ Ban users
   - ✅ Delete messages
3. **Bot starts monitoring immediately!**

---

## 🔧 How It Works

### When Someone Joins:
```
User joins → Bot checks name/username → 
If NSFW detected → Alert + Action taken
```

### When Someone Sends Message:
```
Message sent → Bot analyzes content → 
If NSFW detected → Delete message + Warn user + Track strike
```

---

## 💡 Tips

1. **Test the bot**: Try sending messages with mild inappropriate words to see it in action
2. **Monitor logs**: Watch the terminal to see what the bot detects
3. **Adjust word list**: Edit `nsfw_words.py` to customize detection
4. **Clear warnings**: Use `/clear` command if needed

---

## 🚨 Important Notes

- Bot must be **admin** to delete messages and ban users
- Warnings are tracked per group per user
- Auto-moderation happens in real-time
- All processing is local (no data sent externally)

---

## 📞 Testing

Try these tests (in a test group, not important groups):

1. **Name Test**: Create a test account with "NSFW" in the name and add to group
2. **Message Test**: Send a message containing inappropriate words

You should see immediate action from the bot!

---

**Bot Status**: ✅ RUNNING  
**Features**: Names + Usernames + Messages  
**Auto-Moderation**: ENABLED
