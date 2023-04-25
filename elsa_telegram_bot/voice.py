from pathlib import Path

import openai
from config import OPENAI_API_TOKEN
from loguru import logger
from pydub import AudioSegment

OGG_EXTENSION = ".oga"
MP3_EXTENSION = ".mp3"

openai.api_key = OPENAI_API_TOKEN


async def convert_ogg_to_mp3(ogg_file: Path, mp3_file: Path):
    audio = AudioSegment.from_file_using_temporary_files(ogg_file, "ogg")
    audio.export(mp3_file, format="mp3")


async def transcribe_audio(mp3_file) -> str:
    logger.info(f"Transcribing {mp3_file}")
    with open(mp3_file.name, "rb") as f:
        result = await openai.Audio().atranscribe(file=f, model="whisper-1")
    logger.info(result)
    return result["text"]
