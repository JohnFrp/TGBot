# bot.py
import telebot
import requests
from flask import Flask, request

API_TOKEN = '8134541950:AAF0YnZmcge04P-SujsoV52sirhsFsHEb8Y'
bot = telebot.TeleBot(API_TOKEN)

app = Flask(__name__)

# Welcome message for the /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = ("Welcome to the AI Chatbot! 🤖\n"
                    "Feel free to ask me anything. Just type your message and I'll respond.\n"
                    "To exit the chat, just type 'exit'.")
    bot.send_message(message.chat.id, welcome_text)

@bot.message_handler(func=lambda message: True)
def respond_to_message(message):
    user_message = message.text
    chat_id = message.chat.id

    # Call OpenRouter API for chatbot response
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer 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",
        },
        json={
            "model": "deepseek/deepseek-r1:free",
            "messages": [{"role": "user", "content": user_message}],
            "top_p": 1,
            "temperature": 0.9,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "repetition_penalty": 1,
            "top_k": 0,
        }
    )

    if response.status_code == 200:
        bot_response = response.json().get('choices', [{}])[0].get('message', {}).get('content', 'Sorry, I did not understand that.')
    else:
        bot_response = 'Error occurred while processing your request.'

    bot.send_message(chat_id, bot_response)

# Webhook route
@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'Invalid content type', 403

# Set webhook (you'll need to call this once)
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    # Replace <YOUR_VERCEL_URL> with your actual Vercel app URL
    webhook_url = f"https://your-vercel-app-url.vercel.app/"
    s = bot.set_webhook(url=webhook_url)
    if s:
        return "Webhook setup ok"
    else:
        return "Webhook setup failed"

if __name__ == '__main__':
    app.run()