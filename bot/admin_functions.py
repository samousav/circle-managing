from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from database import get_all_users
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

ADMIN_CHAT_ID = int(os.getenv("ADMINS"))


async def get_all_users_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id != ADMIN_CHAT_ID:
        return
    
    users = get_all_users()

    if not users:
        await update.message.reply_text("No users found")
        return
    
    total_users = len(users)
    total_friends = sum([user["friend_count"] for user in users])

    report = (
        f"📊 <b>SOCIRCLE SYSTEM REPORT</b>\n"
        f"👥 <b>Total Users:</b> <code>{total_users}</code>\n"
        f"👥 <b>Total Stored Contacts:</b> <code>{total_friends}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
    )

    for user in users:
        username = f"@{user['username']}" if user["username"] else "N/A"
        report += (
            f"👤 <b>Name:</b> <a href='tg://user?id={user['chat_id']}'>{user['name']}</a>\n"
            f"🆔 <b>Chat ID:</b> <code>{user['chat_id']}</code>\n"
            f"💬 <b>Username:</b> {username}\n"
            f"🌐 <b>Lang:</b> {user['language']}\n"
            f"⭕️ <b>Total Friends:</b> <code>{user['friend_count']}</code>\n"
            f"───────────────\n"
        )
    if len(report) > 4000:
        for chunk in [report[i:i+4000] for i in range(0, len(report), 4000)]:
            await update.message.reply_text(chunk, parse_mode="HTML")
    else:
        await update.message.reply_text(report, parse_mode="HTML")



WAITING_FOR_BROADCAST_CONTENT = 100

async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id != ADMIN_CHAT_ID:
        return ConversationHandler.END
    
    await update.message.reply_text("Broadcasting mode enabled. Send anything you want to send to all users.")
    return WAITING_FOR_BROADCAST_CONTENT

async def send_content_to_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id != ADMIN_CHAT_ID:
        return ConversationHandler.END
    users = get_all_users()
    if not users:
        await update.message.reply_text("No users found")
        return ConversationHandler.END
    await update.message.reply_text("Sending to all users...")

    success_count = 0
    fail_count = 0
    for user in users:
        target_chat_id = user["chat_id"]
        if target_chat_id == ADMIN_CHAT_ID:
            continue

        try:
            await context.bot.copy_message(chat_id=target_chat_id, from_chat_id=chat_id, message_id=update.message.message_id)
            success_count += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            fail_count += 1
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Failed to send to {user['firstname']} {user['username']} ({target_chat_id}): {e}")
    
    await update.message.reply_text(f"✅ <b>Broadcast Completed!</b>\n\n"
        f"🟢 Successfully sent: <code>{success_count}</code>\n"
        f"🔴 Failed (Blocked/Left): <code>{fail_count}</code>",
        parse_mode="HTML")
    return ConversationHandler.END

async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fallback to cancel the operation"""
    await update.message.reply_text("❌ Broadcast canceled.")
    return ConversationHandler.END


broadcast_handler = ConversationHandler(
    entry_points=[CommandHandler("broadcast", start_broadcast)],
    states={
        WAITING_FOR_BROADCAST_CONTENT: [MessageHandler(filters.ALL & ~filters.COMMAND, send_content_to_all)]
    },
    fallbacks=[CommandHandler("cancel", cancel_broadcast)]
)