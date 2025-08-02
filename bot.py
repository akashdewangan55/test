import nest_asyncio
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

nest_asyncio.apply()  # Only needed on Pydroid

BOT_TOKEN = "7710160278:AAEuNEnQOfIz2zNMWGWLLNCiNwiBn_4h-gw"  # Replace this

# Handler function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Hello! Bot is working.")

# Main function
async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    await app.run_polling()

# Run the bot
asyncio.run(main())