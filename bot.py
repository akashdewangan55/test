import os
import re
import logging
import asyncio
import functools
from pytube import YouTube
from pytube.exceptions import VideoUnavailable, RegexMatchError
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50MB (Telegram file limit)
DOWNLOAD_PATH = "downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when user sends /start"""
    await update.message.reply_text(
        "🎬 Welcome to YouTube Downloader Bot!\n"
        "Send me a YouTube link and I'll download it for you.\n\n"
        "🔍 I can:\n"
        "- Download videos (up to 50MB)\n"
        "- Extract audio (MP3 format)\n\n"
        "⚠️ Note: Videos longer than 15 minutes will be converted to audio automatically"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process YouTube links sent by users"""
    message_text = update.message.text
    youtube_url = extract_youtube_url(message_text)
    
    if not youtube_url:
        await update.message.reply_text("❌ Please send a valid YouTube URL")
        return
    
    try:
        yt = YouTube(youtube_url)
        title = yt.title
        keyboard = [
            [
                InlineKeyboardButton("🎥 Video", callback_data=f"video:{yt.video_id}"),
                InlineKeyboardButton("🎵 Audio", callback_data=f"audio:{yt.video_id}")
            ]
        ]
        await update.message.reply_text(
            f"🔍 Found: *{title}*\nChoose download format:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
    except (VideoUnavailable, RegexMatchError):
        await update.message.reply_text("❌ Video unavailable or invalid URL")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button selections"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    video_id = data.split(":")[1]
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        yt = YouTube(url)
        if "audio" in data:
            await download_and_send_audio(yt, query)
        elif "video" in data:
            await download_and_send_video(yt, query)
    except VideoUnavailable:
        await query.edit_message_text("❌ Video is no longer available")

async def download_and_send_audio(yt: YouTube, query):
    """Download and send audio to user"""
    await query.edit_message_text("⏳ Downloading audio...")
    
    try:
        # Get best audio stream
        stream = yt.streams.get_audio_only()
        if not stream:
            raise Exception("No audio stream found")
        
        # Download in thread
        loop = asyncio.get_running_loop()
        file_path = await loop.run_in_executor(
            None, 
            functools.partial(
                stream.download,
                output_path=DOWNLOAD_PATH,
                filename_prefix="audio_"
            )
        )
        
        # Rename to MP3
        new_path = os.path.splitext(file_path)[0] + ".mp3"
        os.rename(file_path, new_path)
        
        # Send to user
        await query.message.reply_audio(
            audio=open(new_path, "rb"),
            title=yt.title,
            performer=yt.author,
            caption=f"🎵 {yt.title}"
        )
        await query.edit_message_text("✅ Audio sent!")
    except Exception as e:
        logger.error(f"Audio error: {e}")
        await query.edit_message_text("❌ Failed to download audio")
    finally:
        if 'new_path' in locals() and os.path.exists(new_path):
            os.remove(new_path)

async def download_and_send_video(yt: YouTube, query):
    """Download and send video to user"""
    await query.edit_message_text("⏳ Checking video size...")
    
    try:
        # Get best video within size limit
        stream = yt.streams.filter(
            progressive=True,
            file_extension="mp4"
        ).order_by("resolution").desc().first()
        
        if not stream:
            raise Exception("No suitable video stream")
        
        # Check duration (15 minute limit)
        if yt.length > 900:  # 15 minutes
            await query.edit_message_text("⚠️ Video too long, sending audio instead")
            await download_and_send_audio(yt, query)
            return
        
        # Check file size
        if stream.filesize > MAX_VIDEO_SIZE:
            await query.edit_message_text("⚠️ Video too large, sending audio instead")
            await download_and_send_audio(yt, query)
            return
        
        # Download video
        await query.edit_message_text("⏳ Downloading video...")
        loop = asyncio.get_running_loop()
        file_path = await loop.run_in_executor(
            None,
            functools.partial(
                stream.download,
                output_path=DOWNLOAD_PATH,
                filename_prefix="video_"
            )
        )
        
        # Send to user
        await query.message.reply_video(
            video=open(file_path, "rb"),
            caption=f"🎥 {yt.title}",
            supports_streaming=True
        )
        await query.edit_message_text("✅ Video sent!")
    except Exception as e:
        logger.error(f"Video error: {e}")
        await query.edit_message_text("❌ Failed to download video")
    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

def extract_youtube_url(text: str) -> str:
    """Extract valid YouTube URL from text"""
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    
    matches = re.search(youtube_regex, text)
    if matches:
        return f"https://www.youtube.com/watch?v={matches.group(6)}"
    return None

def main():
    """Start the bot"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    
    # Message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Callback handler
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Start polling
    app.run_polling()

if __name__ == "__main__":
    main()