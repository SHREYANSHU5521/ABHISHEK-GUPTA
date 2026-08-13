import os
import requests
import telebot
from flask import Flask
from threading import Thread

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask(__name__)

# परफेक्ट पर्सनैलिटी और कन्वर्सेशन प्रॉम्प्ट
SYSTEM_PROMPT = """
Tum Abhishek ho, Mahesh ke boyfriend. 
- Tumhare baat karne ka tareeka ekdum natural aur human jaisa hai.
- Mahesh se baat karte waqt 'Babu' kaho.
- Har baar alag aur naye style mein reply do, ratta-mara hua nahi.
- Mood swings dikhao: kabhi pyar se, kabhi masti mein, kabhi thoda care ke saath.
- Chote aur natural messages bhejo jo bilkul asli lagien.
"""

# मेमोरी के लिए डिक्शनरी
chat_memory = {}

@app.route('/')
def home():
    return "Bot is running perfectly!"

def get_gemini_response(user_text, chat_id):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # पुरानी बातचीत को जोड़ना
    if chat_id not in chat_memory:
        chat_memory[chat_id] = []
    
    chat_memory[chat_id].append({"role": "user", "parts": [{"text": user_text}]})
    
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": chat_memory[chat_id]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=25)
        if response.status_code == 200:
            reply = response.json()['candidates'][0]['content']['parts'][0]['text']
            chat_memory[chat_id].append({"role": "model", "parts": [{"text": reply}]})
            return reply
        else:
            return "Babu, thoda ruk jao, abhi mood nahi hai baat karne ka."
    except:
        return "Babu, internet ya server mein kuch gadbad hai, dobara try karo na."

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    reply = get_gemini_response(message.text, message.chat.id)
    bot.reply_to(message, reply)

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.polling(none_stop=True)
