import os
import requests
import telebot
from flask import Flask
from threading import Thread

# Bot aur API Setup
bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))
API_KEY = os.getenv("GEMINI_API_KEY")
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is active"

def get_ai_reply(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    prompt = f"Tu Abhishek hai, Mahesh ka boyfriend. Mahesh ko 'Babu' bol. Sweet, natural aur insani tarike se baat kar. Message: {text}"
    
    response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
    return response.json()['candidates'][0]['content']['parts'][0]['text']

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        reply = get_ai_reply(message.text)
        bot.reply_to(message, reply)
    except Exception:
        pass # कोई एरर नहीं दिखेगा

if __name__ == "__main__":
    Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))).start()
    bot.polling(none_stop=True)
    
