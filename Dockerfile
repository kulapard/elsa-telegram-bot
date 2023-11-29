FROM python:3.12.0-slim-bullseye

WORKDIR /app

ENV PYTHONPATH=/app \
    PYTHONFAULTHANDLER=1 \
    # Keeps Python from buffering stdout and stderr to avoid situations where
    # the application crashes without emitting any logs due to buffering.
    PYTHONUNBUFFERED=1 \
    # Prevents Python from writing pyc files.
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DEFAULT_TIMEOUT=10 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user
ARG UID=10001
ARG APP_USER=appuser
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    ${APP_USER}

COPY requirements.txt requirements.txt
RUN BUILD_DEPS='build-essential' && \
    apt-get update &&  \
    apt-get install -y --no-install-recommends $BUILD_DEPS ffmpeg && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove $BUILD_DEPS && \
    rm -rf /var/lib/apt/lists/*

# Switch to the non-privileged user to run the application.
USER ${APP_USER}

# Copy the source code into the container.
ADD elsa_telegram_bot elsa_telegram_bot

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
CMD python elsa_telegram_bot/cli.py start-webhook
