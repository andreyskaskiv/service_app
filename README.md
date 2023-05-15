# service_app, Django optimization

- Django
- djangorestframework
- Docker
- Postgres
- Celery
- Redis
- Django-cachalot

Run:

1. cd ...../service_app
2. docker-compose build
3. docker-compose run --rm web-app sh -c "python manage.py migrate"
4. docker-compose run --rm web-app sh -c "python manage.py createsuperuser"
5. docker-compose up

- http://127.0.0.1:8000/admin
- http://127.0.0.1:8000/api/subscriptions/?format=json
