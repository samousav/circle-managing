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
import bot.assets.texts_en as texts_en
import bot.assets.texts_fa as texts_fa
import bot.assets.keyboards_en as keyboards_en
import bot.assets.keyboards_fa as keyboards_fa

from database import (
    get_user,
    add_friend_to_db,
    get_friends_from_db,
    remove_friend_from_db,
    get_user_language,
    update_friend_info,
)
from bot.assets.date_picker import (
    jalali_year_grid,
    jalali_month_grid,
    jalali_day_grid,
    gregorian_year_grid,
    gregorian_month_grid,
    gregorian_day_grid,
    format_birthday_for_user
)
from bot.handlers.language_handler import load_assets
from khayyam import JalaliDate
import asyncio

# Conversation state label integers
FULLNAME, NICKNAME, BIRTHDAY, PHONE, LOCATION = range(5)
CHOOSE_DELETION = 11

# Safe Regex Rules and State Filters
cancel_regex = r"^(❌\s*Cancel|Cancel|cancel|CANCEL|❌\s*لغو|لغو)$"
state_filter = (
    filters.TEXT
    & ~filters.COMMAND
    & filters.Regex(f"^(?!❌\s*Cancel$|Cancel$|cancel$|CANCEL$|❌\s*لغو$|لغو$).*$")
)


# ======================== ADD FRIEND CODE ========================


async def add_friend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, keyboard = load_assets(update.effective_user.id)
    if not get_user(update.effective_user.id):
        return

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            text["get_fullname_text"],
            reply_markup=keyboard["cancel_markup"],
        )
    else:
        await update.message.reply_text(
            text["get_fullname_text"],
            reply_markup=keyboard["cancel_markup"],
        )
    return FULLNAME


async def get_fullname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, keyboard = load_assets(update.effective_user.id)
    context.user_data["fullname"] = update.message.text
    await update.message.reply_text(
        text["ask_nickname"], reply_markup=keyboard["cancel_markup"]
    )
    return NICKNAME


async def get_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, keyboard = load_assets(update.effective_user.id)
    context.user_data["nickname"] = update.message.text
    user_lang = get_user_language(update.effective_chat.id)
    if user_lang == "fa":
        prompt_text = "سال تولدش رو انتخاب کن\nYYYY-MM-DD"
        markup = jalali_year_grid()

    else:
        prompt_text = "Select birth year\nYYYY-MM-DD"
        markup = gregorian_year_grid()
    await update.message.reply_text(
        prompt_text,
        reply_markup=markup,
    )
    return BIRTHDAY


async def process_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = update.effective_chat.id
    text, keyboard = load_assets(chat_id)
    user_lang = get_user_language(chat_id)

    if data == "DATE-IGNORE":
        return BIRTHDAY
    
    if data.startswith("DATE-YRPAGE-"):
        _, _, lang_code, new_start_year = data.split("-")
        new_start_year = int(new_start_year)

        if lang_code == "FA":
            markup = jalali_year_grid(start_year=new_start_year)
            prompt_text = "سال تولدش رو انتخاب کن\nYYYY-MM-DD"
        else:
            markup = gregorian_year_grid(start_year=new_start_year)
            prompt_text = "Select birth year\nYYYY-MM-DD"

        await query.message.edit_text(prompt_text, reply_markup=markup)
        return BIRTHDAY

    # ----- year selected -----
    if data.startswith("DATE-YR-"):
        year = data.split("-")[2]
        context.user_data["temp_year"] = year

        if user_lang == "fa":
            prompt_text = f"ماه تولدش رو انتخاب کن\n{year} - MM - DD"
            markup = jalali_month_grid(int(year))

        else:
            prompt_text = f"Select month\n{year}-MM-DD"
            markup = gregorian_month_grid(int(year))

        await query.message.edit_text(prompt_text, reply_markup=markup)
        return BIRTHDAY

    # ----- month selected -----
    elif data.startswith("DATE-MO-"):
        _, _, year, month = data.split("-")
        context.user_data["temp_month"] = month
        if user_lang == "fa":
            fa_months = text["months"]
            m_name = fa_months[int(month) - 1]
            prompt_text = f"روز تولدش رو انتخاب کن\n{year} - {m_name} - DD"
            markup = jalali_day_grid(int(year), int(month))

        else:
            eng_months = text["months"]
            m_name = eng_months[int(month) - 1]
            prompt_text = f"Select day\n{year}-{month}-DD"
            markup = gregorian_day_grid(int(year), int(month))

        await query.message.edit_text(prompt_text, reply_markup=markup)
        return BIRTHDAY

    # ----- day selected -> standardize and save to DB -----
    elif data.startswith("DATE-DY-"):
        _, _, year, month, day = data.split("-")

        if user_lang == "fa":
            jalali_input = JalaliDate(int(year), int(month), int(day))
            gregorian_date = jalali_input.todate()
            formatted_db_date = gregorian_date.strftime("%Y-%m-%d")
            display_text = f"{day} {jalali_input.monthname()} {year} انتخاب شد!"

        else:
            formatted_db_date = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"
            display_text = f"Selected {formatted_db_date}!"
        context.user_data["birthday"] = formatted_db_date
        await query.message.edit_text(display_text, reply_markup=None)
        await query.message.reply_text(
            text["ask_phone"], reply_markup=keyboard["phone_markup"]
        )
        context.user_data.pop("temp_year", None)
        context.user_data.pop("temp_month", None)

        return PHONE


