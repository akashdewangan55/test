import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

nest_asyncio.apply()  # ✅ Needed only in Pydroid3 (not on Render)

BOT_TOKEN = "7710160278:AAEuNEnQOfIz2zNMWGWLLNCiNwiBn_4h-gw"  # ⚠️ Replace with your bot token

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Hello! I'm alive and working!")

async def main():
    # Create application
    app = Application.builder().token(BOT_TOKEN).build()

    # Register command handler
    app.add_handler(CommandHandler("start", start))

    # Start polling
    await app.run_polling()

# Run main
asyncio.run(main())