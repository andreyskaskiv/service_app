from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Prefetch
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from clients.models import Client
from services.models import Subscription, Service, Plan
from services.serializers import SubscriptionSerializer


class ServicesApiTestCase(APITestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username='test_username_1',
                                          email="andrey@gmail.com")
        self.user_2 = User.objects.create(username='test_username_2')

        self.client_1 = Client.objects.create(user=self.user_1,
                                              company_name='company_name_test_1',
                                              full_address='full_address_test_1')
        self.client_2 = Client.objects.create(user=self.user_2,
                                              company_name='company_name_test_2',
                                              full_address='full_address_test_2')

        self.service_1 = Service.objects.create(name='Tech_Support_test_1',
                                                full_price=250)

        self.plan_1 = Plan.objects.create(plan_type='Full',
                                          discount_percent=0)
        self.plan_2 = Plan.objects.create(plan_type='Discount',
                                          discount_percent=20)

        Subscription.objects.create(client=self.client_1,
                                    service=self.service_1,
                                    plan=self.plan_1)
        Subscription.objects.create(client=self.client_2,
                                    service=self.service_1,
                                    plan=self.plan_2)

    def test_01_get(self):
        """Testing optimization with prefetch_related and select_related"""
        url = reverse('subscription-list')
        # self.client.force_login(self.user_1)  # add this line to log in the user and refresh the page

        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)
            # print(f"len =====>>>>> {len(queries)}")
            # print(f"list =====>>>>> {list(queries)}")
            self.assertEqual(3, len(queries))

        queryset = Subscription.objects.all().prefetch_related(
            'plan',
            Prefetch('client',
                     queryset=Client.objects.all().select_related('user').only('company_name',
                                                                               'user__email'))
        )
        serializer_data = SubscriptionSerializer(queryset, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data[0]['plan']['plan_type'], 'Full')