async def get_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, keyboard = load_assets(update.effective_user.id)
    context.user_data["birthday"] = update.message.text
    await update.message.reply_text(
        text["ask_phone"],
        reply_markup=keyboard["phone_markup"],
    )
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, keyboard = load_assets(update.effective_user.id)
    phone_input = update.message.text
    if phone_input.strip().lower() == "i don't have it":
        phone_input = "Not Available"
    context.user_data["phone"] = phone_input
    await update.message.reply_text(
        text["ask_location"], reply_markup=keyboard["cancel_markup"]
    )
    return LOCATION


async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, keyboard = load_assets(update.effective_user.id)
    location = update.message.text
    chat_id = update.effective_chat.id

    fullname = context.user_data.get("fullname")
    nickname = context.user_data.get("nickname")
    birthday = context.user_data.get("birthday")
    phone = context.user_data.get("phone")

    add_friend_to_db(chat_id, fullname, nickname, birthday, phone, location)
    formatted_birthday = birthday.replace(" ", "-") if birthday else "N/A"

    await update.message.reply_text(
        text["friend_added_text"].format(
            fullname=fullname,
            nickname=nickname,
            birthday=formatted_birthday,
            phone=phone,
            location=location,
        ),
        reply_markup=keyboard["main_menu"],
    )
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, keyboard = load_assets(update.effective_user.id)
    context.user_data.clear()
    await update.message.reply_text(
        text["cancel_text"], reply_markup=keyboard["main_menu"]
    )
    return ConversationHandler.END


add_friend_handler = ConversationHandler(
    entry_points=[
        CommandHandler("add", add_friend),
        MessageHandler(filters.Regex("^(Add|add|اضافه کردن)$"), add_friend),
        CallbackQueryHandler(add_friend, pattern="^inline_add$"),
    ],
    states={
        FULLNAME: [MessageHandler(state_filter, get_fullname)],
        NICKNAME: [MessageHandler(state_filter, get_nickname)],
        BIRTHDAY: [CallbackQueryHandler(process_calendar, pattern="^DATE-")],
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
    text, keyboard = load_assets(update.effective_user.id)
    chat_id = update.effective_chat.id
    friends = get_friends_from_db(chat_id)

    if not friends:
        await update.message.reply_text(
            text["no_friends_yet"], reply_markup=keyboard["main_menu"]
        )
        return

    user_lang = get_user_language(chat_id)
    list_of_data = ""
    first_friend_name = friends[0]["fullname"] if friends else "target"
    for friend in friends:
        fullname = friend["fullname"]
        display_birthday = format_birthday_for_user(friend["birthday"], user_lang)
        list_of_data += text["list_item_format"].format(
            fullname=fullname,
            nickname=friend["nickname"],
            birthday=display_birthday,
            phone=friend["phone"],
            location=friend["location"],
        )

    await update.message.reply_text(
        text["list_header"] + list_of_data,
        reply_markup=keyboard["friend_action_keyboard"](first_friend_name),
    )


# ======================== REMOVE FRIEND CODE ========================


async def select_friend_to_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text, keyboard = load_assets(chat_id)
    friends = get_friends_from_db(chat_id)

    # 1. Check if the circle is empty
    if not friends:
        msg = text["empty_circle"]
        # 🚦 Traffic Cop: Did they click a button or type text?
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.message.reply_text(
                msg, reply_markup=keyboard["main_menu"]
            )
        else:
            await update.message.reply_text(msg, reply_markup=keyboard["main_menu"])
        return ConversationHandler.END

    # 2. Build the inline keyboard list of friends
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

    from database import get_user_language

    user_lang = get_user_language(chat_id)
    cancel_label = "❌ Cancel Process" if user_lang == "en" else "❌ لغو عملیات"
    inline_keyboard.append(
        [InlineKeyboardButton(text=cancel_label, callback_data="del_cancel")]
    )

    # 3. Send the menu safely
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        # Clean up the old list buttons so they don't look clickable anymore
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.reply_text(
            text["who_to_remove"],
            reply_markup=InlineKeyboardMarkup(inline_keyboard),
        )
    else:
        await update.message.reply_text(
            text["who_to_remove"],
            reply_markup=InlineKeyboardMarkup(inline_keyboard),
        )

    return CHOOSE_DELETION


async def remove_friend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, keyboard = load_assets(update.effective_user.id)
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = update.effective_chat.id

    if data == "del_cancel":
        await query.message.edit_text(text["cancel_process"], reply_markup=None)
        await asyncio.sleep(1)
        await query.message.reply_text(
            text["next_action"], reply_markup=keyboard["main_menu"]
        )
        return ConversationHandler.END

    fullname_to_remove = data.replace("remove_", "")
    success = remove_friend_from_db(chat_id, fullname_to_remove)

    if success:
        await query.message.edit_text(
            text["remove_success"].format(fullname=fullname_to_remove),
            parse_mode=ParseMode.HTML,
            reply_markup=None,
        )
    else:
        await query.message.edit_text(
            text["remove_fail"].format(fullname=fullname_to_remove),
            parse_mode=ParseMode.HTML,
            reply_markup=None,
        )

    await context.bot.send_message(
        chat_id=chat_id, text=text["next_action"], reply_markup=keyboard["main_menu"]
    )
    return ConversationHandler.END


remove_friend_handler = ConversationHandler(
    entry_points=[
        CommandHandler("remove", select_friend_to_remove),
        MessageHandler(filters.Regex("^(Remove|remove|حذف)$"), select_friend_to_remove),
        CallbackQueryHandler(select_friend_to_remove, pattern="^remove_target_"),
    ],
    states={CHOOSE_DELETION: [CallbackQueryHandler(remove_friend)]},
    fallbacks=[
        CommandHandler("cancel", cancel),
        MessageHandler(filters.Regex(cancel_regex), cancel),
    ],
)


# ======================== EDIT FRIEND CODE ========================

ASK_FIELD, ASK_INPUT, SAVE_INPUT = range(20, 23)


async def edit_friend_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text, keyboard = load_assets(chat_id)
    friends = get_friends_from_db(chat_id)
    if not friends:
        txt = text["no_friends_yet"]
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.message.reply_text(txt, reply_markup=None)
        else:
            await update.message.reply_text(txt, reply_markup=None)
        return ConversationHandler.END

    inline_keyboard = []

    def keyboard_function():
        for friend in friends:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=friend["fullname"],
                        callback_data=f"edit_target_{friend['fullname']}",
                    )
                ]
            )
        inline_keyboard.append(
            [InlineKeyboardButton(text="Cancel", callback_data="edit_cancel")]
        )

    if update.callback_query:
        await update.callback_query.answer()
        keyboard_function()
        await update.callback_query.message.reply_text(
            text["response_to_edit"], reply_markup=InlineKeyboardMarkup(inline_keyboard)
        )
    else:
        keyboard_function()
        await update.message.reply_text(
            text["response_to_edit"], reply_markup=InlineKeyboardMarkup(inline_keyboard)
        )
    return ASK_FIELD


