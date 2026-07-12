from telegram import (
    Update,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from telegram.constants import ParseMode
from assets.texts import (
    cancel_markup,
    main_menu,
    friend_added_text,
    cancel_text,
    list_of_friends_text,
)
from database import (
    get_user,
    add_friend_to_db,
    get_friends_from_db,
    remove_friend_from_db,
)
import asyncio

# Conversation state label integers
FULLNAME, NICKNAME, BIRTHDAY, PHONE, LOCATION = range(5)
CHOOSE_DELETION = 11

# Safe Regex Rules and State Filters
cancel_regex = r"^(❌\s*Cancel|Cancel|cancel|CANCEL)$"
state_filter = (
    filters.TEXT
    & ~filters.COMMAND
    & filters.Regex(f"^(?!❌\s*Cancel$|Cancel$|cancel$|CANCEL$).*$")
)

# ======================== ADD FRIEND CODE ========================

async def add_friend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not get_user(update.effective_user.id):
        await update.message.reply_text(
            "You are not registered yet! Tap /start to register."
        )
        return
    await update.message.reply_text(
        "So you wanna add a friend? Okay! What's the fullname of your friend?",
        reply_markup=cancel_markup,
    )
    return FULLNAME

async def get_fullname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fullname"] = update.message.text
    await update.message.reply_text(
        "Nickname of your friend?", reply_markup=cancel_markup
    )
    return NICKNAME

async def get_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["nickname"] = update.message.text
    await update.message.reply_text(
        "Birthday of your friend? (Insert in this format 'DD MM YYYY')",
        reply_markup=cancel_markup,
    )
    return BIRTHDAY

async def get_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["birthday"] = update.message.text
    await update.message.reply_text(
        "Awesome! I'll remind you 3 days before their birthday. What's their phone number?",
        reply_markup=ReplyKeyboardMarkup(
            [["I don't have it"], ["❌ Cancel"]],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone_input = update.message.text
    if phone_input.strip().lower() == "i don't have it":
        phone_input = "Not Available"
    context.user_data["phone"] = phone_input
    await update.message.reply_text(
        "And where do they live?", reply_markup=cancel_markup
    )
    return LOCATION

async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.text
    chat_id = update.effective_chat.id

    fullname = context.user_data.get("fullname")
    nickname = context.user_data.get("nickname")
    birthday = context.user_data.get("birthday")
    phone = context.user_data.get("phone")

    add_friend_to_db(chat_id, fullname, nickname, birthday, phone, location)

    formatted_birthday = birthday.replace(" ", "-") if birthday else "N/A"
    await update.message.reply_text(
        friend_added_text.format(
            fullname=fullname,
            nickname=nickname,
            birthday=formatted_birthday,
            phone=phone,
            location=location,
        ),
        reply_markup=main_menu,
    )
    context.user_data.clear()  
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(cancel_text, reply_markup=main_menu)
    return ConversationHandler.END

add_friend_handler = ConversationHandler(
    entry_points=[
        CommandHandler("add", add_friend),
        MessageHandler(filters.Regex("^(Add|add)$"), add_friend),
    ],
    states={
        FULLNAME: [MessageHandler(state_filter, get_fullname)],
        NICKNAME: [MessageHandler(state_filter, get_nickname)],
        BIRTHDAY: [MessageHandler(state_filter, get_birthday)],
        PHONE: [MessageHandler(state_filter, get_phone)],
        LOCATION: [MessageHandler(state_filter, get_location)],
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
        MessageHandler(filters.Regex(cancel_regex), cancel),
    ],
)

# ======================== LIST FRIENDS CODE ========================

async def list_of_friends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    friends = get_friends_from_db(chat_id)
    if not friends:
        await update.message.reply_text(
            "You have no friends yet!", reply_markup=main_menu
        )
        return
    list_of_data = ""
    text = "Here are the friends you've added:\n\n"
    for friend in friends:
        list_of_data += list_of_friends_text.format(
            fullname=friend["fullname"],
            nickname=friend["nickname"],
            birthday=friend["birthday"],
            phone=friend["phone"],
            location=friend["location"],
        )
    await update.message.reply_text(text + list_of_data, reply_markup=main_menu)

# ======================== REMOVE FRIEND CODE ========================

async def select_friend_to_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    friends = get_friends_from_db(chat_id)

    if not friends or friends == "Nothing yet!":
        await update.message.reply_text(
            "Your circle is empty! Add a friend first.", reply_markup=main_menu
        )
        return ConversationHandler.END

    inline_keyboard = []
    for friend in friends:
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=friend["fullname"],
                    callback_data=f"remove_{friend['fullname']}",  
                )
            ]
        )
    inline_keyboard.append(
        [InlineKeyboardButton(text="❌ Cancel Process", callback_data="del_cancel")]
    )

    await update.message.reply_text(
        "Sorry to hear that, who do you want to remove?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard),
    )
    return CHOOSE_DELETION  

async def remove_friend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  
    data = query.data
    chat_id = update.effective_chat.id

    if data == "del_cancel":
        await query.message.edit_text("Okay, process canceled.", reply_markup=None)
        await asyncio.sleep(1)  
        await query.message.reply_text(
            "What would you like to do next?", reply_markup=main_menu
        )
        return ConversationHandler.END

    fullname_to_remove = data.replace("remove_", "")
    success = remove_friend_from_db(chat_id, fullname_to_remove)

    if success:
        await query.message.edit_text(
            f"You removed <b>{fullname_to_remove}</b>!",  
            parse_mode=ParseMode.HTML,  
            reply_markup=None,
        )
    else:
        await query.message.edit_text(
            f"You tried to remove <b>{fullname_to_remove}</b>, but they weren't found!",
            parse_mode=ParseMode.HTML,
            reply_markup=None,
        )

    await context.bot.send_message(
        chat_id=chat_id, text="What would you like to do next?", reply_markup=main_menu
    )
    return ConversationHandler.END  

remove_friend_handler = ConversationHandler(
    entry_points=[
        CommandHandler("remove", select_friend_to_remove),
        MessageHandler(filters.Regex("^(Remove|remove)$"), select_friend_to_remove),
    ],
    states={
        CHOOSE_DELETION: [CallbackQueryHandler(remove_friend)]  
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
        MessageHandler(filters.Regex(cancel_regex), cancel),
    ],
)