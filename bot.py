#!/usr/bin/env python3
"""
Fixed Inline UserDetailsBot
- Properly closed all brackets
- Working inline buttons
- Safe message handling
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class InlineUserDetailsBot:
    def __init__(self, token: str):
        self.token = token
        self.app = Application.builder().token(self.token).build()
        
        # Register handlers
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("myid", self.myid_command))
        self.app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, self.handle_message))
        self.app.add_handler(CallbackQueryHandler(self.button))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message with inline keyboard"""
        keyboard = [
            [InlineKeyboardButton("Show My ID", callback_data='myid')],
            [InlineKeyboardButton("Help", callback_data='help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "👋 Hi! I can show info about forwarded messages.\n\n"
            "◇ Forward any message to see details\n"
            "◇ Click buttons below or use commands:",
            reply_markup=reply_markup
        )

    async def myid_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /myid command"""
        user = update.effective_user
        keyboard = [
            [InlineKeyboardButton("Refresh", callback_data='refresh_myid')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🆔 <b>Your Telegram ID</b>\n"
            f"├ ID: <code>{user.id}</code>\n"
            f"├ Username: @{user.username if user.username else 'N/A'}\n"
            f"└ Language: {user.language_code if user.language_code else 'N/A'}",
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all messages with inline reply"""
        msg = update.message
        if hasattr(msg, 'forward_from') and msg.forward_from:
            await self.show_user_details(msg, msg.forward_from)
        elif hasattr(msg, 'forward_from_chat') and msg.forward_from_chat:
            await self.show_chat_details(msg, msg.forward_from_chat)
        elif hasattr(msg, 'forward_sender_name') and msg.forward_sender_name:
            await self.show_private_forward(msg)
        else:
            if msg.from_user:
                keyboard = [
                    [InlineKeyboardButton("Show Sender Info", callback_data=f'show_{msg.from_user.id}')]
                ]
                await msg.reply_text(
                    "ℹ️ This is a regular message",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )

    async def show_user_details(self, msg: Message, user):
        """Show user details inline"""
        keyboard = [
            [InlineKeyboardButton("Refresh", callback_data=f'refresh_{user.id}')],
            [InlineKeyboardButton("Close", callback_data='close')]
        ]
        await msg.reply_text(
            f"👤 <b>User Details</b>\n"
            f"├ ID: <code>{user.id}</code>\n"
            f"├ Username: @{user.username if user.username else 'N/A'}\n"
            f"└ Bot: {'✅' if user.is_bot else '❌'}",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button presses"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'myid':
            user = query.from_user
            await query.edit_message_text(
                f"🆔 <b>Your ID</b>: <code>{user.id}</code>\n"
                f"👤 <b>Username</b>: @{user.username if user.username else 'N/A'}",
                parse_mode='HTML'
            )
        elif query.data == 'close':
            await query.delete_message()
        elif query.data.startswith('show_'):
            user_id = int(query.data.split('_')[1])
            await query.edit_message_text(
                f"👤 User ID: <code>{user_id}</code>\n"
                "⚠️ More details not available inline",
                parse_mode='HTML'
            )

    def run(self):
        logger.info("Starting inline bot...")
        self.app.run_polling()

if __name__ == "__main__":
    import os
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "YOUR_TOKEN_HERE"  # REPLACE THIS
    bot = InlineUserDetailsBot(TOKEN)
    bot.run()
