![foodgram_workflow](https://github.com/KrisNovi/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
### Описание пректа
Проект собирает отзывы пользователей на произведения. Сами произведения в проекте не хранятся,
здесь нельзя посмотреть фильм или послушать музыку.
Посмотреть пример развернутого проекта можно тут:
http://51.250.65.210/
Админ: 
log: nko
pass: nko
email: test@mail.ru
### Технологии
См. requirements.txt
### Репозиторий
https://github.com/KrisNovi/foodgram-project-react

### Для запуска приложения в контейнерах
- клонировать проект из репозитория на github (ссылка выше)
```
git clone git@github.com:KrisNovi/foodgram-project-react.git
```
- в директории /infra создать файл .env и прописать там следующие переменные окружения:
```
- DB_ENGINE # указываем БД, с которой работаем
- DB_NAME # имя БД
- POSTGRES_USER=postgres # логин для подключения к базе данных
- POSTGRES_PASSWORD # пароль для подключения к БД (установите свой)
- DB_HOST # название сервиса (контейнера)
- DB_PORT # номер порта
```
- из директории /infra смонтировать и запустить контейнеры:
```
docker-compose up -d --build
``` 
- выполнить миграции внутри запущенного контейнера web:
```
docker-compose exec web python manage.py migrate
```
- создать суперпользователя:
```
docker-compose exec web python manage.py createsuperuser
```
- собрать статику:
```
docker-compose exec web python manage.py collectstatic --no-input
```
### Заполнение базы из .csv файлов
Для заполнения базы данных ингредиентами (более 2000 наименований) и тэгами необходимо выполнить следующие команды:
```
docker-compose exec web python manage.py import_ingred
docker-compose exec web python manage.py import_tags
```
### Создание резервной копии базы данных
```
docker-compose exec web python manage.py dumpdata > fixtures.json
```

