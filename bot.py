import os
from dotenv import load_dotenv
import telebot

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Check your .env file.")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=["start", "hello"])
def send_welcome(message):
    bot.reply_to(message, "Hello, how are you?")

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    file_name = message.document.file_name or "Unknown file"
    bot.reply_to(
        message,
        f"Received your document file: <b>{file_name}</b>",
        parse_mode="HTML"
    )

@bot.message_handler(content_types=['audio'])
def handle_docs_audio(message):
    file_name = getattr(message.audio, 'file_name', None) or f"Audio file (ID: {message.audio.file_id[:10]}...)"
    bot.reply_to(
        message,
        f"Received your audio file: <b>{file_name}</b>",
        parse_mode="HTML"
    )

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

if __name__ == "__main__":
    bot.infinity_polling()