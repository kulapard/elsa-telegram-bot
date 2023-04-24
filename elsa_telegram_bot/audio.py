from pathlib import PurePath

from dotenv import load_dotenv
from loguru import logger
from pydub import AudioSegment

load_dotenv() # take environment variables from .env.

import openai

from elsa_telegram_bot.chat import OPENAI_API_TOKEN


OGG_EXTENSION = ".oga"
WAV_EXTENSION = ".wav"
MP3_EXTENSION = ".mp3"


# Convert OGG to MP3
async def convert_ogg_to_mp3(ogg_file: PurePath, mp3_file: PurePath):
    logger.info(f"Converting {ogg_file} to {mp3_file}")
    audio = AudioSegment.from_ogg(ogg_file)
    audio.export(mp3_file, format="mp3")


async def transcribe_audio(audio_file: PurePath) -> str:
    wav_file_name = audio_file.name.replace(OGG_EXTENSION, MP3_EXTENSION)
    wav_file = audio_file.parent / wav_file_name
    await convert_ogg_to_mp3(audio_file, wav_file)
    audio_file = wav_file

    logger.info(f"Transcribing {audio_file}")
    with open(audio_file, "rb") as f:
        result = await openai.Audio.atranscribe(file=f, model="whisper-1", openai_api_key=OPENAI_API_TOKEN)
    logger.info(result)
    return result["text"]
