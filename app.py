import os
import fitz  # PyMuPDF
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from summarizer import summarize_text

TOKEN = "7710160278:AAEuNEnQOfIz2zNMWGWLLNCiNwiBn_4h-gw"  # Replace this with your real bot token

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("👋 Send me a PDF and I’ll summarize it for you!")

def handle_pdf(update: Update, context: CallbackContext):
    file = update.message.document
    if file.mime_type != "application/pdf":
        update.message.reply_text("❌ Please send a valid PDF file.")
        return

    file_path = os.path.join(DOWNLOAD_DIR, file.file_name)
    file.get_file().download(file_path)
    update.message.reply_text("📄 PDF received. Extracting text...")

    # Extract text
    doc = fitz.open(file_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()

    if not full_text.strip():
        update.message.reply_text("⚠️ Couldn't extract any text from this PDF.")
        return

    update.message.reply_text("🧠 Summarizing text, please wait...")

    # Summarize
    summary = summarize_text(full_text)
    update.message.reply_text(f"✅ Summary:\n\n{summary[:4096]}")  # Telegram limit

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document.mime_type("application/pdf"), handle_pdf))

    updater.start_polling()
    print("✅ Bot is running...")
    updater.idle()

if __name__ == "__main__":
    main()