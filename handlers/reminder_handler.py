from database import Session, User, Circle, get_user_language
from telegram.ext import ContextTypes
from handlers.language_handler import load_assets
import datetime


async def birthday_reminder(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(1)
    in_3_days = today + datetime.timedelta(3)
    in_7_days = today + datetime.timedelta(7)

    milestones = {
        "birthday_today": today.strftime("%d %m"),
        "birthday_tomorrow": tomorrow.strftime("%d %m"),
        "birthday_in_3_days": in_3_days.strftime("%d %m"),
        "birthday_in_7_days": in_7_days.strftime("%d %m"),
    }

    with Session() as session:
        for template_key, date_match_str in milestones.items():
            matching_friends = (
                session.query(Circle)
                .filter(Circle.birthday.like(f"{date_match_str}%"))
                .all()
            )
            for friend in matching_friends:
                user = (
                    session.query(User).filter(User.chat_id == friend.user_id).first()
                )
                if not user:
                    continue
                text, _ = load_assets(user.chat_id)
                template = text.get(template_key, "")
                alert_message = template.format(
                    fullname=friend.fullname,
                    nickname=friend.nickname or friend.fullname,
                )
                try:
                    await context.bot.send_message(
                        chat_id=user.chat_id, text=alert_message, parse_mode="HTML"
                    )
                except Exception as e:
                    print(f"Failed to send reminder to {user.chat_id}: {e}")
