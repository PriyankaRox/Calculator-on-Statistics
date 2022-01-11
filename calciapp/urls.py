from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf.urls import url
from . import views
from .views import calculator, contact, VerifyEmail

urlpatterns = [
    path('', views.index, name='index'),
    path('calculator', views.calculator, name='calculator'),
    path('result', views.result, name='result'),
    path('contact', views.contact, name='contact'),
    path('login', views.login, name='login'),
    path('logout', views.logoutUser, name='logout'),
    path('signup', views.signup, name='signup'),
    path('email-verify', VerifyEmail.as_view(),name='email-verify'),
    path('forgotpassword', views.forgotpassword, name='forgotpassword'),
    path('change-password/<token>/', views.ChangePassword, name='change_password'),
]