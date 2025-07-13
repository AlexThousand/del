# Запуск контейнеров
```bash
docker-compose -f docker-compose-prod.yml --env-file .env up -d --build
```
```bash
docker-compose -f docker-compose-dev.yml --env-file .env.dev up -d --build
```

# Записать миграции в контейнере web
```bash
python manage.py migrate
```
