<a name="top"></a>

### Tutorial

Create requirements.txt, .gitignore, Tutorial.md, .env

1. Create <a href="#dockerfile">Dockerfile</a>
2. Create <a href="#docker_compose">docker-compose</a>
3. Create <a href="#postgres">Postgres</a>
4. Create app <a href="#clients">clients</a>
5. Create app <a href="#services">services</a>
6. ORM query <a href="#optimization">optimization</a>
7. Annotate and Aggregate in <a href="#orm">ORM</a>
8. <a href="#celery">Celery</a>
9. Create celery <a href="#tasks">tasks</a>
10. Create celery <a href="#worker">worker2</a>

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

### 4. Create app clients: <a name="clients"></a>

1. Create app
   ```
   cd PycharmProjects/Django_optimization/service_app
   ```

   ```
   docker-compose run --rm web-app sh -c "django-admin startapp clients"
   ```
2. Registration app
   ```
   service -> settings.py
   
   INSTALLED_APPS = [
      ....
    'clients',
      ....
   ]
   ```
3. Create models:
   ```
   clients -> models.py
   
   Client
   ```

   ```
   docker-compose run --rm web-app sh -c "python manage.py makemigrations"
   docker-compose run --rm web-app sh -c "python manage.py migrate"
   ``` 
4. Registration in admin panel:
   ```
   clients -> admin.py
   
   admin.site.register(Client)
   ```

---

### 5. Create app services: <a name="services"></a>

1. Create app
   ```
   cd PycharmProjects/Django_optimization/service_app
   ```

   ```
   docker-compose run --rm web-app sh -c "django-admin startapp services"
   ```
2. Registration app
   ```
   service -> settings.py
   
   INSTALLED_APPS = [
      ....
    'services',
      ....
   ]
   ```
3. Create models:
   ```
   services -> models.py
   
   class Service(models.Model):
   ...
   
   class Plan(models.Model):
   ...
   
   class Subscription(models.Model):
   ...
   
   ```

   ```text
   client = models.ForeignKey(Client, related_name='subscriptions', on_delete=models.PROTECT)
   related_name - это то, с каким именем будет доступна создаваемая модель с которой мы образуем связь(Client).
   Чтобы показать подписки клиента - Client.subscriptions.all() или Subscription.filter(client=client_id).all()
   ```

   ```
   docker-compose run --rm web-app sh -c "python manage.py makemigrations"
   docker-compose run --rm web-app sh -c "python manage.py migrate"
   ``` 

4. Registration in admin panel:
   ```
   services -> admin.py
   
   admin.site.register(Service)
   admin.site.register(Plan)
   admin.site.register(Subscription)
   ```

