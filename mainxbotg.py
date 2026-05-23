import logging
import sqlite3
import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ChatJoinRequestHandler,
    ChatMemberHandler,
    ContextTypes
)

# ---------------- CONFIG ----------------
BOT_TOKEN = os.getenv("8951924190:AAGdEOeC_GQNcAVjPdQiRPP7xV2BUxgU70U")
OWNER_ID = int(os.getenv("8787816729"))

WELCOME_MESSAGE = """🔥 Welcome to Auto Join System Bot! 🔥

🤖 Your bot is now ACTIVE
⚡ Auto join request approval enabled
🚀 Just add me as admin in your channel

👉 Join Updates:
https://t.me/Premium_Collection_bx

💎 Enjoy seamless automation 24/7
"""

# ---------------- LOGGING ----------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("channels.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS channels(
    chat_id INTEGER PRIMARY KEY,
    title TEXT
)
""")
conn.commit()

def save_channel(chat_id, title):
    cursor.execute(
        "INSERT OR IGNORE INTO channels VALUES (?, ?)",
        (chat_id, title)
    )
    conn.commit()

def fetch_channels():
    cursor.execute("SELECT * FROM channels")
    return cursor.fetchall()

# ---------------- AUTO APPROVE ----------------
async def auto_accept(update: Update,
                      context: ContextTypes.DEFAULT_TYPE):

    req = update.chat_join_request
    user = req.from_user
    chat = req.chat

    try:
        await context.bot.approve_chat_join_request(
            chat.id,
            user.id
        )

        try:
            await context.bot.send_message(
                user.id,
                f"Thanks for joining ({user.id})"
            )
        except:
            pass

    except Exception as e:
        logging.error(e)


# ---------------- BOT ADMIN DETECT ----------------
async def detect_admin(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE):

    cm = update.my_chat_member

    if not cm:
        return

    chat = cm.chat
    status = cm.new_chat_member.status

    if status == "administrator":

        save_channel(
            chat.id,
            chat.title or "Unnamed"
        )

        try:
            await context.bot.send_message(
                OWNER_ID,
                f"""✅ New Channel Connected

Name: {chat.title}
ID: {chat.id}
"""
            )
        except:
            pass


# ---------------- START ----------------
async def start(update: Update,
                context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        WELCOME_MESSAGE
    )


# ---------------- OWNER PANEL ----------------
async def panel(update: Update,
                context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    channels = fetch_channels()

    msg = f"📡 Connected: {len(channels)}\n\n"

    for cid, title in channels:
        msg += f"• {title}\n"

    await update.message.reply_text(msg)


# ---------------- BROADCAST ----------------
async def broadcast(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        return

    msg = " ".join(context.args)

    if not msg:
        return await update.message.reply_text(
            "/broadcast message"
        )

    sent = 0

    for cid, _ in fetch_channels():
        try:
            await context.bot.send_message(
                cid,
                msg
            )
            sent += 1
        except:
            pass

    await update.message.reply_text(
        f"Sent: {sent}"
    )


# ---------------- MAIN ----------------
def main():

    app = Application.builder()\
        .token(BOT_TOKEN)\
        .build()

    app.add_handler(
        ChatJoinRequestHandler(
            auto_accept
        )
    )

    app.add_handler(
        ChatMemberHandler(
            detect_admin,
            ChatMemberHandler.MY_CHAT_MEMBER
        )
    )

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CommandHandler(
            "panel",
            panel
        )
    )

    app.add_handler(
        CommandHandler(
            "broadcast",
            broadcast
        )
    )

    print("🤖 Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()