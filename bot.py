import os
import telebot
import requests
from flask import Flask, request, jsonify

# Initialize bot with token from environment variables
API_TOKEN = os.environ.get('API_TOKEN') or '8134541950:AAF0YnZmcge04P-SujsoV52sirhsFsHEb8Y'
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY') or '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'
bot = telebot.TeleBot(API_TOKEN)

app = Flask(__name__)

# Welcome message
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = ("Welcome to the AI Chatbot! 🤖\n"
                   "Feel free to ask me anything. Just type your message and I'll respond.\n"
                   "To exit the chat, just type 'exit'.")
    bot.send_message(message.chat.id, welcome_text)

# Message handler
@bot.message_handler(func=lambda message: True)
def respond_to_message(message):
    user_message = message.text
    chat_id = message.chat.id

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
        json={
            "model": "deepseek/deepseek-r1:free",
            "messages": [{"role": "user", "content": user_message}],
            "temperature": 0.9,
        }
    )

    if response.status_code == 200:
        bot_response = response.json().get('choices', [{}])[0].get('message', {}).get('content', 'Sorry, I did not understand that.')
    else:
        bot_response = f'Error occurred: {response.status_code}'

    bot.send_message(chat_id, bot_response)

# Webhook handler - must accept POST requests
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        bot.process_new_updates([update])
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 405

# Set webhook endpoint
@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    webhook_url = f"https://{os.environ.get('VERCEL_URL')}/webhook"
    if bot.set_webhook(url=webhook_url):
        return jsonify({"status": "success", "url": webhook_url}), 200
    return jsonify({"status": "failed"}), 400

# Health check endpoint
@app.route('/')
def home():
    return "Telegram bot is running", 200

if __name__ == '__main__':
    app.run()
