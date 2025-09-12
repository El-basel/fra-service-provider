from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/login/', views.login_view, name='login_view'),
    path('accounts/logout/', views.logout_view, name='logout_view'),
    path('accounts/signup/', views.signup_view, name='signup_view'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('request-service/', views.request_service, name='request_service'),
    path('applicant/payments/<int:service_id>/', views.dashboard, name='payments'),
]