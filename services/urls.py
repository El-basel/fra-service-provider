from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/login/', views.login_view, name='login_view'),
    path('accounts/logout/', views.logout_view, name='logout_view'),
    path('accounts/signup/', views.signup_view, name='signup_view'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('request-service/', views.request_service, name='request_service'),
    path('service-approval/<int:pk>/', views.service_approval, name='service_approval'),
    path('delete-service/<int:pk>/', views.delete_service, name='delete_service'),
    path('service-review/<int:pk>/', views.service_review, name='service_review'),
    path('service-approve/<int:pk>/', views.service_approve, name='service_approve'),
    path('service-reject/<int:pk>/', views.service_reject, name='service_reject'),
    path('pay-service/<int:pk>/', views.pay_service, name='pay_service'),
    path('history/', views.history, name='history'),
    path('my-services/', views.my_services, name='my_services'),
]