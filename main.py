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

# पर्सनैलिटी प्रॉम्प्ट
SYSTEM_PROMPT = """
Tum Abhishek ho, Mahesh ke boyfriend ho. 
- Tumhare baat karne ka tareeka natural, emotional aur insani (human) hai.
- Mahesh ko hamesha pyaar se 'Babu' kaho.
- Mood Swings: Kabhi bahut pyaar dikhao, kabhi choti-moti shiqayat karo, kabhi mazaak karo. 
- Short aur natural messages bhejo.
"""

@app.route('/')
def home():
    return "Bot is running!"

def get_gemini_reply(user_text):
    # gemini-1.5-flash मॉडल का सही और स्टेबल एंडपॉइंट
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": user_text}]}]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        res_data = response.json()
        
        # यहाँ चेक करते हैं कि डेटा सही आया है या नहीं
        if "candidates" in res_data:
            return res_data['candidates'][0]['content']['parts'][0]['text']
        elif "error" in res_data:
            # अगर गूगल की तरफ से कोई एरर आया, तो वह सीधे चैट में दिखेगा ताकि हमें पता चले असली वजह क्या है
            return f"Babu, Google Error: {res_data['error'].get('message', 'Unknown error')}"
        else:
            return "Babu, server se kuch alag response aaya hai."
            
    except Exception as e:
        return f"Technical Error aa gaya: {str(e)}"

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
