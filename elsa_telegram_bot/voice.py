import random
from functools import cache

import langdetect
import openai
from aiofiles.threadpool.binary import AsyncBufferedReader
from google.cloud import texttospeech
from loguru import logger
from pydub import AudioSegment

from elsa_telegram_bot.config import OPENAI_API_TOKEN

OGG_EXTENSION = ".oga"
MP3_EXTENSION = ".mp3"
DEFAULT_VOICE_NAME = "en-US-Wavenet-D"


async def convert_ogg_to_mp3(ogg_file: str, mp3_file: str):
    """Converts OGG file to MP3 file."""
    audio = AudioSegment.from_file_using_temporary_files(ogg_file, "ogg")
    audio.export(mp3_file, format="mp3")


async def transcribe_audio(mp3_file: AsyncBufferedReader) -> str:
    """Transcribes MP3 file to text."""
    logger.info(f"Transcribing {mp3_file}")
    with open(mp3_file.name, "rb") as f:
        result = await openai.Audio.atranscribe(
            file=f, model="whisper-1", api_key=OPENAI_API_TOKEN
        )
    return result["text"]  # type: ignore[no-any-return]


@cache
def list_voice_names(lang: str) -> list[str]:
    """Returns list of voice names for the language."""
    client = texttospeech.TextToSpeechClient()
    response = client.list_voices()
    voice_names = []
    for voice in response.voices:
        if lang in voice.language_codes[0] and voice.ssml_gender == 2:
            voice_names.append(voice.name)
    return voice_names


def get_voice_name(lang) -> str:
    """Returns random voice name for the language or default voice name if no voice names found."""
    voice_name = random.choice(list_voice_names(lang))
    voice_name = voice_name or DEFAULT_VOICE_NAME
    return voice_name


def get_lang_code(voice_name: str) -> str:
    """Returns language code from voice name.

    >>> get_lang_code("en-US-Wavenet-D")
    "en-US"
    """
    return "-".join(voice_name.split("-", maxsplit=2)[0:2])


async def text_to_speech(text: str, file_path: str) -> str:
    """Converts text to speech using Google Cloud Text-to-Speech."""
    lang = langdetect.detect(text)
    voice_name = get_voice_name(lang)
    lang_code = get_lang_code(voice_name)

    logger.info(
        f"Text to speech using lang code {lang_code!r} and {voice_name!r} voice name"
    )

    # Initialize the Text-to-Speech client
    client = texttospeech.TextToSpeechClient()

    # Configure the synthesis request
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(language_code=lang_code, name=voice_name)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.OGG_OPUS
    )

    # Perform the synthesis
    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    # Save the synthesized speech to an audio file
    with open(file_path, "wb") as out:
        out.write(response.audio_content)

    return voice_name
