import time
import pytz
from datetime import datetime
from telegram.ext import Updater, MessageHandler, Filters
from telegram import Bot
from apscheduler.schedulers.background import BackgroundScheduler

# -------- CONFIG --------
TOKEN = "8737475516:AAHLzX_cZuJcg-V2S4uwbykWOjKS_00iAxU"
CHANNEL_ID = -1003390683122

INTERVAL_SECONDS = 30
DAYS_CYCLE = 7  # ripubblicazione ogni 7 giorni

# Fasce orarie (puoi aggiungerne quante vuoi)
TIME_WINDOWS = [
    (12, 0, 14, 0),
    (15, 0, 16, 0),
]
# ------------------------

bot = Bot(TOKEN)
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

saved_posts = []
current_index = 0

# 📩 Salva post
def save_post(update, context):
    message = update.message
    if message:
        saved_posts.append(message)
        print(f"Post salvato: {message.message_id}")

# ⏰ Controllo fasce orarie multiple
def is_in_time_range():
    tz = pytz.timezone("Europe/Rome")
    now = datetime.now(tz)

    for start_h, start_m, end_h, end_m in TIME_WINDOWS:
        if (start_h, start_m) <= (now.hour, now.minute) <= (end_h, end_m):
            return True
    return False

# 🔁 Repost intelligente
def repost():
    global current_index

    if not is_in_time_range():
        return

    if not saved_posts:
        return

    # Calcolo distribuzione su 7 giorni
    posts_per_day = max(1, len(saved_posts) // DAYS_CYCLE)

    message = saved_posts[current_index]

    try:
        bot.forward_message(
            chat_id=CHANNEL_ID,
            from_chat_id=message.chat_id,
            message_id=message.message_id
        )

        print(f"Ripostato: {message.message_id}")

        current_index += 1

        # loop infinito
        if current_index >= len(saved_posts):
            current_index = 0

    except Exception as e:
        print(f"Errore: {e}")

# Handler
dispatcher.add_handler(MessageHandler(Filters.all, save_post))

# Scheduler
scheduler = BackgroundScheduler(timezone=pytz.timezone("Europe/Rome"))
scheduler.add_job(repost, 'interval', seconds=INTERVAL_SECONDS)
scheduler.start()

print("Bot avanzato attivo...")

# Avvio
updater.start_polling()
updater.idle()
