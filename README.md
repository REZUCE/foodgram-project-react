# Домен: https://foodgramlisicyn.ddns.net/
# Админка: 
Пароль: a
Логин: admin@admin.ru
# Foodgram
### Cоциальная сеть для обмена рецептами.
## Стек
- Django==4.2.4
- djangorestframework==3.14.0
- djoser==2.2.0
- webcolors==1.13
- psycopg2-binary==2.9.3
- Pillow==10.0.0
- python-dotenv==1.0.0
- psycopg2-binary==2.9.7
- gunicorn==21.2.0
## Установка запуск
1. Клонирование кода приложения с GitHub.
   ```
   git clone SSH-ссылка
   ```
2. Создать файл `.env` в котором перечислены все переменные окружения <В ГЛАВНОЙ ДИРЕКТОРИИ>.
   ```
    # Переменные для PostgreSQL
    POSTGRES_USER=<логин>
    POSTGRES_PASSWORD=<пароль>
    POSTGRES_DB=<название базы данных>
    # Переменные для Django-проекта:
    DB_HOST=db
    DB_PORT=5432
    SECRET_KEY=<здесь ключ Django>
    DEBUG_VALUE=False
    USE_TZ=True
    ALLOWED_HOSTS=<здесь хост>
    CSRF_TRUSTED_ORIGINS
   ```
2. Поочерёдно выполнить на сервере команды для установки Docker и Docker Compose для Linux.
   ```
    sudo apt update
    sudo apt install curl
    curl -fSL https://get.docker.com -o get-docker.sh
    sudo sh ./get-docker.sh
    sudo apt-get install docker-compose-plugin
   ```
4. Зайти в директорию infra и там запустить Docker Compose.
   ```
    sudo docker compose up -d
   ```
5. Проверить запустились ли все наши контейнеры.
   ```
    sudo docker compose -f docker-compose.production.yml ps
   ```
5. Собрать статику, применить миграции и создать админа.
   ```
     sudo docker compose -f docker-compose.yml exec infra_backend_1 python manage.py migrate
     sudo docker compose -f docker-compose.yml exec infra_backend_1 python manage.py collectstatic
     sudo docker compose -f docker-compose.yml exec infra_backend_1 python manage.py createsuperuser
   ```
   Если так не выполняется команда сверху:
   ```
     # Получаем все контейнеры и взять id контейнера, который связан с backend.
     sudo docker ps
     # Зайти в контейнер и там собрать статику.
     sudo docker exec -ti <id контейнера> /bin/bash
     # Применить миграции.
     python3 manage.py migrate
     # Собрать статику.
     python3 manage.py collectstatic
     # Создать админа.
     python3 manage.py createsuperuser
     # Выйти из контейнера.
     exit
   ```
6. Зайти через админку в модель Ingredient и залить туда csv с данными ингредиентов.
   Пример csv:
   ```
   name,measurement_unit
    абрикосовое варенье,г
    абрикосовое пюре,г
    абрикосовый джем,г
    абрикосовый сок,стакан
    абрикосы,г
   ```
## Автор
Владимир Лисицын 
telegram: @LisicynV
