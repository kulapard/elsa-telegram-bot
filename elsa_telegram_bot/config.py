import os

OPENAI_API_TOKEN = os.getenv("OPENAI_API_TOKEN")
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

PORT = int(os.getenv("PORT", "8000"))
ALLOWED_USER_IDS = [
    int(uid.strip()) for uid in os.getenv("ALLOWED_USER_IDS", "").split(",") if uid
]
