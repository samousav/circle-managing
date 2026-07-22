from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from handlers.friends_handler import (
    list_of_friends,
    add_friend_handler,
    remove_friend_handler,
    edit_friend_handler,
)
from database import create_user, get_user, create_tables
from assets.texts_fa import items as text_fa
from handlers.language_handler import (
    send_language_picker,
    handle_language_selection,
    load_assets,
)
from handlers.reminder_handler import birthday_reminder
from handlers.list_handler import handle_list_actions
from admin_functions import (
    get_all_users_handler,
    WAITING_FOR_BROADCAST_CONTENT,
    start_broadcast,
    send_content_to_all,
    cancel_broadcast,
    broadcast_handler,
)
from dotenv import load_dotenv
import datetime
import zoneinfo
import os

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

application = Application.builder().token(TOKEN).build()
create_tables()

tehran_tz = zoneinfo.ZoneInfo("Asia/Tehran")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if get_user(user.id):
        text, keyboard = load_assets(user.id)
        await update.message.reply_text(
            text["start_already_registered_text"].format(first_name=user.first_name),
            reply_markup=keyboard["main_menu"],  # FIX: Kept dynamic markup
        )
        return

    create_user(user.id, user.first_name, user.username)
    await update.message.reply_text(
        text_fa["start_command_text"].format(first_name=user.first_name)
    )
    await send_language_picker(update, context)
    return


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, keyboard = load_assets(update.message.from_user.id)
    await update.message.reply_text(
        text["help_text"], reply_markup=keyboard["main_menu"]
    )
    return


add_friend_handler.fallbacks.extend(
    [
        CommandHandler("start", start),
        CommandHandler("list", list_of_friends),
        filters.Regex("(?i)^(list|لیست افراد)$"),
    ]
)

if application.job_queue:
    application.job_queue.run_daily(
        birthday_reminder,
        time=datetime.time(hour=0, minute=0, second=0, tzinfo=tehran_tz),
    )


# 🌟 Add it at the top of your handlers stack!
application.add_handler(broadcast_handler)
application.add_handler(CommandHandler("all_users", get_all_users_handler))
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help))
application.add_handler(CallbackQueryHandler(handle_list_actions, pattern="^(view_)"))
application.add_handler(
    CallbackQueryHandler(handle_language_selection, pattern="^setlang_")
)
application.add_handler(add_friend_handler)
application.add_handler(CommandHandler("list", list_of_friends))
application.add_handler(
    MessageHandler(
        filters.Regex("(?i)^(list|list of friends|لیست افراد)$"), list_of_friends
    )
)
application.add_handler(CommandHandler("settings", send_language_picker))
application.add_handler(remove_friend_handler)
application.add_handler(edit_friend_handler)
print("BOT IS RUNNING")
if __name__ == "__main__":
    application.run_polling()
