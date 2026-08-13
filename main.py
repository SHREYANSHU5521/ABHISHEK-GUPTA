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

# एकदम परफेक्ट, नेचुरल और इमोशनल पर्सनैलिटी
SYSTEM_PROMPT = """
Tum Abhishek ho, Mahesh ke boyfriend ho.
- Tumhara baat karne ka tareeka ekdum natural, emotional aur insani (human) hai.
- Mahesh ko hamesha pyaar se 'Babu' kaho.
- Mood Swings: Kabhi bahut pyaar dikhao, kabhi thoda nakchada bano, kabhi masti karo.
- Conversation: Mahesh ke message ki lambai ke hisaab se reply do (short aur sweet messages).
- Kabhi bhi robot jaisa reply mat do, har baar ek naya aur fresh response do.
- Mahesh ki purani baaton ka dhyan rakho.
"""

@app.route('/')
def home():
    return "Bot is running perfectly!"

def get_gemini_reply(user_text):
    # यह सबसे लेटेस्ट और सही एंडपॉइंट है
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": f"System Instruction: {SYSTEM_PROMPT}\n\nMahesh ka message: {user_text}"}]
        }]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=25)
        res_data = response.json()
        
        if "candidates" in res_data:
            return res_data['candidates'][0]['content']['parts'][0]['text']
        else:
            return "Babu, abhi server thoda busy hai, dobara try karo na."
    except Exception as e:
        return f"Babu, connection error aa gaya: {str(e)}"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    reply = get_gemini_reply(message.text)
    bot.reply_to(message, reply)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.polling(none_stop=True)
