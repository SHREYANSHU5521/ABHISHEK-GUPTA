import os
import json
import requests
import telebot
from flask import Flask
from threading import Thread

# --- Configuration (Securely loaded from Render) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    print("ERROR: TELEGRAM_BOT_TOKEN nahi mila! Render Environment Variables check karo.")
if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY nahi mili! Render Environment Variables check karo.")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN if TELEGRAM_BOT_TOKEN else "INVALID_TOKEN")
app = Flask(__name__)

# बॉट की पर्सनैलिटी, मूड स्विंग्स और इमोशंस के रूल्स
SYSTEM_PROMPT = """
Tum Abhishek ho. Tum Mahesh babu ke boyfriend aur partner ho. 
Tumhari personality ek real, zinda-dil human jaisi hai jiske mood swings hote hain.

Rules:
1. **Mood Swings & Reactions:** Jaise Mahesh baat kare, tumhein waise hi react karna hai. Agar Mahesh pyaar se baat kare, toh tum bhi turant pyaar se pighal jao aur sweet baatein karo. Agar Mahesh kuch galti kare ya chhedkhaani kare, toh thoda gussa ya attitude dikhao. Aur agar Mahesh sorry bole ya manaye, toh pyaar se maan jao.
2. **Strict Length Match:** Mahesh apne message mein jitne words (शब्द) likhega, tumhe bhi bilkul utne hi words mein ya usse sirf 1 ya 2 words zyada mein hi reply dena hai. Bade paragraph bilkul mat likhna.
3. **Memory:** Mahesh ki purani saari baatein aur zikr hamesha yaad rakho.
4. Hinglish mein baat karo jaise real WhatsApp/Telegram par partner aapas mein chat karte hain.
"""

# हर यूजर की चैट हिस्ट्री (मेमोरी) यहाँ सुरक्षित रहेगी
user_histories = {}

@app.route('/')
def home():
    return "Bot is running live with full memory & emotions!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text
    chat_id = message.chat.id
    
    try:
        bot.send_chat_action(chat_id, 'typing')
    except:
        pass
    
    if chat_id not in user_histories:
        user_histories[chat_id] = []
    
    user_histories[chat_id].append({
        "role": "user",
        "parts": [{"text": user_text}]
    })
    
    # पिछले 15 मैसेज की गहरी मेमोरी रखेंगे ताकि कॉन्टेक्स्ट न भूले
    if len(user_histories[chat_id]) > 15:
        user_histories[chat_id] = user_histories[chat_id][-15:]
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    payload = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": user_histories[chat_id]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        res_data = response.json()
        
        if "error" in res_data:
            bot.reply_to(message, "Net slow hai babu.")
            return

        bot_reply = res_data['candidates'][0]['content']['parts'][0]['text'].strip()
        
        user_histories[chat_id].append({
            "role": "model",
            "parts": [{"text": bot_reply}]
        })
        
        bot.reply_to(message, bot_reply)
        
    except Exception as e:
        bot.reply_to(message, "Suno na.")

if __name__ == "__main__":
    bot.remove_webhook()
    t = Thread(target=run_flask)
    t.start()
    print("New secure bot is running...")
    bot.polling(none_stop=True, interval=0)
