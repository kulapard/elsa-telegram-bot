import json
import os

from google.cloud import texttospeech as tts
from google.oauth2.service_account import Credentials


def _load_google_cloud_credentials() -> Credentials:
    """Loads Google Cloud credentials from environment variable."""
    json_str = os.getenv("GOOGLE_CREDENTIALS")
    if not json_str:
        raise RuntimeError("GOOGLE_CREDENTIALS env variable is not set")

    try:
        json_data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise RuntimeError("GOOGLE_CREDENTIALS env variable is not valid JSON") from e

    # private_key needs to replace \n parsed as string literal with escaped newlines
    json_data["private_key"] = json_data["private_key"].replace("\\n", "\n")

    return Credentials.from_service_account_info(json_data)


google_cloud_credentials = _load_google_cloud_credentials()
tts_client = tts.TextToSpeechClient(credentials=google_cloud_credentials)
