from database import link_chat_id_to_code
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import ContextTypes


async def check_for_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()
    chat_id = update.message.chat_id

    success = link_chat_id_to_code(code, chat_id)

    if success:
        keyboard = [[InlineKeyboardButton("🔙 Return to Socircle Web", url="https://socircle.samousavi.online")], [InlineKeyboardButton("📱 Open Mini App", web_app=WebAppInfo(url="https://socircle.samousavi.online"))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "✅ Verification successful!\n\n"
            "Your browser is now securely linked to your Telegram account. "
            "You can return to the website tab now.", reply_markup=reply_markup
        )

    else:
        await update.message.reply_text("❌ Invalid or expired code.\n\n"
            "Please go back to the website, refresh the page, and click the Telegram logo to generate a new 4-digit code.")
 