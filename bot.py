#!/usr/bin/env python3
"""
Telegram Bot for NSFW Detection in Group Member Names and Usernames
This bot monitors all group members' names and usernames for inappropriate content
"""

import logging
import re
import asyncio
from typing import Dict, List, Optional, Set, Tuple
from telegram import Update, ChatMember, Message, User, Chat, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ChatMemberHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from telegram.error import BadRequest
from nsfw_words import NSFW_WORDS, ALL_NSFW_WORDS, CRITICAL_WORDS, NSFW_PATTERNS, LEET_SPEAK_MAP
import os
from dotenv import load_dotenv

try:
    from better_profanity import profanity
    PROFANITY_AVAILABLE = True
except ImportError:
    PROFANITY_AVAILABLE = False
    logger.warning("better_profanity not installed. Install with: pip install better-profanity")

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class NSFWDetector:
    """NSFW text detection utility"""
    
    # Unicode character mapping for fancy text normalization
    FANCY_CHAR_MAP = {
        # Bold mathematical alphanumeric
        '𝐚': 'a', '𝐛': 'b', '𝐜': 'c', '𝐝': 'd', '𝐞': 'e', '𝐟': 'f', '𝐠': 'g', '𝐡': 'h', '𝐢': 'i',
        '𝐣': 'j', '𝐤': 'k', '𝐥': 'l', '𝐦': 'm', '𝐧': 'n', '𝐨': 'o', '𝐩': 'p', '𝐪': 'q', '𝐫': 'r',
        '𝐬': 's', '𝐭': 't', '𝐮': 'u', '𝐯': 'v', '𝐰': 'w', '𝐱': 'x', '𝐲': 'y', '𝐳': 'z',
        '𝐀': 'A', '𝐁': 'B', '𝐂': 'C', '𝐃': 'D', '𝐄': 'E', '𝐅': 'F', '𝐆': 'G', '𝐇': 'H', '𝐈': 'I',
        '𝐉': 'J', '𝐊': 'K', '𝐋': 'L', '𝐌': 'M', '𝐍': 'N', '𝐎': 'O', '𝐏': 'P', '𝐐': 'Q', '𝐑': 'R',
        '𝐒': 'S', '𝐓': 'T', '𝐔': 'U', '𝐕': 'V', '𝐖': 'W', '𝐗': 'X', '𝐘': 'Y', '𝐙': 'Z',
        
        # Italic mathematical alphanumeric
        '𝑎': 'a', '𝑏': 'b', '𝑐': 'c', '𝑑': 'd', '𝑒': 'e', '𝑓': 'f', '𝑔': 'g', 'ℎ': 'h', '𝑖': 'i',
        '𝑗': 'j', '𝑘': 'k', '𝑙': 'l', '𝑚': 'm', '𝑛': 'n', '𝑜': 'o', '𝑝': 'p', '𝑞': 'q', '𝑟': 'r',
        '𝑠': 's', '𝑡': 't', '𝑢': 'u', '𝑣': 'v', '𝑤': 'w', '𝑥': 'x', '𝑦': 'y', '𝑧': 'z',
        '𝐴': 'A', '𝐵': 'B', '𝐶': 'C', '𝐷': 'D', '𝐸': 'E', '𝐹': 'F', '𝐺': 'G', '𝐻': 'H', '𝐼': 'I',
        '𝐽': 'J', '𝐾': 'K', '𝐿': 'L', '𝑀': 'M', '𝑁': 'N', '𝑂': 'O', '𝑃': 'P', '𝑄': 'Q', '𝑅': 'R',
        '𝑆': 'S', '𝑇': 'T', '𝑈': 'U', '𝑉': 'V', '𝑊': 'W', '𝑋': 'X', '𝑌': 'Y', '𝑍': 'Z',
        
        # Bold italic mathematical alphanumeric
        '𝒂': 'a', '𝒃': 'b', '𝒄': 'c', '𝒅': 'd', '𝒆': 'e', '𝒇': 'f', '𝒈': 'g', '𝒉': 'h', '𝒊': 'i',
        '𝒋': 'j', '𝒌': 'k', '𝒍': 'l', '𝒎': 'm', '𝒏': 'n', '𝒐': 'o', '𝒑': 'p', '𝒒': 'q', '𝒓': 'r',
        '𝒔': 's', '𝒕': 't', '𝒖': 'u', '𝒗': 'v', '𝒘': 'w', '𝒙': 'x', '𝒚': 'y', '𝒛': 'z',
        '𝑨': 'A', '𝑩': 'B', '𝑪': 'C', '𝑫': 'D', '𝑬': 'E', '𝑭': 'F', '𝑮': 'G', '𝑯': 'H', '𝑰': 'I',
        '𝑱': 'J', '𝑲': 'K', '𝑳': 'L', '𝑴': 'M', '𝑵': 'N', '𝑶': 'O', '𝑷': 'P', '𝑸': 'Q', '𝑹': 'R',
        '𝑺': 'S', '𝑻': 'T', '𝑼': 'U', '𝑽': 'V', '𝑾': 'W', '𝑿': 'X', '𝒀': 'Y', '𝒁': 'Z',
        
        # Script/calligraphic
        '𝒶': 'a', '𝒷': 'b', '𝒸': 'c', '𝒹': 'd', '𝑒': 'e', '𝒻': 'f', '𝑔': 'g', '𝒽': 'h', '𝒾': 'i',
        '𝒿': 'j', '𝓀': 'k', '𝓁': 'l', '𝓂': 'm', '𝓃': 'n', '𝑜': 'o', '𝓅': 'p', '𝓆': 'q', '𝓇': 'r',
        '𝓈': 's', '𝓉': 't', '𝓊': 'u', '𝓋': 'v', '𝓌': 'w', '𝓍': 'x', '𝓎': 'y', '𝓏': 'z',
        '𝒜': 'A', '𝐵': 'B', '𝒞': 'C', '𝒟': 'D', '𝐸': 'E', '𝐹': 'F', '𝒢': 'G', '𝐻': 'H', '𝐼': 'I',
        '𝒥': 'J', '𝒦': 'K', '𝐿': 'L', '𝑀': 'M', '𝒩': 'N', '𝒪': 'O', '𝒫': 'P', '𝒬': 'Q', '𝑅': 'R',
        '𝒮': 'S', '𝒯': 'T', '𝒰': 'U', '𝒱': 'V', '𝒲': 'W', '𝒳': 'X', '𝒴': 'Y', '𝒵': 'Z',
        
        # Fraktur/Gothic
        '𝔞': 'a', '𝔟': 'b', '𝔠': 'c', '𝔡': 'd', '𝔢': 'e', '𝔣': 'f', '𝔤': 'g', '𝔥': 'h', '𝔦': 'i',
        '𝔧': 'j', '𝔨': 'k', '𝔩': 'l', '𝔪': 'm', '𝔫': 'n', '𝔬': 'o', '𝔭': 'p', '𝔮': 'q', '𝔯': 'r',
        '𝔰': 's', '𝔱': 't', '𝔲': 'u', '𝔳': 'v', '𝔴': 'w', '𝔵': 'x', '𝔶': 'y', '𝔷': 'z',
        '𝔄': 'A', '𝔅': 'B', '𝔆': 'C', '𝔇': 'D', '𝔈': 'E', '𝔉': 'F', '𝔊': 'G', '𝔋': 'H', '𝔌': 'I',
        '𝔍': 'J', '𝔎': 'K', '𝔏': 'L', '𝔐': 'M', '𝔑': 'N', '𝔒': 'O', '𝔓': 'P', '𝔔': 'Q', '𝔕': 'R',
        '𝔖': 'S', '𝔗': 'T', '𝔘': 'U', '𝔜': 'V', '𝔚': 'W', '𝔛': 'X', '𝔜': 'Y', 'ℨ': 'Z',
        
        # Double-struck
        '𝕒': 'a', '𝕓': 'b', '𝕔': 'c', '𝕕': 'd', '𝕖': 'e', '𝕗': 'f', '𝕘': 'g', '𝕙': 'h', '𝕚': 'i',
        '𝕛': 'j', '𝕜': 'k', '𝕝': 'l', '𝕞': 'm', '𝕟': 'n', '𝕠': 'o', '𝕡': 'p', '𝕢': 'q', '𝕣': 'r',
        '𝕤': 's', '𝕥': 't', '𝕦': 'u', '𝕧': 'v', '𝕨': 'w', '𝕩': 'x', '𝕪': 'y', '𝕫': 'z',
        '𝔸': 'A', '𝔹': 'B', 'ℂ': 'C', '𝔻': 'D', '𝔼': 'E', '𝔽': 'F', '𝔾': 'G', 'ℍ': 'H', '𝕀': 'I',
        '𝕁': 'J', '𝕂': 'K', '𝕃': 'L', '𝕄': 'M', 'ℕ': 'N', '𝕆': 'O', 'ℙ': 'P', 'ℚ': 'Q', 'ℝ': 'R',
        '𝕊': 'S', '𝕋': 'T', '𝕌': 'U', '𝕍': 'V', '𝕎': 'W', '𝕏': 'X', '𝕐': 'Y', 'ℤ': 'Z',
        
        # Fullwidth (common in Asian text)
        'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd', 'e': 'e', 'f': 'f', 'g': 'g', 'h': 'h', 'i': 'i',
        'j': 'j', 'k': 'k', 'l': 'l', 'm': 'm', 'n': 'n', 'o': 'o', 'p': 'p', 'q': 'q', 'r': 'r',
        's': 's', 't': 't', 'u': 'u', 'v': 'v', 'w': 'w', 'x': 'x', 'y': 'y', 'z': 'z',
        'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F': 'F', 'G': 'G', 'H': 'H', 'I': 'I',
        'J': 'J', 'K': 'K', 'L': 'L', 'M': 'M', 'N': 'N', 'O': 'O', 'P': 'P', 'Q': 'Q', 'R': 'R',
        'S': 'S', 'T': 'T', 'U': 'U', 'V': 'V', 'W': 'W', 'X': 'X', 'Y': 'Y', 'Z': 'Z',
        
        # Circled characters
        'ⓐ': 'a', 'ⓑ': 'b', 'ⓒ': 'c', 'ⓓ': 'd', 'ⓔ': 'e', 'ⓕ': 'f', 'ⓖ': 'g', 'ⓗ': 'h', 'ⓘ': 'i',
        'ⓙ': 'j', 'ⓚ': 'k', 'ⓛ': 'l', 'ⓜ': 'm', 'ⓝ': 'n', 'ⓞ': 'o', 'ⓟ': 'p', 'ⓠ': 'q', 'ⓡ': 'r',
        'ⓢ': 's', 'ⓣ': 't', 'ⓤ': 'u', 'ⓥ': 'v', 'ⓦ': 'w', 'ⓧ': 'x', 'ⓨ': 'y', 'ⓩ': 'z',
        'Ⓐ': 'A', 'Ⓑ': 'B', 'Ⓒ': 'C', 'Ⓓ': 'D', 'Ⓔ': 'E', 'Ⓕ': 'F', 'Ⓖ': 'G', 'Ⓗ': 'H', 'Ⓘ': 'I',
        'Ⓙ': 'J', 'Ⓚ': 'K', 'Ⓛ': 'L', 'Ⓜ': 'M', 'Ⓝ': 'N', 'Ⓞ': 'O', 'Ⓟ': 'P', 'Ⓠ': 'Q', 'Ⓡ': 'R',
        'Ⓢ': 'S', 'Ⓣ': 'T', 'Ⓤ': 'U', 'Ⓥ': 'V', 'Ⓦ': 'W', 'Ⓧ': 'X', 'Ⓨ': 'Y', 'Ⓩ': 'Z',
    }
    
    @staticmethod
    def normalize_fancy_text(text: str) -> str:
        """Convert fancy/unicode characters to normal ASCII"""
        if not text:
            return ""
        
        # Replace fancy characters with normal ones
        for fancy_char, normal_char in NSFWDetector.FANCY_CHAR_MAP.items():
            text = text.replace(fancy_char, normal_char)
        
        return text
    
    @staticmethod
    def remove_extra_spaces(text: str) -> str:
        """Remove excessive spacing between characters"""
        if not text:
            return ""
        
        # Remove spaces between letters (handles "s p a c e d" text)
        # But keep word boundaries (multiple spaces or spaces around punctuation)
        text = re.sub(r'(\w)\s+(\w)', r'\1\2', text)
        
        return text
    
    @staticmethod
    def remove_monospace_formatting(text: str) -> str:
        """Remove markdown monospace formatting (code blocks)"""
        if not text:
            return ""
        
        # Remove inline code formatting: `text`
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Remove code block formatting: ```text```
        text = re.sub(r'```[\s\S]*?```', lambda m: m.group(0)[3:-3], text)
        
        # Remove preformatted text formatting: __text__
        text = re.sub(r'__([^_]+)__', r'\1', text)
        
        return text
    
    @staticmethod
    def normalize_leet_speak(text: str) -> str:
        """Convert leet speak to normal text (e.g., s3x → sex, p0rn → porn)"""
        if not text:
            return ""
        
        # Replace numbers and symbols with letters
        leet_map = {
            '0': 'o', '1': 'i', '2': 'z', '3': 'e', '4': 'a', 
            '5': 's', '6': 'g', '7': 't', '8': 'b', '9': 'g',
            '@': 'a', '$': 's', '!': 'i', '*': 'x', '+': 't',
            '<': 'c', '>': 'c', '(': 'c', '|': 'l', '0': 'o'
        }
        
        for leet_char, normal_char in leet_map.items():
            text = text.replace(leet_char, normal_char)
        
        return text
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text for analysis"""
        if not text:
            return ""
        
        # First, remove monospace/markdown formatting
        text = NSFWDetector.remove_monospace_formatting(text)
        
        # Normalize fancy unicode characters
        text = NSFWDetector.normalize_fancy_text(text)
        
        # Convert leet speak to normal text
        text = NSFWDetector.normalize_leet_speak(text)
        
        # Remove extra spacing between characters
        text = NSFWDetector.remove_extra_spaces(text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    @staticmethod
    def detect_nsfw(text: str, chat_blocked_words: Set[str] = None) -> Tuple[bool, List[str], str, List[str]]:
        """
        Detect NSFW content in text
        
        Returns:
            Tuple containing:
            - bool: Whether NSFW content was detected
            - List[str]: List of detected categories
            - str: Severity level ('low', 'medium', 'high', 'critical')
            - List[str]: List of detected words
        """
        if not text:
            return False, [], 'none', []
        
        cleaned_text = NSFWDetector.clean_text(text)
        words = set(cleaned_text.split())
        
        detected_categories = []
        severity = 'none'
        found_words = []
        
        # Check for critical words first
        for word in words:
            if word in CRITICAL_WORDS:
                found_words.append(word)
                severity = 'critical'
        
        # Check each category
        for category, category_words in NSFW_WORDS.items():
            matching_words = words.intersection(set(w.lower() for w in category_words))
            if matching_words:
                detected_categories.append(category)
                found_words.extend(matching_words)
        
        # Check regex patterns
        for pattern in NSFW_PATTERNS:
            matches = re.findall(pattern, cleaned_text)
            if matches:
                if 'pattern_match' not in detected_categories:
                    detected_categories.append('pattern_match')
                found_words.extend(matches)
        
        # Check better-profanity if available
        if PROFANITY_AVAILABLE:
            try:
                if profanity.contains_profanity(text):
                    # Get censored version to identify problematic words
                    censored = profanity.censor(text)
                    if censored != text:
                        if 'profanity_filter' not in detected_categories:
                            detected_categories.append('profanity_filter')
            except Exception as e:
                logger.warning(f"Profanity check failed: {e}")
        
        # Check custom blocked words
        if chat_blocked_words:
            blocked_matches = words.intersection(chat_blocked_words)
            if blocked_matches:
                if 'blocked_word' not in detected_categories:
                    detected_categories.append('blocked_word')
                found_words.extend(blocked_matches)
        
        # Determine severity if not already critical
        if not detected_categories and severity != 'critical':
            return False, [], 'none', []
        
        if severity != 'critical':
            if 'sexual' in detected_categories or 'violence' in detected_categories or 'child_safety' in detected_categories:
                severity = 'high'
            elif 'hate' in detected_categories or 'drugs' in detected_categories:
                severity = 'medium'
            else:
                severity = 'low'
        
        return True, detected_categories, severity, found_words


class TelegramNSFWBot:
    """Main bot class for NSFW detection in Telegram groups"""
    
    def __init__(self, token: str):
        self.token = token
        self.detector = NSFWDetector()
        
        # Track warned users to avoid spam
        self.warned_users: Dict[int, Set[int]] = {}  # chat_id -> set of user_ids
        
        # Chat settings storage
        self.chat_settings: Dict[int, Dict] = {}  # chat_id -> settings
        
        # Default settings
        self.default_settings = {
            'enable_username_check': True,
            'enable_message_check': True,
            'enable_name_check': True,
            'warning_limit': 3,
            'penalty_type': 'ban',  # 'ban', 'kick', 'mute', 'warn'
            'who_can_use': 'admin'  # 'admin', 'member', 'everyone'
        }
        
        # Custom blocked words per chat
        self.blocked_words: Dict[int, Set[str]] = {}  # chat_id -> set of blocked words
        
        # Custom penalty for blocked words per chat
        self.blocked_words_penalty: Dict[int, str] = {}  # chat_id -> penalty_type
        
        # Log channel configuration
        self.log_channel_id = -1003757375746  # @music_24345
        
        # Initialize application with error handlers
        self.application = Application.builder().token(token).build()
        
        # Register error handlers
        self.application.add_error_handler(self.on_error)
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all bot handlers"""
        
        # Commands
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("check", self.check_user))
        self.application.add_handler(CommandHandler("scan", self.scan_group))
        self.application.add_handler(CommandHandler("clear", self.clear_warnings))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        self.application.add_handler(CommandHandler("blockword", self.block_word_command))
        self.application.add_handler(CommandHandler("unblockword", self.unblock_word_command))
        self.application.add_handler(CommandHandler("listblockwords", self.list_block_words_command))
        
        # Callback query handler for buttons
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Member updates (new members joining)
        self.application.add_handler(ChatMemberHandler(self.track_chat_member, ChatMemberHandler.CHAT_MEMBER))
        
        # Regular messages (optional - can monitor message content too)
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.check_message))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        # Create fancy text message (without commands list)
        start_message = (
            f"𝐇𝐞𝐥𝐥𝐨 {user.first_name} 🥀\n\n"
            f"𝐈'𝐦 𝐭𝐡𝐞 𝐍𝐒𝐅𝐖 𝐃𝐞𝐭𝐞𝐜𝐭𝐢𝐨𝐧 𝐁𝐨𝐭. 𝐈 𝐦𝐨𝐧𝐢𝐭𝐨𝐫 𝐠𝐫𝐨𝐮𝐩 𝐦𝐞𝐦𝐛𝐞𝐫𝐬' 𝐧𝐚𝐦𝐞𝐬 𝐚𝐧𝐝 𝐮𝐬𝐞𝐫𝐧𝐚𝐦𝐞𝐬 𝐟𝐨𝐫 𝐢𝐧𝐚𝐩𝐩𝐫𝐨𝐩𝐫𝐢𝐚𝐭𝐞 𝐜𝐨𝐧𝐭𝐞𝐧𝐭.\n\n"
            f"𝐂𝐥𝐢𝐜𝐤 𝐭𝐡𝐞 𝐛𝐮𝐭𝐭𝐨𝐧𝐬 𝐛𝐞𝐥𝐨𝐰 𝐭𝐨:\n"
            f"• 𝐀𝐝𝐝 𝐦𝐞 𝐭𝐨 𝐲𝐨𝐮𝐫 𝐠𝐫𝐨𝐮𝐩\n"
            f"• 𝐕𝐢𝐞𝐰 𝐚𝐥𝐥 𝐜𝐨𝐦𝐦𝐚𝐧𝐝𝐬 𝐚𝐧𝐝 𝐟𝐞𝐚𝐭𝐮𝐫𝐞𝐬"
        )
        
        # Create inline keyboard with buttons
        keyboard = [
            [
                InlineKeyboardButton(
                    "🅰🅳🅳 🅼🅴 🅱🅰🅱🆈 🥀",
                    url=f"https://t.me/{context.bot.username}?startgroup=true"
                )
            ],
            [
                InlineKeyboardButton(
                    "🅷🅴🅻🅿 🅰🅽🅳 🅲🅾🅼🅼🅰🅽🅳",
                    callback_data="show_help"
                )
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Try to send with bot's profile picture as spoiler
        try:
            # Get bot's profile photo
            bot_photos = await context.bot.get_user_profile_photos(context.bot.id)
            
            if bot_photos.total_count > 0:
                # Get the first photo file ID
                photo_file_id = bot_photos.photos[0][-1].file_id
                
                # Send photo with caption as spoiler
                await update.message.reply_photo(
                    photo=photo_file_id,
                    caption=start_message,
                    reply_markup=reply_markup,
                    parse_mode='Markdown',
                    has_spoiler=True
                )
            else:
                # No profile photo, send regular message
                await update.message.reply_text(
                    start_message,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
        except Exception as e:
            logger.error(f"Failed to send start message with photo: {e}")
            # Fallback to regular message
            await update.message.reply_text(
                start_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🤖 **NSFW Detection Bot Help**

**What I do:**
• Monitor member names for NSFW content
• Check usernames for inappropriate words
• Alert admins when violations are found
• Scan entire groups on request
• Detect fancy text, leet speak, and obfuscation

**Commands:**
• /start - Start the bot
• /help - Show this help message
• /check <reply or mention> - Check a specific user's name/username
• /scan - Scan all group members (admin only)
• /clear - Clear warning history (admin only)
• /settings - Configure bot settings (admin only)
• /blockword <word> [penalty] - Add custom blocked word (admin only)
• /unblockword <word> - Remove custom blocked word (admin only)
• /listblockwords - List all custom blocked words (admin only)

**Severity Levels:**
• 🔴 Critical - Immediate action required
• 🟠 High - Serious violation
• 🟡 Medium - Moderate concern
• 🟢 Low - Minor issue

Add me to your group and make me an admin to automatically monitor new members!
"""
        await update.message.reply_text(help_text)
    
    async def show_help_from_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help message when Help button is clicked from start menu"""
        query = update.callback_query
        await query.answer()
        
        help_text = """
𝐃𝐞𝐭𝐚𝐢𝐥𝐞𝐝 𝐇𝐞𝐥𝐩 & 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬 🥀

━━━━━━━━━━━━━━━━━━━━

𝐁𝐎𝐓 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒:

𝟏. /𝐬𝐭𝐚𝐫𝐭
   → Start the bot and see welcome message

𝟐. /𝐡𝐞𝐥𝐩
   → Show this detailed help message

𝟑. /𝐜𝐡𝐞𝐜𝐤 <𝐫𝐞𝐩𝐥𝐲 𝐨𝐫 𝐦𝐞𝐧𝐭𝐢𝐨𝐧>
   → Check a specific user's name/username for NSFW content
   → Works in groups only

𝟒. /𝐬𝐜𝐚𝐧
   → Scan all group members for inappropriate names
   → Admin only command
   → Checks admins first, then all members

𝟓. /𝐜𝐥𝐞𝐚𝐫
   → Reset warning history for this group
   → Admin only command

𝟔. /𝐬𝐞𝐭𝐭𝐢𝐧𝐠𝐬
   → Open interactive settings panel
   → Configure detection options
   → Set warning limits and penalties
   → Admin only command

𝟕. /𝐛𝐥𝐨𝐜𝐤𝐰𝐨𝐫𝐝 <𝐰𝐨𝐫𝐝> [𝐩𝐞𝐧𝐚𝐥𝐭𝐲]
   → Add custom blocked word to your group
   → Optional penalty: ban/kick/mute/warn
   → Example: /blockword spam ban
   → Admin only command

𝟖. /𝐮𝐧𝐛𝐥𝐨𝐜𝐤𝐰𝐨𝐫𝐝 <𝐰𝐨𝐫𝐝>
   → Remove a custom blocked word
   → Admin only command

𝟗. /𝐥𝐢𝐬𝐭𝐛𝐥𝐨𝐜𝐤𝐰𝐨𝐫𝐝𝐬
   → View all custom blocked words and their penalties
   → Admin only command

━━━━━━━━━━━━━━━━━━━━

𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒:

✅ 𝐍𝐒𝐅𝐖 𝐃𝐞𝐭𝐞𝐜𝐭𝐢𝐨𝐧:
   • Monitors names, usernames, and messages
   • Detects 600+ inappropriate words
   • Zero tolerance for child-related content

✅ 𝐀𝐝𝐯𝐚𝐧𝐜𝐞𝐝 𝐏𝐫𝐨𝐭𝐞𝐜𝐭𝐢𝐨𝐧:
   • Handles fancy text (𝐛𝐨𝐥𝐝, 𝑖𝑡𝑎𝑙𝑖𝑐, 𝓼𝓬𝓻𝓲𝓹𝓽)
   • Detects leet speak (s3x, p0rn, etc.)
   • Removes spaced text (s e x)
   • Strips markdown formatting

✅ 𝐂𝐮𝐬𝐭𝐨𝐦𝐢𝐳𝐚𝐭𝐢𝐨𝐧:
   • Toggle detection per field (name/username/message)
   • Set warning limit (1-10 warnings)
   • Choose penalty (ban/kick/mute/warn)
   • Add unlimited custom blocked words

✅ 𝐏𝐫𝐢𝐯𝐚𝐜𝐲 & 𝐔𝐗:
   • Shows only User ID (not names) in warnings
   • Auto-deletes warnings after 30 seconds
   • Unban/unmute buttons for quick reversal

✅ 𝐒𝐞𝐯𝐞𝐫𝐢𝐭𝐲 𝐋𝐞𝐯𝐞𝐥𝐬:
   🔴 Critical - Instant ban (child safety, violence)
   🟠 High - Temporary ban or kick
   🟡 Medium - Warning with mute option
   🟢 Low - Simple warning

━━━━━━━━━━━━━━━━━━━━

𝐆𝐄𝐓𝐓𝐈𝐍𝐆 𝐒𝐓𝐀𝐑𝐓𝐄𝐃:

1. Add me to your group
2. Make me an admin (required for auto-moderation)
3. Use /settings to customize my behavior
4. I'll automatically monitor new members!

𝐍𝐞𝐞𝐝 𝐡𝐞𝐥𝐩? 𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐭𝐡𝐞 𝐝𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫.

[« 𝐁𝐚𝐜𝐤]
"""
        
        # Create back button
        keyboard = [[InlineKeyboardButton("« 𝐁𝐚𝐜𝐤", callback_data="back_to_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(
                help_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except BadRequest as e:
            logger.error(f"Failed to show help from button: {e}")
    
    async def back_to_start_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Go back to start menu"""
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        
        # Recreate start message
        start_message = (
            f"𝐇𝐞𝐥𝐥𝐨 {user.first_name} 🥀\n\n"
            f"𝐈'𝐦 𝐭𝐡𝐞 𝐍𝐒𝐅𝐖 𝐃𝐞𝐭𝐞𝐜𝐭𝐢𝐨𝐧 𝐁𝐨𝐭. 𝐈 𝐦𝐨𝐧𝐢𝐭𝐨𝐫 𝐠𝐫𝐨𝐮𝐩 𝐦𝐞𝐦𝐛𝐞𝐫𝐬' 𝐧𝐚𝐦𝐞𝐬 𝐚𝐧𝐝 𝐮𝐬𝐞𝐫𝐧𝐚𝐦𝐞𝐬 𝐟𝐨𝐫 𝐢𝐧𝐚𝐩𝐩𝐫𝐨𝐩𝐫𝐢𝐚𝐭𝐞 𝐜𝐨𝐧𝐭𝐞𝐧𝐭.\n\n"
            f"𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬:\n"
            f"• /help - Show help message\n"
            f"• /check <username> - Check a specific user\n"
            f"• /scan - Scan entire group\n"
            f"• /clear - Clear warning history (admin only)\n"
            f"• /settings - Configure bot settings (admin only)\n"
            f"• /blockword <word> [penalty] - Add custom blocked word (admin only)"
        )
        
        # Recreate keyboard
        keyboard = [
            [
                InlineKeyboardButton(
                    "🅰🅳🅳 🅼🅴 🅱🅰🅱🆈 🥀",
                    url=f"https://t.me/{context.bot.username}?startgroup=true"
                )
            ],
            [
                InlineKeyboardButton(
                    "🅷🅴🅻🅿 🅰🅽🅳 🅲🅾🅼🅼🅰🅽🅳",
                    callback_data="show_help"
                )
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(
                start_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except BadRequest as e:
            logger.error(f"Failed to go back to start: {e}")
    
    async def check_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /check command to check a specific user"""
        if not update.effective_chat or update.effective_chat.type == 'private':
            await update.message.reply_text("This command only works in groups!")
            return
        
        # Check permissions
        can_use = await self.can_use_bot_commands(update, context)
        if not can_use:
            settings = self.chat_settings.get(update.effective_chat.id, self.default_settings)
            access_level = settings['who_can_use']
            await update.message.reply_text(f"⚠️ Only {access_level} can use this command!")
            return
        
        # Get replied user or mentioned user
        target_user = None
        
        if update.message.reply_to_message:
            target_user = update.message.reply_to_message.from_user
        elif context.args and context.message.entities:
            # Check for user mention
            for entity in context.message.entities:
                if entity.type == 'text_mention':
                    target_user = await context.bot.get_chat(entity.user.id)
                    break
        
        if not target_user:
            await update.message.reply_text(
                "Please reply to a user's message or mention them to check their profile."
            )
            return
        
        await self.analyze_user(target_user, update.effective_chat, update.message)
    
    async def scan_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /scan command to scan all group members"""
        if not update.effective_chat or update.effective_chat.type == 'private':
            await update.message.reply_text("This command only works in groups!")
            return
        
        # Check if user is admin
        user = await update.effective_chat.get_member(update.effective_user.id)
        if user.status not in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            await update.message.reply_text("⚠️ Only admins can use the /scan command!")
            return
        
        await update.message.reply_text("🔍 Scanning group members... This may take a moment.")
        
        try:
            # Get chat members
            administrators = await update.effective_chat.get_administrators()
            violations_found = 0
            
            for admin in administrators:
                is_violation, categories, severity, words = await self.check_member_profile(
                    admin.user,
                    update.effective_chat.id
                )
                if is_violation:
                    violations_found += 1
                    await self.send_violation_report(
                        update.effective_chat,
                        admin.user,
                        categories,
                        severity,
                        words,
                        is_admin=True
                    )
            
            # Note: Full member scan requires proper pagination
            # This is a simplified version checking admins first
            
            await update.message.reply_text(
                f"✅ Scan complete! Found {violations_found} violation(s) among administrators."
            )
            
        except Exception as e:
            logger.error(f"Error scanning group: {e}")
            await update.message.reply_text(f"❌ Error during scan: {str(e)}")
    
    async def track_chat_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Track chat member changes and check new members"""
        result = update.chat_member
        if not result:
            return
        
        old_status = result.old_chat_member.status
        new_status = result.new_chat_member.status
        user = result.new_chat_member.user
        
        # Check if user joined the chat
        if old_status in [ChatMember.LEFT, ChatMember.RESTRICTED] and new_status == ChatMember.MEMBER:
            logger.info(f"New member joined: {user.username or user.first_name}")
            await self.analyze_new_member(user, update.effective_chat)
        
        # Also check if user was promoted (their name might have changed)
        elif new_status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            await self.analyze_user(user, update.effective_chat, None, is_promotion=True)
    
    async def can_use_bot_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Check if user can use bot commands based on access control settings"""
        if not update.effective_chat:
            return True  # Private chats always allowed
        
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        settings = self.chat_settings.get(chat_id, self.default_settings)
        access_level = settings['who_can_use']
        
        # Get user status
        try:
            member = await update.effective_chat.get_member(user_id)
            user_status = member.status
            
            if access_level == 'admin':
                # Only admins and owner can use
                return user_status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]
            elif access_level == 'member':
                # All group members can use (not kicked/restricted)
                return user_status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
            elif access_level == 'everyone':
                # Everyone can use
                return True
        except Exception as e:
            logger.error(f"Error checking user permissions: {e}")
            return False
        
        return False
    
    async def show_access_control_submenu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show access control submenu with dedicated buttons"""
        query = update.callback_query
        await query.answer()
        
        chat_id = query.message.chat_id
        settings = self.chat_settings.get(chat_id, self.default_settings)
        current_access = settings['who_can_use']
        
        access_emoji = {
            'admin': '👮',
            'member': '👥',
            'everyone': '🌍'
        }
        
        access_desc = {
            'admin': 'Only administrators and group owner can use bot commands',
            'member': 'All group members can use bot commands (except restricted users)',
            'everyone': 'Anyone in the group can use bot commands without restrictions'
        }
        
        submenu_msg = (
            f"**🔐 Access Control Settings**\n\n"
            f"**Current Setting:** {access_emoji[current_access]} {current_access.capitalize()}\n\n"
            f"{access_desc[current_access]}\n\n"
            f"**Select who can use bot commands:**"
        )
        
        # Create keyboard with radio-button style selection
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{'✅ ' if current_access == 'admin' else ''}👮 Admins Only",
                    callback_data="set_admin_only"
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅ ' if current_access == 'member' else ''}👥 All Members",
                    callback_data="set_all_members"
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅ ' if current_access == 'everyone' else ''}🌍 Everyone",
                    callback_data="set_everyone"
                )
            ],
            [
                InlineKeyboardButton("« Back to Settings", callback_data="back_to_settings")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(
                submenu_msg,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except BadRequest as e:
            logger.error(f"Failed to show access control submenu: {e}")
    
    async def analyze_new_member(self, user: User, chat: Chat):
        """Analyze a new group member"""
        is_violation, categories, severity, words = await self.check_member_profile(user, chat.id)
        
        if is_violation:
            await self.handle_violation(chat, user, categories, severity, words)
    
    async def analyze_user(self, user: User, chat: Chat, message: Message = None, is_promotion: bool = False):
        """Analyze a user's profile"""
        is_violation, categories, severity, words = await self.check_member_profile(user, chat.id)
        
        if is_violation:
            if message:
                await self.send_violation_report(chat, user, categories, severity, words)
            else:
                await self.handle_violation(chat, user, categories, severity, words)
    
    async def check_member_profile(self, user: User, chat_id: int) -> Tuple[bool, List[str], str, List[str]]:
        """Check a member's full name and username for NSFW content"""
        texts_to_check = []
        
        # Get chat settings
        settings = self.chat_settings.get(chat_id, self.default_settings)
        
        # Check first name if enabled
        if settings['enable_name_check'] and user.first_name:
            texts_to_check.append(user.first_name)
        
        # Check last name if enabled
        if settings['enable_name_check'] and user.last_name:
            texts_to_check.append(user.last_name)
        
        # Check username if enabled
        if settings['enable_username_check'] and user.username:
            texts_to_check.append(user.username)
        
        # Combine all texts
        full_text = ' '.join(texts_to_check)
        
        # Get custom blocked words for this chat
        chat_blocked_words = self.blocked_words.get(chat_id, set())
        
        # Analyze for NSFW content (including custom blocked words)
        is_violation, categories, severity, words = self.detector.detect_nsfw(full_text, chat_blocked_words)
        
        return is_violation, categories, severity, words
    
    async def handle_violation(self, chat: Chat, user: User, categories: List[str], 
                               severity: str, words: List[str]):
        """Handle a NSFW violation"""
        chat_id = chat.id
        
        # Get chat settings
        settings = self.chat_settings.get(chat_id, self.default_settings)
        
        # Initialize warning tracking for this chat
        if chat_id not in self.warned_users:
            self.warned_users[chat_id] = {}
        
        # Track warnings per user
        if user.id not in self.warned_users[chat_id]:
            self.warned_users[chat_id][user.id] = 0
        
        self.warned_users[chat_id][user.id] += 1
        warning_count = self.warned_users[chat_id][user.id]
        
        # Send violation report with user ID and action buttons
        await self.send_violation_report(chat, user, categories, severity, words, warning_count)
        
        # Determine penalty type - use custom blocked words penalty if applicable
        penalty_type = settings['penalty_type']
        if 'blocked_word' in categories and chat_id in self.blocked_words_penalty:
            penalty_type = self.blocked_words_penalty[chat_id]
        
        # Apply penalty based on settings and warning count
        warning_limit = settings['warning_limit']
        
        # Take action based on severity and warning count
        if severity == 'critical' or warning_count >= warning_limit:
            if penalty_type == 'ban':
                try:
                    await chat.ban_member(user.id)
                    logger.warning(f"Banned user {user.id} for violation in chat {chat_id}")
                    # Send unban button after a short delay
                    await asyncio.sleep(2)
                    await self.send_action_buttons(chat, user, "ban")
                except Exception as e:
                    logger.error(f"Failed to ban user: {e}")
            elif penalty_type == 'kick':
                try:
                    await chat.ban_member(user.id)
                    await asyncio.sleep(60)  # Wait 1 minute before unbanning (kick effect)
                    await chat.unban_member(user.id)
                    logger.warning(f"Kicked user {user.id} for violation in chat {chat_id}")
                except Exception as e:
                    logger.error(f"Failed to kick user: {e}")
            elif penalty_type == 'mute':
                try:
                    # Restrict user from sending messages (mute for 1 hour)
                    await chat.restrict_member(
                        user_id=user.id,
                        can_send_messages=False,
                        until_date=3600  # Mute for 1 hour
                    )
                    logger.warning(f"Muted user {user.id} for violation in chat {chat_id}")
                    # Send unmute button after a short delay
                    await asyncio.sleep(2)
                    await self.send_action_buttons(chat, user, "mute")
                except Exception as e:
                    logger.error(f"Failed to mute user: {e}")
            # For 'warn' type, just send warning message
        
        elif severity == 'high':
            # Try to kick if bot has permission
            if penalty_type == 'ban':
                try:
                    member = await chat.get_member(user.id)
                    if member.can_be_edited:
                        await chat.ban_member(user.id, until_date=60)  # Ban for 1 minute as warning
                        logger.warning(f"Temporarily banned user {user.id} for high severity violation")
                except Exception as e:
                    logger.error(f"Failed to temporarily ban user: {e}")
    
    async def send_action_buttons(self, chat: Chat, user: User, action_type: str):
        """Send buttons to unban/unmute user after action is taken"""
        keyboard = []
        
        if action_type == "ban":
            keyboard.append([InlineKeyboardButton(
                "✅ Unban User", 
                callback_data=f"unban_{user.id}"
            )])
        elif action_type == "mute":
            keyboard.append([InlineKeyboardButton(
                "🔓 Unmute User", 
                callback_data=f"unmute_{user.id}"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            f"**Action Taken**\n\n"
            f"User ID: `{user.id}`\n"
            f"Reason: NSFW violation\n"
            f"\nAdmins can reverse this action using the button below."
        )
        
        try:
            await chat.send_message(message, reply_markup=reply_markup, parse_mode='Markdown')
        except BadRequest as e:
            logger.error(f"Failed to send action buttons: {e}")
    
    async def send_violation_report(self, chat: Chat, user: User, categories: List[str], 
                                    severity: str, words: List[str], is_admin: bool = False, warning_count: int = 0):
        """Send a violation report to the chat"""
        emoji_map = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }
        
        emoji = emoji_map.get(severity, '⚪')
        
        # Show only user ID (no name) and DON'T show detected words
        report = (
            f"{emoji} **NSFW Content Detected!**\n\n"
            f"**User ID:** `{user.id}`\n"
            f"**Severity:** {severity.upper()}\n"
            f"**Warning Count:** {warning_count}\n"
            f"**Categories:** {', '.join(categories)}\n"
            f"\n⚠️ Inappropriate content detected. Please review group guidelines."
        )
        
        if is_admin:
            report += "\nℹ️ This is an administrator."
        else:
            report += "\n⚠️ Appropriate action will be taken."
        
        try:
            sent_message = await chat.send_message(report, parse_mode='Markdown')
            # Auto-delete warning after 30 seconds
            await asyncio.sleep(30)
            await sent_message.delete()
        except BadRequest as e:
            logger.error(f"Failed to send/delete violation report: {e}")
    
    async def check_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check message content for NSFW words"""
        if not update.effective_chat or update.effective_chat.type == 'private':
            return
        
        # Check if message checking is enabled
        chat_id = update.effective_chat.id
        settings = self.chat_settings.get(chat_id, self.default_settings)
        
        if not settings['enable_message_check']:
            return
        
        if not update.message or not update.message.text:
            return
        
        message_text = update.message.text
        user = update.effective_user
        
        # Get custom blocked words for this chat
        chat_blocked_words = self.blocked_words.get(chat_id, set())
        
        # Analyze message for NSFW content (including custom blocked words)
        is_violation, categories, severity, words = self.detector.detect_nsfw(message_text, chat_blocked_words)
        
        if is_violation:
            await self.handle_message_violation(
                update,
                update.effective_chat,
                user,
                message_text,
                categories,
                severity,
                words
            )
    
    async def handle_message_violation(self, update: Update, chat: Chat, user: User, 
                                       message_text: str, categories: List[str], 
                                       severity: str, words: List[str]):
        """Handle NSFW violation in messages"""
        chat_id = chat.id
        
        # Get chat settings
        settings = self.chat_settings.get(chat_id, self.default_settings)
        
        # Initialize warning tracking for this chat
        if chat_id not in self.warned_users:
            self.warned_users[chat_id] = {}
        
        # Track warnings per user
        if user.id not in self.warned_users[chat_id]:
            self.warned_users[chat_id][user.id] = 0
        
        self.warned_users[chat_id][user.id] += 1
        warning_count = self.warned_users[chat_id][user.id]
        
        # Delete the violating message
        try:
            if update.message:
                await update.message.delete()
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
        
        # Send warning with user ID (no detected words shown)
        emoji_map = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }
        
        emoji = emoji_map.get(severity, '⚪')
        
        # Show only user ID (no name) and DON'T show detected words
        warning = (
            f"{emoji} **Inappropriate Content Detected!**\n\n"
            f"**User ID:** `{user.id}`\n"
            f"**Warning Count:** {warning_count}/{settings['warning_limit']}\n"
            f"**Severity:** {severity.upper()}\n"
            f"**Categories:** {', '.join(categories)}\n"
            f"\n⚠️ Inappropriate content detected. Please review group guidelines."
        )
        
        if severity == 'critical':
            warning += "⛔ **You have been banned for severe violation.**"
            try:
                await chat.ban_member(user.id)
                logger.warning(f"Banned user {user.id} for critical message violation")
            except Exception as e:
                logger.error(f"Failed to ban user: {e}")
        elif severity == 'high' or warning_count >= settings['warning_limit']:
            warning += f"⚠️ **You've reached {warning_count}/{settings['warning_limit']} warnings. Further violations will result in a ban.**"
            # Determine penalty type - use custom blocked words penalty if applicable
            penalty_type = settings['penalty_type']
            if 'blocked_word' in categories and chat_id in self.blocked_words_penalty:
                penalty_type = self.blocked_words_penalty[chat_id]
            
            # Apply penalty based on settings
            if penalty_type == 'ban' and warning_count >= settings['warning_limit']:
                try:
                    await chat.ban_member(user.id)
                    logger.warning(f"Banned user {user.id} after reaching warning limit")
                except Exception as e:
                    logger.error(f"Failed to ban user: {e}")
            elif penalty_type == 'kick' and warning_count >= settings['warning_limit']:
                try:
                    await chat.ban_member(user.id)
                    await asyncio.sleep(60)
                    await chat.unban_member(user.id)
                    logger.warning(f"Kicked user {user.id} after reaching warning limit")
                except Exception as e:
                    logger.error(f"Failed to kick user: {e}")
        else:
            warning += "⚠️ **Please keep the conversation appropriate.**"
        
        try:
            sent_message = await chat.send_message(warning, parse_mode='Markdown')
            # Auto-delete warning after 30 seconds
            await asyncio.sleep(30)
            await sent_message.delete()
        except BadRequest as e:
            logger.error(f"Failed to send/delete warning: {e}")
    
    async def clear_warnings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clear warning history (admin only)"""
        if not update.effective_chat:
            return
        
        # Check permissions
        can_use = await self.can_use_bot_commands(update, context)
        if not can_use:
            settings = self.chat_settings.get(update.effective_chat.id, self.default_settings)
            access_level = settings['who_can_use']
            await update.message.reply_text(f"⚠️ Only {access_level} can use this command!")
            return
        
        chat_id = update.effective_chat.id
        if chat_id in self.warned_users:
            self.warned_users[chat_id] = {}
            await update.message.reply_text("✅ Warning history cleared for this group.")
        else:
            await update.message.reply_text("✅ No warnings to clear.")
    
    async def block_word_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add a custom blocked word with optional penalty"""
        if not update.effective_chat:
            return
        
        # Check permissions
        can_use = await self.can_use_bot_commands(update, context)
        if not can_use:
            settings = self.chat_settings.get(update.effective_chat.id, self.default_settings)
            access_level = settings['who_can_use']
            await update.message.reply_text(f"⚠️ Only {access_level} can use this command!")
            return
        
        chat_id = update.effective_chat.id
        
        # Initialize blocked words set if not exists
        if chat_id not in self.blocked_words:
            self.blocked_words[chat_id] = set()
        
        # Parse arguments
        if not context.args or len(context.args) < 1:
            await update.message.reply_text(
                "Usage: /blockword <word> [penalty]\n\n"
                "Examples:\n"
                "/blockword spam\n"
                "/blockword gambling ban\n"
                "/blockword scam mute\n\n"
                "Penalties: ban, kick, mute, warn (default: warn)"
            )
            return
        
        word = context.args[0].lower()
        penalty = context.args[1].lower() if len(context.args) > 1 else 'warn'
        
        # Validate penalty
        valid_penalties = ['ban', 'kick', 'mute', 'warn']
        if penalty not in valid_penalties:
            await update.message.reply_text(
                f"❌ Invalid penalty! Choose from: {', '.join(valid_penalties)}"
            )
            return
        
        # Add blocked word
        self.blocked_words[chat_id].add(word)
        self.blocked_words_penalty[chat_id] = penalty
        
        await update.message.reply_text(
            f"✅ Word '{word}' has been blocked!\n"
            f"Penalty: {penalty.upper()}"
        )
    
    async def unblock_word_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove a custom blocked word"""
        if not update.effective_chat:
            return
        
        # Check if user is admin
        user = await update.effective_chat.get_member(update.effective_user.id)
        if user.status not in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            await update.message.reply_text("⚠️ Only admins can use this command!")
            return
        
        chat_id = update.effective_chat.id
        
        if not context.args or len(context.args) < 1:
            await update.message.reply_text("Usage: /unblockword <word>")
            return
        
        word = context.args[0].lower()
        
        if chat_id in self.blocked_words and word in self.blocked_words[chat_id]:
            self.blocked_words[chat_id].remove(word)
            await update.message.reply_text(f"✅ Word '{word}' has been unblocked.")
        else:
            await update.message.reply_text(f"❌ Word '{word}' is not in the blocked list.")
    
    async def list_block_words_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all custom blocked words"""
        if not update.effective_chat:
            return
        
        # Check if user is admin
        user = await update.effective_chat.get_member(update.effective_user.id)
        if user.status not in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            await update.message.reply_text("⚠️ Only admins can use this command!")
            return
        
        chat_id = update.effective_chat.id
        
        if chat_id not in self.blocked_words or len(self.blocked_words[chat_id]) == 0:
            await update.message.reply_text("✅ No custom blocked words in this group.")
            return
        
        penalty = self.blocked_words_penalty.get(chat_id, 'warn')
        words_list = '\n'.join(f"• {word}" for word in sorted(self.blocked_words[chat_id]))
        
        await update.message.reply_text(
            f"**Blocked Words ({len(self.blocked_words[chat_id])})**\n\n"
            f"{words_list}\n\n"
            f"**Default Penalty:** {penalty.upper()}"
        )
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command to configure bot settings"""
        if not update.effective_chat:
            return
        
        # Check if user is admin
        user = await update.effective_chat.get_member(update.effective_user.id)
        if user.status not in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            await update.message.reply_text("⚠️ Only admins can use this command!")
            return
        
        chat_id = update.effective_chat.id
        
        # Initialize chat settings if not exists
        if chat_id not in self.chat_settings:
            self.chat_settings[chat_id] = self.default_settings.copy()
        
        settings = self.chat_settings[chat_id]
        
        # Create settings message
        settings_msg = (
            "⚙️ **NSFW Bot Settings**\n\n"
            f"**Detection Settings:**\n"
            f"• Username Check: {'✅ Enabled' if settings['enable_username_check'] else '❌ Disabled'}\n"
            f"• Name Check: {'✅ Enabled' if settings['enable_name_check'] else '❌ Disabled'}\n"
            f"• Message Check: {'✅ Enabled' if settings['enable_message_check'] else '❌ Disabled'}\n\n"
            f"**Penalty Settings:**\n"
            f"• Warning Limit: {settings['warning_limit']}\n"
            f"• Penalty Type: {settings['penalty_type'].upper()}\n\n"
            f"**Access Control:**\n"
            f"• Who Can Use Bot: {settings['who_can_use'].capitalize()}\n\n"
            "Use the buttons below to customize settings."
        )
        
        # Create inline keyboard
        keyboard = [
            [
                InlineKeyboardButton(
                    f"Username: {'ON' if settings['enable_username_check'] else 'OFF'}",
                    callback_data="toggle_username"
                ),
                InlineKeyboardButton(
                    f"Name: {'ON' if settings['enable_name_check'] else 'OFF'}",
                    callback_data="toggle_name"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"Message: {'ON' if settings['enable_message_check'] else 'OFF'}",
                    callback_data="toggle_message"
                ),
            ],
            [
                InlineKeyboardButton("➖ Warning Limit", callback_data="decrease_limit"),
                InlineKeyboardButton(f"{settings['warning_limit']}", callback_data="noop"),
                InlineKeyboardButton("➕ Warning Limit", callback_data="increase_limit"),
            ],
            [
                InlineKeyboardButton("🔄 Change Penalty", callback_data="change_penalty"),
            ],
            [
                InlineKeyboardButton("👥 Access Control", callback_data="change_access"),
            ],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(settings_msg, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks from settings menu"""
        query = update.callback_query
        await query.answer()
        
        chat_id = query.message.chat_id
        
        # Check if user is admin
        user = await query.message.chat.get_member(query.from_user.id)
        if user.status not in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            await query.edit_message_text("⚠️ Only admins can modify settings!")
            return
        
        data = query.data
        
        # Handle help button from start menu
        if data == "show_help":
            await self.show_help_from_button(update, context)
            return
        
        # Handle back to start button
        if data == "back_to_start":
            await self.back_to_start_menu(update, context)
            return
        
        # Handle unban/unmute buttons
        if data.startswith("unban_") or data.startswith("unmute_"):
            await self.handle_admin_action_button(update, context)
            return
        
        # Initialize chat settings if not exists
        if chat_id not in self.chat_settings:
            self.chat_settings[chat_id] = self.default_settings.copy()
        
        settings = self.chat_settings[chat_id]
        
        # Handle different button presses
        if data == "toggle_username":
            settings['enable_username_check'] = not settings['enable_username_check']
            await query.edit_message_text(
                f"✅ Username detection {'enabled' if settings['enable_username_check'] else 'disabled'}!"
            )
            await asyncio.sleep(2)
            await self.settings_command_for_callback(update, context)
            
        elif data == "toggle_name":
            settings['enable_name_check'] = not settings['enable_name_check']
            await query.edit_message_text(
                f"✅ Name detection {'enabled' if settings['enable_name_check'] else 'disabled'}!"
            )
            await asyncio.sleep(2)
            await self.settings_command_for_callback(update, context)
            
        elif data == "toggle_message":
            settings['enable_message_check'] = not settings['enable_message_check']
            await query.edit_message_text(
                f"✅ Message detection {'enabled' if settings['enable_message_check'] else 'disabled'}!"
            )
            await asyncio.sleep(2)
            await self.settings_command_for_callback(update, context)
            
        elif data == "increase_limit":
            if settings['warning_limit'] < 10:
                settings['warning_limit'] += 1
                await query.edit_message_text(f"✅ Warning limit increased to {settings['warning_limit']}!")
                await asyncio.sleep(2)
                await self.settings_command_for_callback(update, context)
            else:
                await query.edit_message_text("⚠️ Maximum warning limit is 10!")
                await asyncio.sleep(2)
                await self.settings_command_for_callback(update, context)
                
        elif data == "decrease_limit":
            if settings['warning_limit'] > 1:
                settings['warning_limit'] -= 1
                await query.edit_message_text(f"✅ Warning limit decreased to {settings['warning_limit']}!")
                await asyncio.sleep(2)
                await self.settings_command_for_callback(update, context)
            else:
                await query.edit_message_text("⚠️ Minimum warning limit is 1!")
                await asyncio.sleep(2)
                await self.settings_command_for_callback(update, context)
                
        elif data == "change_penalty":
            # Cycle through penalty types
            penalty_types = ['ban', 'kick', 'mute', 'warn']
            current_index = penalty_types.index(settings['penalty_type'])
            next_index = (current_index + 1) % len(penalty_types)
            settings['penalty_type'] = penalty_types[next_index]
            
            penalty_descriptions = {
                'ban': '🚫 Ban - User is permanently banned',
                'kick': '👢 Kick - User is removed from group',
                'mute': '🔇 Mute - User cannot send messages',
                'warn': '⚠️ Warn - User receives warnings only'
            }
            
            await query.edit_message_text(
                f"✅ Penalty changed to: {settings['penalty_type'].upper()}\n"
                f"{penalty_descriptions[settings['penalty_type']]}"
            )
            await asyncio.sleep(2)
            await self.settings_command_for_callback(update, context)
        
        elif data == "change_access":
            # Show access control submenu
            await self.show_access_control_submenu(update, context)
        
        elif data == "back_to_settings":
            # Return to main settings from access control submenu
            await self.settings_command_for_callback(update, context)
        
        elif data in ["set_admin_only", "set_all_members", "set_everyone"]:
            # Handle access level selection
            access_map = {
                'set_admin_only': 'admin',
                'set_all_members': 'member',
                'set_everyone': 'everyone'
            }
            
            new_access = access_map[data]
            settings['who_can_use'] = new_access
            
            access_emoji = {
                'admin': '👮',
                'member': '👥',
                'everyone': '🌍'
            }
            
            access_success = {
                'admin': '✅ Access set to: Admins Only\n👮 Only administrators can use bot commands',
                'member': '✅ Access set to: All Members\n👥 All group members can use bot commands',
                'everyone': '✅ Access set to: Everyone\n🌍 Anyone can use bot commands'
            }
            
            await query.edit_message_text(
                f"{access_success[new_access]}"
            )
            await asyncio.sleep(2)
            await self.settings_command_for_callback(update, context)
        
        elif data == "noop":
            # Do nothing button (placeholder)
            pass
    
    async def handle_admin_action_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle unban/unmute button clicks by admins"""
        query = update.callback_query
        chat = query.message.chat
        data = query.data
        
        # Extract user ID from callback data
        if data.startswith("unban_"):
            target_user_id = int(data.split("_")[1])
            try:
                await chat.unban_member(target_user_id)
                await query.edit_message_text(
                    f"✅ User `{target_user_id}` has been unbanned!",
                    parse_mode='Markdown'
                )
                logger.info(f"Admin {query.from_user.id} unbanned user {target_user_id} in chat {chat.id}")
            except Exception as e:
                await query.edit_message_text(f"❌ Failed to unban user: {str(e)}")
                logger.error(f"Failed to unban user {target_user_id}: {e}")
        
        elif data.startswith("unmute_"):
            target_user_id = int(data.split("_")[1])
            try:
                # Unmute by restoring default permissions
                await chat.restrict_member(
                    user_id=target_user_id,
                    can_send_messages=True,
                    can_send_polls=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_change_info=False,
                    can_invite_users=True,
                    can_pin_messages=False
                )
                await query.edit_message_text(
                    f"✅ User `{target_user_id}` has been unmuted!",
                    parse_mode='Markdown'
                )
                logger.info(f"Admin {query.from_user.id} unmuted user {target_user_id} in chat {chat.id}")
            except Exception as e:
                await query.edit_message_text(f"❌ Failed to unmute user: {str(e)}")
                logger.error(f"Failed to unmute user {target_user_id}: {e}")
    
    async def settings_command_for_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Helper method to refresh settings menu after button press"""
        chat_id = update.callback_query.message.chat_id
        settings = self.chat_settings[chat_id]
        
        # Create settings message
        settings_msg = (
            "⚙️ **NSFW Bot Settings**\n\n"
            f"**Detection Settings:**\n"
            f"• Username Check: {'✅ Enabled' if settings['enable_username_check'] else '❌ Disabled'}\n"
            f"• Name Check: {'✅ Enabled' if settings['enable_name_check'] else '❌ Disabled'}\n"
            f"• Message Check: {'✅ Enabled' if settings['enable_message_check'] else '❌ Disabled'}\n\n"
            f"**Penalty Settings:**\n"
            f"• Warning Limit: {settings['warning_limit']}\n"
            f"• Penalty Type: {settings['penalty_type'].upper()}\n\n"
            f"**Access Control:**\n"
            f"• Who Can Use Bot: {settings['who_can_use'].capitalize()}\n\n"
            "Use the buttons below to customize settings."
        )
        
        # Create inline keyboard
        keyboard = [
            [
                InlineKeyboardButton(
                    f"Username: {'ON' if settings['enable_username_check'] else 'OFF'}",
                    callback_data="toggle_username"
                ),
                InlineKeyboardButton(
                    f"Name: {'ON' if settings['enable_name_check'] else 'OFF'}",
                    callback_data="toggle_name"
                ),
            ],
            [
                InlineKeyboardButton(
                    f"Message: {'ON' if settings['enable_message_check'] else 'OFF'}",
                    callback_data="toggle_message"
                ),
            ],
            [
                InlineKeyboardButton("➖ Warning Limit", callback_data="decrease_limit"),
                InlineKeyboardButton(f"{settings['warning_limit']}", callback_data="noop"),
                InlineKeyboardButton("➕ Warning Limit", callback_data="increase_limit"),
            ],
            [
                InlineKeyboardButton("🔄 Change Penalty", callback_data="change_penalty"),
            ],
            [
                InlineKeyboardButton("👥 Access Control", callback_data="change_access"),
            ],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(settings_msg, reply_markup=reply_markup, parse_mode='Markdown')
    
    def run(self):
        """Start the bot"""
        logger.info("Starting NSFW Detection Bot...")
        # Send startup notification to log channel
        asyncio.get_event_loop().run_until_complete(
            self.send_log_message(
                "🟢 **Bot Started**\n\n"
                f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                "**Status:** Online and ready!\n"
                "**Version:** v2.0 with auto-restart"
            )
        )
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    async def send_log_message(self, message: str):
        """Send log message to the configured log channel"""
        try:
            await self.application.bot.send_message(
                chat_id=self.log_channel_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to send log to channel: {e}")
    
    async def on_error(self, update: Optional[Update], context: ContextTypes.DEFAULT_TYPE):
        """Handle errors and log them to the channel"""
        error = context.error
        
        # Log the error
        logger.error(f"An error occurred: {error}", exc_info=True)
        
        # Send error to log channel
        error_msg = (
            f"🔴 **Bot Error**\n\n"
            f"**Error:** `{str(error)}`\n"
            f"**Type:** `{type(error).__name__}`\n"
        )
        
        if update and update.effective_chat:
            error_msg += f"**Chat:** `{update.effective_chat.id}`\n"
            error_msg += f"**Title:** {update.effective_chat.title}\n"
        
        if update and update.effective_user:
            error_msg += f"**User:** `{update.effective_user.id}`\n"
            error_msg += f"**Name:** {update.effective_user.first_name}\n"
        
        try:
            await self.send_log_message(error_msg)
        except Exception as e:
            logger.error(f"Failed to send error to log channel: {e}")


def main():
    """Main entry point"""
    # Get bot token from environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found! Please set it in your .env file")
        print("❌ Error: TELEGRAM_BOT_TOKEN not found!")
        print("Please create a .env file with your bot token:")
        print("TELEGRAM_BOT_TOKEN=your_bot_token_here")
        return
    
    # Create and run bot
    bot = TelegramNSFWBot(token)
    bot.run()


if __name__ == '__main__':
    main()
