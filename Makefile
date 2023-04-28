APP_NAME=elsa-telegram-bot
APP_DIR=elsa_telegram_bot

release-web:
	docker buildx build --platform linux/amd64 -t ${APP_NAME}-web .
	docker tag ${APP_NAME}-web registry.heroku.com/${APP_NAME}/web
	docker push registry.heroku.com/${APP_NAME}/web
	heroku container:release web --app ${APP_NAME}

logs:
	heroku logs --tail -a ${APP_NAME}

pre-commit:
	pre-commit run --all-files

mypy:
	mypy ${APP_DIR}

lint: pre-commit mypy

run:
	docker compose up --build
