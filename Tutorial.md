<a name="top"></a>

### Tutorial

Create requirements.txt, .gitignore, Tutorial.md, .env

1. Create <a href="#dockerfile">Dockerfile</a>
2. Create <a href="#docker_compose">docker-compose</a>

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

<a href="#top">UP</a>