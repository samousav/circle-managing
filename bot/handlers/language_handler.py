from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import set_user_language, get_user_language
import bot.assets.keyboards_en as keyboards_en
import bot.assets.keyboards_fa as keyboards_fa
import bot.assets.texts_en as texts_en
import bot.assets.texts_fa as texts_fa


def load_assets(chat_id):
    user_lang = get_user_language(chat_id)
    
    if user_lang == "fa":
        return texts_fa.items, keyboards_fa.items
    return texts_en.items, keyboards_en.items

def get_language_keyboard():
    """Generates the inline keyboard for choosing a language."""
    keyboard = [[
        InlineKeyboardButton(text="🇺🇸 English", callback_data="setlang_en"),
        InlineKeyboardButton(text="🇮🇷 فارسی", callback_data="setlang_fa")
    ]]
    return InlineKeyboardMarkup(keyboard)


async def send_language_picker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message if update.message else update.callback_query.message
    await message.reply_text(
        "لطفا زبان مورد نظر خود را انتخاب کنید:\n\nPlease select your preferred language:", 
        reply_markup=get_language_keyboard()
    )



async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id
    chosen_language = query.data.replace("setlang_", "")
    set_user_language(chat_id, chosen_language)
    await query.message.edit_reply_markup(reply_markup=None)