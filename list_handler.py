from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from language_handler import load_assets
from database import Session, Circle, User
from friends_handler import add_friend, FULLNAME


async def handle_list_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = update.effective_chat.id
    text, keyboard = load_assets(chat_id)
    if data == "view_all_separate":
        friend_messages = []
        with Session() as session:
            user = session.query(User).filter(User.chat_id == chat_id).first()
            if user and user.circles:
                for friend in user.circles:
                    friend_messages.append(
                        text["list_item_format"].format(
                            fullname=friend.fullname,
                            nickname=friend.nickname,
                            birthday=friend.birthday,
                            phone=friend.phone,
                            location=friend.location,
                        )
                    )
                for message in friend_messages:
                    await query.message.reply_text(message)
                if friend_messages:
                    await query.message.reply_text(text["done"])

