APP=elsa-telegram-bot

release-web:
	docker buildx build --platform linux/amd64 -t ${APP}-web .
	docker tag ${APP}-web registry.heroku.com/${APP}/web
	docker push registry.heroku.com/${APP}/web
	heroku container:release web --app ${APP}

logs:
	heroku logs --tail
