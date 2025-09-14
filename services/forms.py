from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Service, Payment

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')


class SignupForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('reviewer', 'Reviewer'),
        ('applicant', 'Applicant'),
    ]

    APPLICANT_TYPE_CHOICES = [
        ('company', 'Company'),
        ('individual', 'Individual'),
    ]

    role = forms.ChoiceField(label='Role', choices=ROLE_CHOICES)
    applicant_type = forms.ChoiceField(
        label='Applicant Type',
        choices=APPLICANT_TYPE_CHOICES,
        required=False
    )
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        applicant_type = cleaned_data.get("applicant_type")

        if role == "applicant" and not applicant_type:
            raise ValidationError("Applicant type is required if role is Applicant.")

        if role != "applicant" and applicant_type:
            raise ValidationError("Applicant type should only be set if role is Applicant.")

        return cleaned_data

    def save(self):
        data = self.cleaned_data

    # 1. Create user (signal will auto-create UserProfile)
        user = User.objects.create_user(
            username=data["username"],
            password=data["password"]
        )

        # 2. Update profile created by signal
        profile = user.userprofile
        profile.role = data["role"]
        profile.applicant_type = data["applicant_type"]
        profile.save()
        return user

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken. Please choose another one.")
        return username

class RequestServiceForm(forms.Form):
    TYPE = [
        ('issue' , "Issue"),
        ('license' , "License"),
    ]

    MARKET = [
        ('insurance' , "Insurance"),
        ('mortgage' , "Mortgage"),
        ('cma', 'CMA')
    ]
    market = forms.ChoiceField(label='Market', choices=MARKET)
    type = forms.ChoiceField(label='Type', choices=TYPE)

    def save(self, user):
        data = self.cleaned_data
        service = Service.objects.create(
            market=data["market"],
            type=data["type"],
            applicant=user.userprofile,
        )

        return service

class ServiceApprovalForm(forms.Form):
    fee = forms.IntegerField(required=True)
    fixed = forms.BooleanField(required=False)

    def save(self, pk):
        service = Service.objects.get(pk=pk)
        data = self.cleaned_data
        service.status = Service.Status.REVIEWING
        service.fee = data["fee"]
        service.fixed = data["fixed"]
        service.save()