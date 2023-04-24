import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from elsa_telegram_bot.audio import transcribe_audio

load_dotenv()  # take environment variables from .env.

from elsa_telegram_bot.chat import get_answer

TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

ALLOWED_USERS = [
    175402881,  # Taras
    557037718,  # Ira
]

CURRENT_DIR = Path(__file__).parent
PROJECT_DIR = CURRENT_DIR.parent
AUDIO_DIR = PROJECT_DIR / "audio"

logger.configure(
    handlers=[
        dict(sink=sys.stdout, format="<blue>{time}</blue> | {elapsed} | {message}"),
    ],
)


def only_allowed_users(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in ALLOWED_USERS:
            logger.info(f"User {update.effective_user.id} is not allowed to use this bot.")
            return
        await func(update, context)

    return wrapper


@only_allowed_users
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(update)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


@only_allowed_users
async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = await get_answer(update.message.text)
    logger.info(answer)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)


@only_allowed_users
async def voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.voice.get_file()
    logger.info(file)
    file_path = await file.download_to_memory()
    # file_path = await file.download_to_drive(
    #     custom_path=AUDIO_DIR / f"{file.file_unique_id}_{update.message.date.strftime('%Y-%m-%d_%H%M%S')}.oga")
    logger.info(file_path)
    text = await transcribe_audio(file_path)
    logger.info(text)
    answer = await get_answer(text)
    logger.info(answer)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)


def run():
    application = ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()

    start_handler = CommandHandler('start', start)
    gpt_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), gpt)
    voice_handler = MessageHandler(filters.VOICE & (~filters.COMMAND), voice)

    application.add_handler(start_handler)
    application.add_handler(gpt_handler)
    application.add_handler(voice_handler)

    application.run_polling()
