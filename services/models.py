from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=16, choices=[
        ('admin', 'Admin'),
        ('reviewer', 'Reviewer'),
        ('applicant', 'Applicant'),
    ])
    applicant_type = models.CharField(max_length=16, choices=[
        ('company', 'Company'),
        ('individual', 'Individual'),
    ], null=True, blank=True)

    def clean(self):
        # if user chooses applicant, applicant_type must be set
        if self.role == "applicant" and not self.applicant_type:
            raise ValidationError("Applicant type is required when role is Applicant.")

        # if user is not applicant, applicant_type must be empty
        if self.role != "applicant" and self.applicant_type:
            raise ValidationError("Applicant type should only be set if role is Applicant.")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username


class Service(models.Model):
    class Type(models.TextChoices):
        ISSUE = "issue"
        LICENSE = "license"

    class Status(models.TextChoices):
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED = "rejected"
        REVIEWING = "reviewing"

    class Market(models.TextChoices):
        INSURANCE = "insurance"
        MORTGAGE = "mortgage"
        CMA = "CMA"

    market = models.CharField(choices=Market.choices)
    type = models.CharField(choices=Type.choices)
    status = models.CharField(choices=Status.choices, default=Status.PENDING)
    fixed = models.BooleanField(null=True, blank=True)
    applicant = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
    fee = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Payment(models.Model):
    amount = models.IntegerField()
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)