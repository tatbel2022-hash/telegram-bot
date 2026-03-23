import time
from telegram import Bot
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

# ------------------- CONFIG -------------------
TOKEN = "8737475516:AAF5yhE0IAS7P_IZCVivBgtZhWpXz2SHWxA"  # <-- metti qui il token reale di BotFather
CHANNEL_ID = -1007120266689      # ID del canale (numerico)
UPDATE_INTERVAL_SECONDS = 30     # ogni quanti secondi pubblicare
TIME_WINDOW_START = (15, 0)       # fascia oraria inizio (h, m)
TIME_WINDOW_END = (16, 0)       # fascia oraria fine (h, m)
MAX_POSTS_HISTORY = 500           # quanti post leggere dal canale
# --------------------------------------------

bot = Bot(TOKEN)
scheduler = BackgroundScheduler(timezone=pytz.timezone("Europe/Rome"))

# Lista dei post già pubblicati (memoria temporanea)
post_queue = []

# Funzione per caricare i post dal canale
def load_posts():
    global post_queue
    updates = bot.get_chat(CHANNEL_ID).get_history(limit=MAX_POSTS_HISTORY)
    post_queue = updates[::-1]  # inverti per partire dal post più vecchio

# Funzione per ripubblicare
def update_posts():
    from datetime import datetime
    now = datetime.now(pytz.timezone("Europe/Rome"))
    if TIME_WINDOW_START <= (now.hour, now.minute) <= TIME_WINDOW_END:
        if post_queue:
            post = post_queue.pop(0)
            bot.forward_message(chat_id=CHANNEL_ID, from_chat_id=CHANNEL_ID, message_id=post.message_id)
            post_queue.append(post)
            print(f"Post {post.message_id} pubblicato in {CHANNEL_ID}")

# Carica inizialmente i post
load_posts()

# Scheduler per aggiornare ogni UPDATE_INTERVAL_SECONDS
scheduler.add_job(update_posts, 'interval', seconds=UPDATE_INTERVAL_SECONDS)
scheduler.start()

print("Bot avviato e pronto a ripubblicare i post...")

# Mantieni il bot attivo
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    scheduler.shutdown()
