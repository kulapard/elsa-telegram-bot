import sys
from contextlib import asynccontextmanager
from functools import wraps
from typing import AsyncIterator, BinaryIO, Callable
from uuid import uuid4

import aiofiles
from chat import get_answer
from config import ADMIN_USER_ID, ALLOWED_USER_IDS, PORT, TELEGRAM_API_TOKEN
from loguru import logger
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.helpers import escape_markdown
from voice import convert_ogg_to_mp3, transcribe_audio

from elsa_telegram_bot.invite import Invite

logger.configure(
    handlers=[
        {"sink": sys.stdout, "format": "<blue>{time}</blue> | {elapsed} | {message}"},
    ],
)


def admin_required(func) -> Callable:
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id if update.effective_user else None
        if user_id != ADMIN_USER_ID:
            logger.error(f"User {user_id} is not allowed to use this command.")
            return
        await func(update, context)

    return wrapper


def only_allowed_users(func) -> Callable:
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id if update.effective_user else None
        if user_id not in ALLOWED_USER_IDS:
            logger.error(f"User {user_id} is not allowed to use this bot.")
            return
        await func(update, context)

    return wrapper


@admin_required
async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(update)
    chat_id = update.effective_chat.id  # type: ignore[union-attr]
    invitation = Invite.generate()
    url = f"https://t.me/{context.bot.username}?start={invitation.code}"
    logger.info(f"Generated invite link {url} for chat {chat_id}")
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"Here is the invitation link:\n\n```\n{url}\n```",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def start_with_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(update)
    chat_id = update.effective_chat.id  # type: ignore[union-attr]
    if context.args:
        code = context.args[0]

        if Invite.check(code):
            await context.bot.send_message(chat_id, "Welcome!")
            Invite.use(code, chat_id)
            Invite.clear_expired()
        else:
            await context.bot.send_message(
                chat_id, "Sorry, your invitation link is invalid or has expired."
            )
    else:
        await context.bot.send_message(
            chat_id, "This is a private bot. An invitation is required to start."
        )


def quoted_response(question: str, answer: str) -> str:
    safe_question = escape_markdown(question, version=2)
    safe_answer = escape_markdown(answer, version=2)
    return f"\\> _{safe_question}_\n\n{safe_answer}"


@only_allowed_users
async def text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    human_input: str = update.message.text  # type: ignore
    user_id: int = update.effective_user.id  # type: ignore[union-attr]
    chat_id: int = update.effective_chat.id  # type: ignore[union-attr]
    answer = await get_answer(human_input, user_id)
    logger.info(answer)
    await context.bot.send_message(
        chat_id=chat_id,
        text=answer,
    )


@asynccontextmanager
async def temp_file(suffix: str) -> AsyncIterator[BinaryIO]:
    async with aiofiles.tempfile.NamedTemporaryFile(mode="w+b", suffix=suffix) as file:
        yield file  # type: ignore[misc]


@only_allowed_users
async def voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id  # type: ignore[union-attr]
    chat_id = update.effective_chat.id  # type: ignore[union-attr]

    file = await update.message.voice.get_file()  # type: ignore[union-attr]
    logger.info(file)

    async with temp_file(suffix=".oga") as ogg_file:
        await file.download_to_drive(ogg_file.name)
        async with temp_file(suffix=".mp3") as mp3_file:
            await convert_ogg_to_mp3(ogg_file.name, mp3_file.name)
            human_input = await transcribe_audio(mp3_file)

    answer = await get_answer(human_input, user_id)
    logger.info(answer)
    await context.bot.send_message(
        chat_id=chat_id,
        text=quoted_response(human_input, answer),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


def create_app() -> Application:  # type: ignore[type-arg]
    application = ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()

    invite_handler = CommandHandler("invite", invite)
    start_with_token_handler = CommandHandler("start", start_with_token)

    text_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), text)
    voice_handler = MessageHandler(filters.VOICE & (~filters.COMMAND), voice)

    application.add_handler(invite_handler)
    application.add_handler(start_with_token_handler)
    application.add_handler(text_handler)
    application.add_handler(voice_handler)

    return application


def run_polling() -> None:
    logger.info("Starting bot in POLLING mode")
    app = create_app()
    app.run_polling(drop_pending_updates=True)


def run_webhook() -> None:
    logger.info(
        f"Starting bot in WEBHOOK mode of port {PORT} with allowed user ids {ALLOWED_USER_IDS}"
    )
    app = create_app()
    url_path = f"bot/{uuid4()}"
    webhook_url = f"https://elsa-telegram-bot.herokuapp.com/{url_path}"
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=url_path,
        webhook_url=webhook_url,
        drop_pending_updates=True,
        secret_token=str(uuid4()),
    )
