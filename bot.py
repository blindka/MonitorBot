import os
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
import logging
import asyncio
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()
logger.info(f"BOT_TOKEN loaded: {os.environ.get('TELEGRAM_BOT_TOKEN') is not None}")

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Check your .env file.")

try:
    resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
    if resp.status_code == 200 and resp.json().get("ok"):
        logger.info("Webhook deleted successfully. Switching to polling mode.")
    else:
        logger.warning(f"Failed to delete webhook: {resp.text}")
except Exception as e:
    logger.error(f"Error deleting webhook: {e}")

bot = AsyncTeleBot(BOT_TOKEN)

# Start and Hello command handler
@bot.message_handler(commands=["start", "hello"])
async def send_welcome(message):
    try:
        await bot.reply_to(message, "Hello, how are you?")
        logger.info(f"Sent welcome message to user {message.chat.id}")
    except Exception as e:
        logger.error(f"Error in send_welcome: {e}")

# Help command handler
@bot.message_handler(commands=["help"])
async def send_help(message):
    try:
        help_text = (
            "/start - Start using the bot\n"
            "/hello - Welcome message\n"
            "/help - Show this menu\n"
            "Sending a document or an audio - Bot will acknowledge the document\n"
        )
        await bot.reply_to(message, help_text, parse_mode="HTML")
        logger.info(f"Sent help message to user {message.chat.id}")
    except Exception as e:
        logger.error(f"Error in send_help: {e}")

def process_document_file(message):
    file_name = message.document.file_name or "Unknown file"
    return f"Received your document file: <b>{file_name}</b>"

#  Document handler
@bot.message_handler(content_types=['document'])
async def handle_docs(message):
    try:
        response = process_document_file(message)
        await bot.reply_to(message, response, parse_mode="HTML")
        logger.info(f"Received document file from user {message.chat.id}")
    except Exception as e:
        logger.error(f"Error in handle_docs: {e}")

def process_audio_file(message):
    file_name = getattr(message.audio, 'file_name', None) or f"Audio file (ID: {message.audio.file_id[:10]}...)"
    return f"Received your audio file: <b>{file_name}</b>"
# Audio handler
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
        if len(message.text) > 1000:
            await bot.reply_to(message, "Message is too long!")
            logger.warning(f"User {message.chat.id} sent a message that is too long.")
            return
        await bot.reply_to(message, message.text)
        logger.info(f"Echoed message to user {message.chat.id}")
    except Exception as e:
        logger.error(f"Error in echo_all: {e}")

@bot.message_handler(func=lambda message: message.text and message.text.startswith('/'))
async def handle_unknown_command(message):
    try:
        await bot.reply_to(message, "Unknown command, Please try again.")
        logger.warning(f"User {message.chat.id} sent an unknown command: {message.text}")
    except Exception as e:
        logger.error(f"Error in handle_unknown_command: {e}")
        
if __name__ == "__main__":
    try:
        logger.info("Bot is starting...")
        asyncio.run(bot.infinity_polling())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
