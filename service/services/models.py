from django.core.validators import MaxValueValidator
from django.db import models

from clients.models import Client
from services.tasks import set_price, set_comment


class Service(models.Model):
    """This is what we sell. We sell subscriptions to some services."""
    name = models.CharField(max_length=50)
    full_price = models.PositiveIntegerField()

    def __str__(self):
        return f"Name Service: {self.name}, Full price: {self.full_price}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__full_price = self.full_price

    def save(self, *args, **kwargs):

        if self.full_price != self.__full_price:
            for subscription in self.subscriptions.all():
                set_price.delay(subscription.id)
                set_comment.delay(subscription.id)

        return super().save(*args, **kwargs)


class Plan(models.Model):
    """These are the tariff plans that we assign to the client."""
    PLAN_TYPES = (
        ('full', 'Full'),
        ('student', 'Student'),
        ('discount', 'Discount')
    )

    plan_type = models.CharField(choices=PLAN_TYPES, max_length=10)
    discount_percent = models.PositiveIntegerField(default=0,
                                                   validators=[
                                                       MaxValueValidator(100)
                                                   ])

    def __str__(self):
        return f"Plan: {self.plan_type}, Discount percent: {self.discount_percent}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__discount_percent = self.discount_percent

    def save(self, *args, **kwargs):

        if self.discount_percent != self.__discount_percent:
            for subscription in self.subscriptions.all():
                set_price.delay(subscription.id)
                set_comment.delay(subscription.id)

        return super().save(*args, **kwargs)


class Subscription(models.Model):
    """This is a client subscription based on the chosen plan.
     Subscription of some client to some service according to some tariff plan."""
    client = models.ForeignKey(Client, related_name='subscriptions', on_delete=models.PROTECT)
    service = models.ForeignKey(Service, related_name='subscriptions', on_delete=models.PROTECT)
    plan = models.ForeignKey(Plan, related_name='subscriptions', on_delete=models.PROTECT)
    price = models.PositiveIntegerField(default=0)
    comment = models.CharField(max_length=50, default='')

    def __str__(self):
        return f"{self.client}, {self.service}, {self.plan}"

    def save(self, *args, **kwargs):
        creating = not bool(self.id)
        result = super().save(*args, **kwargs)
        if creating:
            set_price.delay(self.id)
        return result
