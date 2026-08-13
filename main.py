import os
import telebot
import requests

bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": f"Abhishek ho tum, Mahesh ke liye natural reply do: {message.text}"}]}]}
        response = requests.post(url, json=payload, timeout=20)
        reply = response.json()['candidates'][0]['content']['parts'][0]['text']
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, "Error aa gaya babu: " + str(e))

bot.polling(none_stop=True)
