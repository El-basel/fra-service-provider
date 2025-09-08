from django.db import models
from django.conf import settings
from django.utils import timezone
from abc import ABC, abstractmethod

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=40)
    password = models.CharField(max_length=16)

    def dashboard(self):
        pass

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    class Meta:
        abstract = True


class Admin(User):
    def add_fees(self, service):
        pass

class Reviewer(User):
    def accept_service(self, service):
        pass
    def reject_service(self, service):
        pass

class Applicant(User):
    class Type(models.IntegerChoices):
        COMPANY = 1
        INDIVIDUAL = 2

    type = models.IntegerField(choices=Type.choices)
    def request_service(self):
        pass
    def cancel_service(self):
        pass
    def pay_service(self):
        pass

class Service(models.Model):
    class Type(models.TextChoices):
        ISSUE = "issue"
        LICENSE = "license"

    class Status(models.TextChoices):
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED = "rejected"

    class Market(models.TextChoices):
        INSURANCE = "insurance"
        MORTGAGE = "mortgage"
        CMA = "CMA"
    TYPES_CHOICES = ["issue", "license"]
    MARKET_CHOICES = ["insurance", "mortgage", "CMA"]
    STATUS_CHOICES = ["active", "inactive"]
    market = models.CharField(choices=Market.choices)
    type = models.CharField(choices=Type.choices)
    status = models.IntegerField(choices=Status.choices)
    fixed = models.BooleanField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Payment(models.Model):
    amount = models.IntegerField()
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(Applicant, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)