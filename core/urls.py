# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'), # This will be the default page after login
]