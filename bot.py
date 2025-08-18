import os
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
import logging
import asyncio

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Check your .env file.")

bot = AsyncTeleBot(BOT_TOKEN)

@bot.message_handler(commands=["start", "hello"])
async def send_welcome(message):
    try:
        await bot.reply_to(message, "Hello, how are you?")
        logger.info(f"Sent welcome message to user {message.chat.id}")
    except Exception as e:
        logger.error(f"Error in send_welcome: {e}")

def process_document_file(message):
    file_name = message.document.file_name or "Unknown file"
    return f"Received your document file: <b>{file_name}</b>"

@bot.message_handler(content_types=['document'])
async def handle_docs(message):
    try:
        response = process_document_file(message)
        await bot.reply_to(message, response, parse_mode="HTML")
        logger.info(f"Processed document file from user {message.chat.id}")
    except Exception as e:
        logger.error(f"Error in handle_docs: {e}")

def process_audio_file(message):
    file_name = getattr(message.audio, 'file_name', None) or f"Audio file (ID: {message.audio.file_id[:10]}...)"
    return f"Received your audio file: <b>{file_name}</b>"


@bot.message_handler(content_types=['audio'])
async def handle_docs_audio(message):
    try:
        response = process_audio_file(message)
        await bot.reply_to(message, response, parse_mode="HTML")
        logger.info(f"Processed audio file from user {message.chat.id}")
    except Exception as e:
        logger.error(f"Error in handle_docs_audio: {e}")

@bot.message_handler(func=lambda message: True)
async def echo_all(message):
    try:
        if len(message.text) > 1000:  # Message length limit
            await bot.reply_to(message, "Message is too long!")
            logger.warning(f"User {message.chat.id} sent a message that is too long.")
            return
        await bot.reply_to(message, message.text)
        logger.info(f"Echoed message to user {message.chat.id}")
    except Exception as e:
        logger.error(f"Error in echo_all: {e}")

if __name__ == "__main__":
    try:
        logger.info("Bot is starting...")
        asyncio.run(bot.infinity_polling())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")