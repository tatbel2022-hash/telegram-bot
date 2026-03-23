import logging
from datetime import datetime, timedelta
from telegram import Bot
from apscheduler.schedulers.background import BackgroundScheduler
import time

# ================= CONFIGURAZIONE =================
TOKEN = "IL_TUO_TOKEN_DEL_BOT"
CHANNELS = [
    {
        "id": -1007120266689,      # ID del tuo canale privato
        "interval": 30,             # secondi tra un post e l'altro
        "repeat_days": 0,           # 0 per test immediato
        "time_window_start": (15,0),# inizio fascia
        "time_window_end": (16,0)   # fine fascia
    }
]
UPDATE_INTERVAL_HOURS = 1  # ogni quante ore aggiornare i post nuovi
# =================================================

logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
scheduler = BackgroundScheduler()
post_queues = {}

# Funzione per caricare i post da un canale
def load_posts(channel_id):
    updates = bot.get_chat(channel_id).get_history(limit=200)  # legge ultimi 200 post
    posts = []
    for msg in updates:
        posts.append({
            "message_id": msg.message_id,
            "last_posted": datetime.min  # inizialmente mai postato
        })
    return posts

# Funzione per aggiornare i post nuovi
def update_posts():
    for ch in CHANNELS:
        new_posts = load_posts(ch["id"])
        queue = post_queues.get(ch["id"], [])
        existing_ids = [p["message_id"] for p in queue]
        for p in new_posts:
            if p["message_id"] not in existing_ids:
                queue.append(p)
        post_queues[ch["id"]] = queue
        logging.info(f"Post aggiornati per {ch['id']}, totale in coda: {len(queue)}")

# Controlla se l'ora corrente è nella fascia
def in_time_window(start, end, now):
    start_hour, start_minute = start
    end_hour, end_minute = end
    now_hour, now_minute = now.hour, now.minute
    start_total = start_hour*60 + start_minute
    end_total = end_hour*60 + end_minute
    now_total = now_hour*60 + now_minute
    return start_total <= now_total < end_total

# Funzione per pubblicare post
def publish_posts():
    now = datetime.now()
    for ch in CHANNELS:
        if not in_time_window(ch["time_window_start"], ch["time_window_end"], now):
            continue
        queue = post_queues.get(ch["id"], [])
        if not queue:
            continue
        for post in queue:
            if now - post["last_posted"] >= timedelta(days=ch["repeat_days"]):
                try:
                    bot.forward_message(
                        chat_id=ch["id"],
                        from_chat_id=ch["id"],
                        message_id=post["message_id"]
                    )
                    post["last_posted"] = now
                    logging.info(f"Post {post['message_id']} pubblicato in {ch['id']}")
                    time.sleep(ch["interval"])
                except Exception as e:
                    logging.error(f"Errore pubblicazione post {post['message_id']}: {e}")
                break

# Scheduler
scheduler.add_job(update_posts, 'interval', hours=UPDATE_INTERVAL_HOURS)
scheduler.add_job(publish_posts, 'interval', minutes=1)

# Carica inizialmente i post
for ch in CHANNELS:
    post_queues[ch["id"]] = load_posts(ch['id'])

scheduler.start()

logging.info("Bot in modalità test avviato...")
try:
    while True:
        time.sleep(10)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    logging.info("Bot arrestato.")
