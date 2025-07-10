#Запуск контейнеров
docker-compose -f docker-compose-prod.yml --env-file .env up -d --build
docker-compose -f docker-compose-dev.yml --env-file .env.dev up -d --build

#Записить миграции в контейнере web
python manage.py migrate