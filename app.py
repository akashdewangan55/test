from flask import Flask, request
import telegram

TOKEN = "7710160278:AAEuNEnQOfIz2zNMWGWLLNCiNwiBn_4h-gw"
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

@app.route(f'/{TOKEN}', methods=['POST'])
def respond():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    message = update.message.text

    if message == "/start":
        bot.sendMessage(chat_id=chat_id, text="👋 Hello! Webhook is working.")
    else:
        bot.sendMessage(chat_id=chat_id, text="You said: " + message)

    return 'ok'

@app.route('/')
def index():
    return "🤖 Bot is running on Render using webhook!", 200

if __name__ == '__main__':
    app.run()