from database import Session, User, Circle, get_user_language
from telegram.ext import ContextTypes
from bot.handlers.language_handler import load_assets
from dotenv import load_dotenv
from pathlib import Path
import datetime
import zoneinfo
import os

env_path = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(env_path)

LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")

TEHRAN_TZ = zoneinfo.ZoneInfo("Asia/Tehran")

async def birthday_reminder(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now(TEHRAN_TZ)
    today = now.date()
    tomorrow = today + datetime.timedelta(1)
    in_3_days = today + datetime.timedelta(3)
    in_7_days = today + datetime.timedelta(7)

    milestones = {
        "birthday_today": today.strftime("%m-%d"),
        "birthday_tomorrow": tomorrow.strftime("%m-%d"),
        "birthday_in_3_days": in_3_days.strftime("%m-%d"),
        "birthday_in_7_days": in_7_days.strftime("%m-%d"),
    }

    with Session() as session:
        for template_key, date_match_str in milestones.items():
            matching_friends = (
                session.query(Circle)
                .filter(Circle.birthday.like(f"%-{date_match_str}"))
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
                if friend:
                    try:
                        await context.bot.send_message(
                            chat_id=user.chat_id, text=alert_message, parse_mode="HTML"
                        )
                    except Exception as e:
                        print(f"Failed to send reminder to {user.chat_id}: {e}")
                else:
                    await context.bot.send_message(chat_id=user.chat_id, text="nothing today bruv", parse_mode="HTML")