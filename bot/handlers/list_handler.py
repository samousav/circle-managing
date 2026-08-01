from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot.handlers.language_handler import load_assets
from database import Session, Circle, User, get_user_language
from bot.handlers.friends_handler import add_friend, FULLNAME
from bot.assets.date_picker import format_birthday_for_user


async def handle_list_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = update.effective_chat.id
    text, keyboard = load_assets(chat_id)
    user_lang = get_user_language(chat_id)

    if data == "view_all_separate":
        friend_messages = []
        with Session() as session:
            user = session.query(User).filter(User.chat_id == chat_id).first()
            if user and user.circles:
                for friend in user.circles:

                    display_birthday = format_birthday_for_user(friend.birthday, user_lang)

                    friend_messages.append(
                        text["list_item_format"].format(
                            fullname=friend.fullname,
                            nickname=friend.nickname,
                            birthday=display_birthday,
                            phone=friend.phone,
                            location=friend.location,
                        )
                    )
                for message in friend_messages:
                    await query.message.reply_text(message)
                if friend_messages:
                    await query.message.reply_text(text["done"])

