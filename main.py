from telegram import Bot
import time

TOKEN = "8737475516:AAF5yhE0IAS7P_IZCVivBgtZhWpXz2SHWxA"
CHANNEL = -1007120266689

bot = Bot(TOKEN)

print("Bot avviato...")

while True:
    try:
        bot.send_message(chat_id=CHANNEL, text="Test bot attivo 🚀")
        print("Messaggio inviato")
        time.sleep(60)
    except Exception as e:
        print("Errore:", e)
        time.sleep(60)
