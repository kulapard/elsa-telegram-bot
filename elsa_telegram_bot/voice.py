import openai
from aiofiles.threadpool.binary import AsyncBufferedReader
from loguru import logger
from pydub import AudioSegment

from elsa_telegram_bot.config import OPENAI_API_TOKEN

OGG_EXTENSION = ".oga"
MP3_EXTENSION = ".mp3"


async def convert_ogg_to_mp3(ogg_file: str, mp3_file: str):
    audio = AudioSegment.from_file_using_temporary_files(ogg_file, "ogg")
    audio.export(mp3_file, format="mp3")


async def transcribe_audio(mp3_file: AsyncBufferedReader) -> str:
    logger.info(f"Transcribing {mp3_file}")
    with open(mp3_file.name, "rb") as f:
        result = await openai.Audio.atranscribe(
            file=f, model="whisper-1", api_key=OPENAI_API_TOKEN
        )
    return result["text"]  # type: ignore[no-any-return]
