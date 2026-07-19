from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from friends_handler import (
    list_of_friends,
    add_friend_handler,
    remove_friend_handler,
    edit_friend_handler
)
from database import create_user, get_user, create_tables
from assets.texts_fa import items as text_fa
from language_handler import (
    send_language_picker,
    handle_language_selection,
    load_assets,
)
from list_handler import handle_list_actions
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

application = Application.builder().token(TOKEN).build()
create_tables()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    # CASE 1: User already exists
    if get_user(user.id):
        text, keyboard = load_assets(user.id)
        await update.message.reply_text(
            text["start_already_registered_text"].format(first_name=user.first_name),
            reply_markup=keyboard["main_menu"], # FIX: Kept dynamic markup
        )
        return
        
    # CASE 2: New User signup
    create_user(user.id, user.first_name, user.username)
    await update.message.reply_text(
        text_fa["start_command_text"].format(first_name=user.first_name)
    )
    await send_language_picker(update, context)
    return


add_friend_handler.fallbacks.extend(
    [
        CommandHandler("start", start),
        CommandHandler("list", list_of_friends),
        # FIX: Handle Persian list word filter in fallback rules
        filters.Regex("(?i)^(list|لیست افراد)$")
    ]
)

print("BOT IS RUNNING")
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_list_actions, pattern="^(view_)"))
application.add_handler(CallbackQueryHandler(handle_language_selection, pattern="^setlang_"))
application.add_handler(add_friend_handler)
application.add_handler(CommandHandler("list", list_of_friends))
application.add_handler(
    MessageHandler(filters.Regex("(?i)^(list|list of friends|لیست افراد)$"), list_of_friends)
)
application.add_handler(CommandHandler("settings", send_language_picker))
application.add_handler(remove_friend_handler)
application.add_handler(edit_friend_handler)
application.run_polling()