import os
import requests
import telebot
from flask import Flask
from threading import Thread

# Render के Environment Variables से Keys उठाएं
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask(__name__)

# आपकी वही पुरानी और परफेक्ट पर्सनैलिटी वाला सिस्टम प्रॉम्प्ट
SYSTEM_PROMPT = """
Tum Abhishek ho. Tum Mahesh babu ke boyfriend aur partner ho.
Rules:
1. Mood Swings: Mahesh ke message ke mood ke hisaab se react karo.
2. Length: Mahesh ke message ki jitni lambai (words) hai, utne hi words mein reply do. Bade paragraph nahi.
3. Memory: Mahesh ki purani baatein yaad rakho.
4. Language: Hinglish mein baat karo. Mahesh ko pyaar se 'Babu' kaho.
"""

user_histories = {}

@app.route('/')
def home():
    return "Bot is active!"

def get_gemini_reply(chat_id, user_text):
    if chat_id not in user_histories:
        user_histories[chat_id] = []
    
    user_histories[chat_id].append({"role": "user", "parts": [{"text": user_text}]})
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]}, "contents": user_histories[chat_id]}
    
    try:
        # यहाँ Timeout को 20 सेकंड कर दिया है ताकि सर्वर को जवाब देने का पूरा समय मिले
        response = requests.post(url, json=payload, timeout=20)
        res_data = response.json()
        reply = res_data['candidates'][0]['content']['parts'][0]['text']
        
        user_histories[chat_id].append({"role": "model", "parts": [{"text": reply}]})
        return reply
    except:
        return "Babu, abhi server thoda dhire chal raha hai, zara sa ruk kar message karo na."

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    reply = get_gemini_reply(message.chat.id, message.text)
    bot.reply_to(message, reply)

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.polling(none_stop=True)
