# bookings/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.booking_list, name='booking_list'),
    path('create/', views.booking_create, name='booking_create'),
    path('<int:pk>/', views.booking_detail, name='booking_detail'),
    path('<int:pk>/edit/', views.booking_update, name='booking_update'),
    path('<int:pk>/delete/', views.booking_delete, name='booking_delete'),
    path('<int:booking_pk>/add_note/', views.booking_add_note, name='booking_add_note'), # <--- ADDED
    path('ajax/get_trip_options/', views.get_trip_options_for_booking, name='get_trip_options_for_booking'),
]