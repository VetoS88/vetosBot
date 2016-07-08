from __future__ import unicode_literals

from django.db import models


class User(models.Model):
    person_id = models.IntegerField()
    first_name = models.CharField(max_length=30, default="Anonymous")
    last_name = models.CharField(max_length=30)
    person_drink = models.OneToOneField('Drink', null=True)


class Drink(models.Model):
    person = models.OneToOneField(User)
    liquid = models.CharField(max_length=30)
    cup = models.CharField(max_length=30)
    sugar = models.CharField(max_length=30)
    is_drunk = models.BooleanField(default=True)
    is_ready = models.BooleanField(default=True)
