import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext

TOKEN = os.environ.get("BOT_TOKEN")  # Set this in Render environment variables
bot = Bot(token=TOKEN)

app = Flask(__name__)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=0, use_context=True)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("✅ Webhook bot is live!")

dispatcher.add_handler(CommandHandler("start", start))

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

@app.route('/', methods=['GET'])
def index():
    return "🤖 Webhook bot running!"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)