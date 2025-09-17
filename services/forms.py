from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import *

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if not username or not password:
            error = ValidationError("Username and Password are required")
            self.add_error('username', error)
            self.add_error('password', error)
        if not User.objects.filter(username=username).exists():
            error = ValidationError("Username does not exist")
            self.add_error('username', error)

        user = User.objects.get(username=username)
        if not user.check_password(password):
            error = ValidationError("Incorrect Password")
            self.add_error('password', error)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'


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
        username = cleaned_data.get("username")


        if role == "applicant" and not applicant_type:
            error = ValidationError("Applicant type is required if role is Applicant.")
            self.add_error("applicant_type", "Applicant type must be specified")

        if role != "applicant" and applicant_type:
            error = ValidationError("Applicant type is required if role is Applicant.")
            self.add_error("applicant_type", "Applicant type must be specified")

        if User.objects.filter(username=username).exists():
            error = ValidationError("Username already exists")
            self.add_error("username", "Username already exists")
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


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        self.fields['applicant_type'].widget.attrs['class'] += ' applicant-type-wrapper'
        self.fields['role'].widget.attrs['class'] += ' role-wrapper'

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class ServiceApprovalForm(forms.Form):
    fee = forms.IntegerField(required=True)
    fixed = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        fee = cleaned_data.get("fee")
        if fee < 0:
            error = ValidationError("Fee should be greater than 0.")
            self.add_error('fee', error)

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fee'].widget.attrs['class'] = 'form-control'
        self.fields['fixed'].widget.attrs['class'] = 'form-check-input'

    def save(self, pk):
        service = Service.objects.get(pk=pk)
        data = self.cleaned_data
        service.status = Service.Status.REVIEWING
        service.fee = data["fee"]
        service.fixed = data["fixed"]
        service.save()