# trips/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.trip_list, name='trip_list'),
    path('create/', views.trip_create, name='trip_create'),
    path('<int:pk>/', views.trip_detail, name='trip_detail'),
    path('<int:pk>/edit/', views.trip_update, name='trip_update'),
    path('<int:pk>/delete/', views.trip_delete, name='trip_delete'),

    # Re-added: Trip Participants List
    path('<int:trip_pk>/participants/', views.trip_participants, name='trip_participants'), # <--- RE-ADDED

    # URLs for Price Tiers
    path('<int:trip_pk>/tiers/create/', views.trip_price_tier_create, name='trip_price_tier_create'),
    path('tiers/<int:pk>/edit/', views.trip_price_tier_update, name='trip_price_tier_update'),
    path('tiers/<int:pk>/delete/', views.trip_price_tier_delete, name='trip_price_tier_delete'),

    # URLs for Add-Ons
    path('<int:trip_pk>/addons/create/', views.trip_add_on_create, name='trip_add_on_create'),
    path('addons/<int:pk>/edit/', views.trip_add_on_update, name='trip_add_on_update'),
    path('addons/<int:pk>/delete/', views.trip_add_on_delete, name='trip_add_on_delete'),
]