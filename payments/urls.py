# payments/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.payment_list, name='payment_list'),
    path('for_booking/<int:booking_pk>/create/', views.payment_create, name='payment_create'),
    path('<int:pk>/', views.payment_detail, name='payment_detail'),
    path('<int:pk>/edit/', views.payment_update, name='payment_update'), # <--- ADDED
    path('<int:pk>/delete/', views.payment_delete, name='payment_delete'), # <--- ADDED
]