from django.contrib.auth.models import User
from django.db.models import Prefetch, F
from django.test import TestCase

from clients.models import Client
from services.models import Subscription, Service, Plan
from services.serializers import SubscriptionSerializer


class ServicesSerializerTestCase(TestCase):
    def test_ok(self):
        self.user_1 = User.objects.create(username='test_username_1',
                                          email="andrey@gmail.com")
        self.user_2 = User.objects.create(username='test_username_2',
                                          email="samsung@gmail.com")
        self.user_3 = User.objects.create(username='test_username_3',
                                          email="galaxy@gmail.com")

        self.client_1 = Client.objects.create(user=self.user_1,
                                              company_name='company_name_test_1',
                                              full_address='full_address_test_1')
        self.client_2 = Client.objects.create(user=self.user_2,
                                              company_name='company_name_test_2',
                                              full_address='full_address_test_2')
        self.client_3 = Client.objects.create(user=self.user_3,
                                              company_name='company_name_test_3',
                                              full_address='full_address_test_3')

        self.service_1 = Service.objects.create(name='Tech_Support_test_1',
                                                full_price=250)

        self.plan_1 = Plan.objects.create(plan_type='Full',
                                          discount_percent=0)
        self.plan_2 = Plan.objects.create(plan_type='Discount',
                                          discount_percent=20)
        self.plan_3 = Plan.objects.create(plan_type='Student',
                                          discount_percent=40)

        Subscription.objects.create(client=self.client_1,
                                    service=self.service_1,
                                    plan=self.plan_1,
                                    price=0)
        Subscription.objects.create(client=self.client_2,
                                    service=self.service_1,
                                    plan=self.plan_2,
                                    price=0)
        Subscription.objects.create(client=self.client_3,
                                    service=self.service_1,
                                    plan=self.plan_3,
                                    price=0)

        queryset = Subscription.objects.all().prefetch_related(
            'plan',
            Prefetch('client',
                     queryset=Client.objects.all().select_related('user').only('company_name',
                                                                               'user__email'))
        )
        data = SubscriptionSerializer(queryset, many=True).data
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
                "price": 0
            },
            {
                "id": self.client_2.id,
                "plan_id": self.plan_2.id,
                "client_name": "company_name_test_2",
                "email": "samsung@gmail.com",
                "plan": {
                    "id": self.plan_2.id,
                    "plan_type": "Discount",
                    "discount_percent": 20
                },
                "price": 0
            },
            {
                "id": self.client_3.id,
                "plan_id": self.plan_3.id,
                "client_name": "company_name_test_3",
                "email": "galaxy@gmail.com",
                "plan": {
                    "id": self.plan_3.id,
                    "plan_type": "Student",
                    "discount_percent": 40
                },
                "price": 0
            }
        ]

        # print('=============================================================')
        # print(f"data => {data}")
        # print('=============================================================')
        # print(f"expected_data => {expected_data}")

        self.assertEqual(expected_data, data)
