FROM python:3.11.3-slim-bullseye

ADD requirements.txt /tmp/requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -q -r /tmp/requirements.txt

ENV PYTHONPATH=/app
ADD . /app
WORKDIR /app

CMD ["python", "elsa_telegram_bot/cli.py", "start-webhook"]