async def show_edit_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text, keyboard = load_assets(chat_id)
    query = update.callback_query
    await query.answer()
    if query.data == "edit_cancel":
        await query.message.edit_text(text["cancel_process"], reply_markup=None)
        return ConversationHandler.END
    chosen_friend = query.data.replace("edit_target_", "")
    context.user_data["edit_target"] = chosen_friend
    prompt = text["what_to_edit"].format(fullname=chosen_friend)
    await query.message.reply_text(
        prompt, reply_markup=keyboard["edit_options_keyboard"]
    )
    return ASK_INPUT


async def get_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    text, keyboard = load_assets(chat_id)
    chosen_column = query.data.lower().strip()
    context.user_data["edit_field"] = chosen_column

    await query.message.edit_reply_markup(reply_markup=None)

    if chosen_column == "fullname":
        txt = text["edit_fullname_text"]

    else:
        asset_key = f"ask_{chosen_column}"
        txt = text[asset_key]

    await query.message.reply_text(txt)
    return SAVE_INPUT


async def save_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text, keyboard = load_assets(chat_id)

    new_value = update.message.text
    target_friend = context.user_data.get("edit_target")
    field_to_edit = context.user_data.get("edit_field")

    update_friend_info(
        chat_id=chat_id, fullname=target_friend, field=field_to_edit, value=new_value
    )
    await update.message.reply_text(text["done"], reply_markup=keyboard["main_menu"])
    context.user_data.clear()
    return ConversationHandler.END


edit_friend_handler = ConversationHandler(
    entry_points=[
        CommandHandler("edit", edit_friend_trigger),
        MessageHandler(filters.Regex("^(Edit|edit|ویرایش)$"), edit_friend_trigger),
        CallbackQueryHandler(edit_friend_trigger, pattern="^edit_target_"),
    ],
    states={
        ASK_FIELD: [
            CallbackQueryHandler(show_edit_options, pattern="^edit_target_"),
            CallbackQueryHandler(show_edit_options, pattern="^edit_cancel$"),
        ],
        ASK_INPUT: [CallbackQueryHandler(get_input, pattern=".*")],
        SAVE_INPUT: [MessageHandler(state_filter, save_input)],
    },
    fallbacks=[
        CommandHandler("cancel", cancel),
        MessageHandler(filters.Regex(cancel_regex), cancel),
    ],
)
