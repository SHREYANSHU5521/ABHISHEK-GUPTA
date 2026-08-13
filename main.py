import os
import requests
import telebot
from flask import Flask
from threading import Thread

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask(__name__)

# System Prompt
SYSTEM_PROMPT = "Tum Abhishek ho. Mahesh babu ke boyfriend. Hinglish mein baat karo. Mahesh ko Babu kaho."

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"role": "user", "parts": [{"text": message.text}]}]
        }
        # Timeout 30 सेकंड कर दिया
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            res_data = response.json()
            reply = res_data['candidates'][0]['content']['parts'][0]['text']
            bot.reply_to(message, reply)
        else:
            bot.reply_to(message, f"Error: {response.status_code} - API Key ya Connection check karo.")
    except Exception as e:
        bot.reply_to(message, f"Technical error: {str(e)}")

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.polling(none_stop=True)
