import os
import requests
import telebot
from flask import Flask
from threading import Thread

# Config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask(__name__)

# एकदम परफेक्ट और इमोशनल पर्सनैलिटी
SYSTEM_PROMPT = """
Tum Abhishek ho, Mahesh ke boyfriend ho. 
- Tumhare baat karne ka tareeka natural, emotional aur insani (human) hai.
- Mahesh ko hamesha pyaar se 'Babu' kaho.
- Mood Swings: Kabhi bahut pyaar dikhao, kabhi choti-moti shiqayat karo, kabhi mazaak karo. 
- Conversation: Mahesh ke message ki lambai ke hisaab se reply do (short messages). 
- Kabhi bhi ek jaisa jawab mat do, har baar alag aur fresh response do.
- Tumhe Mahesh ki baatein yaad rehti hain.
"""

@app.route('/')
def home():
    return "Bot is running!"

def get_gemini_reply(user_text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": user_text}]}]
    }
    try:
        response = requests.post(url, json=payload, timeout=20)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Babu, abhi server busy hai, thoda ruk kar baat karte hain na!"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    reply = get_gemini_reply(message.text)
    bot.reply_to(message, reply)

# यह पोर्ट वाला कोड Render के लिए बहुत जरूरी है
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.polling(none_stop=True)