5. create multiple subdisks:
   ```
   docker-compose up
   ```

   [go to admin panel](http://127.0.0.1:8000/admin/)

6. Create serializers:
   ```
   services -> serializers.py
   
   SubscriptionSerializer
   ```

7. Create Views:
   ```
   services -> views.py 
   
   class SubscriptionView(ReadOnlyModelViewSet)
   ```
8. Add the URLs:
   ```
   service -> urls.py added urlpatterns

   from rest_framework import routers
   
   from services.views import SubscriptionView
   ...
   router = routers.DefaultRouter()
   router.register(r'api/subscriptions', SubscriptionView)
   
   urlpatterns += router.urls
   ```

   [&#8658; test serializers ](http://127.0.0.1:8000/api/subscriptions/?format=json)
   ```json
   [
   {
   "id": 1,
   "plan_id": 3,
   "client_name": "Company First",
   "email": "andrey@gmail.com"
   }
   ]
   ```

---

### 6. ORM query optimization: <a name="optimization"></a>

* Проверить, какие существуют N+1 запросы.
* Определить, какие поля нам реально нужно брать из базы, убрать все лишнее.
* В Unit-test можно сразу закрепить сколько данный api-endpoint делает запросов.
* Запросы с JOIN-ами тяжелея, чем обычные, но предпочтительней чем N+1.
* Возможно, стоит пересмотреть и сами модели, которые мы создаем в ДБ.

Разница между select_related и prefetch_related что один для one to one, второй one to many.

1. Added LOGGING:
   ```
   service -> settings.py
   
   LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'}
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG' # here we choose what we will log
        }
    }
   }
   ```
2. Run docker and api:
   ```
   cd PycharmProjects/Django_optimization/service_app
   ```

   ```
   docker-compose up
   ```

   [&#8658; json ](http://127.0.0.1:8000/api/subscriptions/?format=json)
3. views refactoring:

   ```text
   Смысл prefetch_related - для всех подписок вытащить одним разом всех клиентов
   При получении каждой подписки мы должны вытащить Client чтоб у него потом взять company_name.  
   email - это то же самое, но еще глубже Client -> user -> email
   
   `.prefetch_related('client').prefetch_related('client__user')` - при таком запросе мы решаем проблему
   N+1, но мы достаем все поля, а нам надо только необходимые. Для этого воспользуемся классом Prefetch.
   И в классе Prefetch мы можем указать конкретные поля (only('company_name', 'user__email')) из конкретной модели ('client'). 
   ```

   ```
   services -> views.py 
   
   class SubscriptionView(ReadOnlyModelViewSet):
       queryset = Subscription.objects.all().prefetch_related(
           Prefetch('client',
                    queryset=Client.objects.all().select_related('user').only('company_name',
                                                                              'user__email'))
       )
       serializer_class = SubscriptionSerializer
   ```

4. Added PlanSerializer:
   ```
   services -> serializers.py
   
   class PlanSerializer(serializers.ModelSerializer)
   ```

   ```
   PlanSerializer
   ...
   SubscriptionSerializer(serializers.ModelSerializer)
   plan = PlanSerializer()
   
      fields = (...., 'plan')
   ```

5. views refactoring::
   ```
   services -> views.py 
   
   class SubscriptionView(ReadOnlyModelViewSet):
      queryset = Subscription.objects.all().prefetch_related(
         'plan',
         Prefetch('client',
      queryset=Client.objects.all().select_related('user').only('company_name',
                                                            'user__email'))
      )
      serializer_class = SubscriptionSerializer
   ```

6. Create test_api:  
   Testing optimization with prefetch_related and select_related

   ```
   services/tests -> test_api.py
    
   class ServicesApiTestCase(TestCase):
      ...
   ```

   ```
   docker-compose run --rm web-app sh -c "python manage.py test"
   ```

7. Create test_serializers:

   ```
   services/tests -> test_serializers.py
    
   class ServicesSerializerTestCase(TestCase):
      ...
   ```

   ```
   docker-compose run --rm web-app sh -c "python manage.py test"
   ```

---

### 7. Annotate and Aggregate in ORM: <a name="orm"></a>

1. Added get_price:  
   Данную логику можно реализовать и в модели, но для примера реализуем в сериализаторе.
   instance в функции get_price - это конкретная модель подписки. API-endpoint у нас создает все подписки,
   а функция запускается для каждой подписки. instance == subscription.
   Данный способ создает проблему N+1, можно решить это и с помощью "Prefetch",
   но мы решим это на уровне базы в следующем пункте.

   ```
   services -> serializers.py
   
   class SubscriptionSerializer(serializers.ModelSerializer):
      ...
      price = serializers.SerializerMethodField()
      
      def get_price(self, instance):
        return (instance.service.full_price -
                instance.service.full_price * (instance.plan.discount_percent / 100))
   
   
      fields = (...., 'price')
   ```

   ```json
   [
     {
       "id": 1,
       "plan_id": 3,
       "client_name": "Company First",
       "email": "andrey@gmail.com",
       "plan": {
         "id": 3,
         "plan_type": "discount",
         "discount_percent": 5
       },
       "price": 237.5
     },
     {
       "id": 2,
       "plan_id": 2,
       "client_name": "Company Second",
       "email": "Test_users@mail.com",
       "plan": {
         "id": 2,
         "plan_type": "student",
         "discount_percent": 20
       },
       "price": 200
     }
   ]
   
   ```

2. Annotate:

   annotate - каждую из выдаваемых subscription он будет чем-то дополнять, как-то анотировать.
   Добавиться вируальное поле price.

   ```
   services -> views.py 
   
   class SubscriptionView(ReadOnlyModelViewSet):
      queryset = Subscription.objects.all().prefetch_related(
        'plan',
        Prefetch('client',
        queryset=Client.objects.all().select_related('user').only('company_name',
                                                               'user__email'))
        ).annotate(price=F('service__full_price') -
                         F('service__full_price') * F('plan__discount_percent') / 100.00)
    serializer_class = SubscriptionSerializer
   ```

3. serializers refactoring:

   ```
   services -> serializers.py 
   
   class SubscriptionSerializer(serializers.ModelSerializer):
      ...
      
      def get_price(self, instance):
         return instance.price
   ```

   ```json
   [
     {
       "id": 1,
       "plan_id": 3,
       "client_name": "Company First",
       "email": "andrey@gmail.com",
       "plan": {
         "id": 3,
         "plan_type": "discount",
         "discount_percent": 5
       },
       "price": 237.5
     },
     {
       "id": 2,
       "plan_id": 2,
       "client_name": "Company Second",
       "email": "Test_users@mail.com",
       "plan": {
         "id": 2,
         "plan_type": "student",
         "discount_percent": 20
       },
       "price": 200
     }
   ]
   
   ```

4. test_api refactoring:

   ```
   services/tests -> test_api.py
    
   class ServicesApiTestCase(TestCase):
      ...
   
      queryset = Subscription.objects.all().prefetch_related(
            'plan',
            Prefetch('client',
                     queryset=Client.objects.all().select_related('user').only('company_name',
                                                                               'user__email'))
        ).annotate(price=F('service__full_price') -
                         F('service__full_price') * F('plan__discount_percent') / 100.00)
   ```

   ```
   docker-compose run --rm web-app sh -c "python manage.py test"
   ```

5. test_serializers refactoring:

   ```
   services/tests -> test_serializers.py
    
   class ServicesSerializerTestCase(TestCase):
      ...
   
      queryset = Subscription.objects.all().prefetch_related(
            'plan',
            Prefetch('client',
                     queryset=Client.objects.all().select_related('user').only('company_name',
                                                                               'user__email'))
        ).annotate(price=F('service__full_price') -
                         F('service__full_price') * F('plan__discount_percent') / 100.00)
   
       expected_data = [
            {
                "id": self.client_1.id,
                "plan_id": self.plan_1.id,
                "client_name": "company_name_test_1",
                "email": "andrey@gmail.com",
                "plan": {
                    "id": self.plan_1.id,
                    "plan_type": "Full",
                    "discount_percent": 0
                },
                "price": 250
            },
            ...
        ]
   ```

   ```
   docker-compose run --rm web-app sh -c "python manage.py test"
   ```

6. Aggregate:  
   Api 2.0

   "queryset.aggregate(total=Sum('price')).get('total')" сработал, так как мы в annotate создали виртуальное
   поле price.

   В функции list(self, request, *args, **kwargs) обрабатывается запрос и формируется ответ нашему клиенту

   ```
   services -> views.py 
   
   class SubscriptionView(ReadOnlyModelViewSet):
      ...
      def list(self, request, *args, **kwargs):
         queryset = self.filter_queryset(self.get_queryset())
         response = super().list(request, *args, **kwargs)
         
         response_data = {'result': response.data}
         response_data['total_amount'] = queryset.aggregate(total=Sum('price')).get('total')
         response.data = response_data
         
         return response
   ```

   ```json
   {
     "result": [
       {
         "id": 1,
         "plan_id": 3,
         "client_name": "Company First",
         "email": "andrey@gmail.com",
         "plan": {
           "id": 3,
           "plan_type": "discount",
           "discount_percent": 5
         },
         "price": 237.5
       },
       {
         "id": 2,
         "plan_id": 2,
         "client_name": "Company Second",
         "email": "Test_users@mail.com",
         "plan": {
           "id": 2,
           "plan_type": "student",
           "discount_percent": 20
         },
         "price": 200
       }
     ],
     "total_amount": 437.5
   }
   ```

7. test_api refactoring:  
   Aggregate добавляет еще один запрос в базу

   ```
   class ServicesApiTestCase(APITestCase):
       def test_01_get(self):
           ...
   
           with CaptureQueriesContext(connection) as queries:
                ...
               self.assertEqual(4, len(queries))
   
      ...
      self.assertEqual(serializer_data, response.data['result'])
   ```

   ```
   docker-compose run --rm web-app sh -c "python manage.py test"
   ```

---

### 8. Celery: <a name="celery"></a>

1. docker-compose.yml refactoring:
   fix bag:

   ```dockerfile
   services:
      web-app:
      ....
      
      redis:
       image: redis:7.0.5-alpine
       hostname: redis
      
      worker:
       build:
         context: .
       hostname: worker
       entrypoint: celery
       command: -A celery_app.app worker --loglevel=info
       volumes:
         - ./service:/service
       links:
         - redis
       depends_on:
         - redis
         - database
       environment:
         - DB_HOST=database
         - DB_NAME=dbname
         - DB_USER=dbuser
         - DB_PASS=pass
   
      ```

2. Create celery_app.py
3. Create __init__.py:
   fix bag:
   Path: service/service/__init__.py

   ```python
   from .celery_app import app as celery_app
   
   __all__ = ('celery_app',)
   
   ```
4. settings.py refactoring:
   ```
   service -> settings.py
   
   ....
   
   CELERY_BROKER_URL = 'redis://redis:6379/0'
   ```

5. Run
   ```
   cd PycharmProjects/Django_optimization/service_app
   ```

   ```
   docker-compose build
   ```

   ```
   docker-compose up
   ```

6. Test
   ```
   docker-compose run --rm web-app sh -c "python manage.py shell"
   ```

   ```pycon
   >>> from celery_app import debug_task
   >>> debug_task()
   Hello form debug_task
   
   >>> debug_task.delay()
   <AsyncResult: 2cbc3698-be65-4edb-8a57-93fabb880dd9>
   
   ```

7. docker-compose.yml refactoring:

   ```dockerfile
   services:
      web-app:
      ....
      
      flower:
          build:
            context: .
          hostname: flower
          entrypoint: celery
          command: -A celery_app.app flower
          volumes:
            - ./service:/service
          links:
            - redis
          depends_on:
            - redis
          ports:
            - "5555:5555"
   
   ```

   ```
   docker-compose build
   ```

   ```
   docker-compose up
   ```

   [flower](http://127.0.0.1:5555/)

---

### 9. Create celery tasks: <a name="tasks"></a>

1. Run:
   ```
   cd PycharmProjects/Django_optimization/service_app
   ```
   ```
   docker-compose up
   ```
   New Tab:
   ```
   docker-compose run --rm web-app sh -c "python manage.py test"
   ```

   [&#8658; flower ](http://127.0.0.1:5555/)  
   [&#8658; json ](http://127.0.0.1:8000/api/subscriptions/?format=json)

2. views refactoring:

   delete annotate

   ```
   services -> views.py 
   
   class SubscriptionView(ReadOnlyModelViewSet):
      queryset = Subscription.objects.all().prefetch_related(
        'plan',
        Prefetch('client',
                 queryset=Client.objects.all().select_related('user').only('company_name',
                                                                           'user__email'))
      )
      serializer_class = SubscriptionSerializer
   ```

3. models refactoring:
   ```
   services -> models.py

   class Subscription(models.Model):
      ...
   
      price = models.PositiveIntegerField(default=0)
   ...

   ```
   docker-compose run --rm web-app sh -c "python manage.py makemigrations"
   docker-compose run --rm web-app sh -c "python manage.py migrate"
   ``` 

4. Create tasks.py
   ```
   services -> tasks.py

   @shared_task
   def set_price(subscription_id):
      ...
   
   ```

5. models refactoring:
   ```
   services -> models.py
   
   class Service(models.Model):
   
      ...
   
       def __init__(self, *args, **kwargs):
           super().__init__(*args, **kwargs)
           self.__full_price = self.full_price
   
       def save(self, *args, **kwargs):
   
           if self.full_price != self.__full_price:
               for subscription in self.subscriptions.all():
                   set_price.delay(subscription.id)
   
           return super().save(*args, **kwargs)
   ```

   ```
   services -> models.py
   
   class Plan(models.Model):
   
      ...
   
       def __init__(self, *args, **kwargs):
           super().__init__(*args, **kwargs)
           self.__full_price = self.full_price
   
       def save(self, *args, **kwargs):
   
           if self.full_price != self.__full_price:
               for subscription in self.subscriptions.all():
                   set_price.delay(subscription.id)
   
           return super().save(*args, **kwargs)
   ```

6. Added celery_singleton:

   ```
   services -> tasks.py

   @shared_task(base=Singleton)
   def set_price(subscription_id):
      ...
   
   ```

   ```
   docker-compose build
   ```

   ```
   docker-compose up
   ```
7. test_api refactoring:   
   delete annotate and added "price=0"

8. test_serializers refactoring:   
   delete annotate and added "price=0"

   ```text
   Решить проблему с пересчетом price в тестах.
   ```

---

### 10. Create celery worker2: <a name="worker2"></a>

1. docker-compose.yml refactoring:

   ```dockerfile
   services:
      web-app:
      ....
   
     worker2:
       build:
         context: .
       hostname: worker2
       entrypoint: celery
       command: -A celery_app.app worker --loglevel=info
       volumes:
         - ./service:/service
       links:
         - redis
       depends_on:
         - redis
         - database
       environment:
         - DB_HOST=database
         - DB_NAME=dbname
         - DB_USER=dbuser
         - DB_PASS=pass
      
   ```
   ```
   cd PycharmProjects/Django_optimization/service_app
   ```
   ```
   docker-compose build
   ```

   ```
   docker-compose up
   ```

2. models refactoring:

   ```text
   Let's create another minor field in the model
   ```
   ```
   services -> models.py

   class Subscription(models.Model):
      ...
   
      comment = models.CharField(max_length=50, default='')
   ```

   ```
   services -> models.py

   class Service(models.Model):
      ...
   
       def save(self, *args, **kwargs):

            if self.full_price != self.full_price:
                for subscription in self.subscriptions.all():
                    ...
   
                    set_comment.delay(subscription.id)

            return super().save(*args, **kwargs)
   ```
   ```
   services -> models.py

   class Plan(models.Model):
      ...
   
       def save(self, *args, **kwargs):

            if self.discount_percent != self.__discount_percent:
                for subscription in self.subscriptions.all():
                    ...
   
                    set_comment.delay(subscription.id)

            return super().save(*args, **kwargs)
   ```

3. refactoring tasks.py
   ```
   services -> tasks.py

   @shared_task(base=Singleton)
   def set_comment(subscription_id):
      ...
   
   ```
   ```text
   with transaction.atomic():
   transaction - Это процедура в базе, которая будет происходит атомарно, то есть либо код выполнится
   полностью (все пункты), либо все это вместе не случится. Или все вместе, или не как. 
   atomic - означает, что это не может быть применено частично. 
   ```
   ```text
   Внутрь транзакции необходимо включать только такой код, который лочится внутри этой транзакции. После этого мы сразу 
   должны выходить из этой транзакции, чтоб дальнейший код мог отрабатывать параллельно. 
   ```

   ```
   services -> tasks.py

   @shared_task(base=Singleton)
   def set_price(subscription_id):
      ...
      with transaction.atomic():
      ....
   
   ```
   ```
   docker-compose run --rm web-app sh -c "python manage.py makemigrations"
   docker-compose run --rm web-app sh -c "python manage.py migrate"
   ``` 

<a href="#top">UP</a>