import os

OPENAI_API_TOKEN = os.environ["OPENAI_API_TOKEN"]
TELEGRAM_API_TOKEN = os.environ["TELEGRAM_API_TOKEN"]

PORT = int(os.getenv("PORT", "8000"))
BASE_URL = os.environ["BASE_URL"]
ALLOWED_USER_IDS = [
    int(uid.strip()) for uid in os.getenv("ALLOWED_USER_IDS", "").split(",") if uid
]
ADMIN_USER_ID = int(os.environ["ADMIN_USER_ID"].strip())
