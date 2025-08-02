from flask import Flask, request
import telegram
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telegram.Bot(token=BOT_TOKEN)

app = Flask(__name__)

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    message = update.message.text

    if message == "/start":
        bot.sendMessage(chat_id=chat_id, text="🤖 Hello! I'm alive using webhooks.")
    else:
        bot.sendMessage(chat_id=chat_id, text="You said: " + message)

    return "OK"

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(debug=True)