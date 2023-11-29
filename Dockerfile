FROM python:3.12.0-slim-bullseye

ENV PYTHONPATH=/app
WORKDIR /app

ADD requirements.txt requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -q -r requirements.txt

ADD . /app

CMD ["python", "elsa_telegram_bot/cli.py", "start-webhook"]
