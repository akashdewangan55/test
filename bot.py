import asyncio
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes
)

BOT_TOKEN = "7710160278:AAEuNEnQOfIz2zNMWGWLLNCiNwiBn_4h-gw"  # Replace with your actual token

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot is live on Render!")

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    await app.run_polling()

# For local testing
if __name__ == "__main__":
    asyncio.run(main())