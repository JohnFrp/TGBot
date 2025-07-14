import os
import telebot
import requests
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Initialize bot with token from environment variables
API_TOKEN = os.environ.get('8134541950:AAF0YnZmcge04P-SujsoV52sirhsFsHEb8Y')
OPENROUTER_API_KEY = os.environ.get('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')
bot = telebot.TeleBot(API_TOKEN)

# Handler for the /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "Welcome to the AI Chatbot! 🤖\nSend me a message and I'll respond."
    bot.send_message(message.chat.id, welcome_text)

# Handler for all messages
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={
                "model": "deepseek/deepseek-r1:free",
                "messages": [{"role": "user", "content": message.text}],
                "temperature": 0.7,
            }
        )
        response.raise_for_status()
        reply = response.json()['choices'][0]['message']['content']
    except Exception as e:
        reply = f"Sorry, I encountered an error: {str(e)}"
    
    bot.send_message(message.chat.id, reply)

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        json_data = request.get_json()
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
        return jsonify(success=True), 200
    return jsonify(success=False), 405

# Set webhook endpoint
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    webhook_url = f"https://{os.environ.get('VERCEL_URL')}/webhook"
    success = bot.set_webhook(url=webhook_url)
    return jsonify(success=success, url=webhook_url), 200 if success else 400

# Health check endpoint
@app.route('/')
def health_check():
    return "Bot is running", 200

if __name__ == '__main__':
    app.run(debug=True)