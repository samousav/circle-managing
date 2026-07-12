from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters
)
from friends_functions import add_friend_handler, list_of_friends, remove_friend_handler
from database import create_user, get_user, create_tables
from assets.texts import start_command_text, main_menu
from dotenv import load_dotenv
import os
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

application = Application.builder().token(TOKEN).build()
create_tables()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if get_user(user.id):
        await update.message.reply_text(f"You are already registered {user.first_name}!", reply_markup=main_menu)
        return
    create_user(user.id, user.first_name, user.username)
    await update.message.reply_text(start_command_text.format(first_name=user.first_name))


add_friend_handler.fallbacks.extend([
    CommandHandler("start", start),
    CommandHandler("list", list_of_friends),
    MessageHandler(filters.Regex("(?i)^list$"), list_of_friends)
])

print("BOT IS RUNNING")
application.add_handler(CommandHandler("start", start))
application.add_handler(add_friend_handler)
application.add_handler(CommandHandler("list", list_of_friends))    
application.add_handler(MessageHandler(filters.Regex("(?i)^(list|list of friends)$"), list_of_friends))
application.add_handler(remove_friend_handler)
application.run_polling()