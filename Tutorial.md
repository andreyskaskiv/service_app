<a name="top"></a>

### Tutorial

Create requirements.txt, .gitignore, Tutorial.md, .env

1. Create <a href="#dockerfile">Dockerfile</a>
2. Create <a href="#docker_compose">docker-compose</a>
3. Create <a href="#postgres">Postgres/a>

---

### 1. Create Dockerfile: <a name="dockerfile"></a>

[python:3.9-alpine3.16](https://hub.docker.com/_/python)

```dockerfile
COPY service /service  # копируем service в корень докерконтейнера под тем же названием /service 

FROM python:3.9-alpine3.16  # базовый image на основе которого мы создадим свой image

COPY requirements.txt /temp/requirements.txt  # файл requirements.txt копируем в /temp/requirements.txt
WORKDIR /service  # все команды будут запускаться вот из этой директории  
EXPOSE 8000  # внутри докерконтейнера пробрасываем порт наружу 

RUN pip install -r /temp/requirements.txt

RUN adduser --disabled-password service-user  # создадим пользователя service-user в операционной системе, пароль отключен 

   USER service-user  # service-user под этим пользователем будем запускать все команды 


```

---

### 2. Create docker-compose: <a name="docker_compose"></a>

Перечисляем какие сервисы будут запускаться докеркомпозом

```dockerfile
services:
  web-app:  # название нашего сервиса
    build:  # перечисляем с помощью чего мы его билдим 
      context: .  # это путь к тому место, где находится докерфайл 
    ports:  # какие порты будут проброшены 8000 порт докерконтейнера : сооответствует 8000 порту нашей ОС
      - "8000:8000"
    volumes:  # подключеные тома 
      - ./service:/service  # локальная папка ./service подключается к нашему докерконтейнеру /service 

    user: "${UID}:${GID}"   # так как при создании выскакивало Permission denied: '/service/manage.py'
    command: >   # команда для запуска нашего приложения 
      sh -c "python manage.py runserver 0.0.0.0:8000"

```

UID (User ID) - это идентификатор пользователя внутри контейнера,  
а GID (Group ID) - идентификатор группы. Если они не установлены,  
то обычно используется значение по умолчанию, которое соответствует  
пользователю и группе root.

```
cd PycharmProjects/Django_optimization/service_app
```

```
docker-compose run --rm web-app sh -c "django-admin startproject service ."
```

```
docker-compose build
```

```
docker-compose up
```

---

### 3. Create Postgres: <a name="postgres"></a>

[postgres:14.6-alpine](https://hub.docker.com/_/postgres)

1. docker-compose.yml

    ```dockerfile
    services:
      web-app:
        .....
          
        environment:
          - DB_HOST=database  # вот тут указываем ссылку на другой сервис докеркомпоза
          - DB_NAME=dbname
          - DB_USER=dbuser
          - DB_PASS=pass
    
        .....
    
        depends_on:  эта директива означает что мы не должны запускать web-app раньше, чем мы запустили сервис database
          - database
    
      database:
       image: postgres:14.6-alpine
       environment:  # конфигурируем пользователя и при билде он сам создастся
         - POSTGRES_DB=dbname
         - POSTGRES_USER=dbuser
         - POSTGRES_PASSWORD=pass
    
    ```
2. settings.py

    ```
    import os
    
    ...
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': os.environ.get('DB_HOST'),
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASS'),
        }
    }
    ```

3. Dockerfile
   ```dockerfile
   ...
   RUN apk add postgresql-client build-base postgresql-dev
   ...
   ```

4. build, migrate, createsuperuser
   ```
   docker-compose build
   ```
   ```
   docker-compose run --rm web-app sh -c "python manage.py migrate"
   ```
   ```
   docker-compose run --rm web-app sh -c "python manage.py createsuperuser"
   ```

   ```
   docker-compose up
   ```

Если возникает ошибка в отсутствие psycopg2, копирования кода нужно поставить после скачивания пакетов requirements

   ```dockerfile
   COPY requirements.txt /temp/requirements.txt
   COPY service /service
   ```

---




<a href="#top">UP</a>