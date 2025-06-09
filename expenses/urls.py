# expenses/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # URLs for individual Expense records
    path('', views.expense_list, name='expense_list'),
    path('for_booking/<int:booking_pk>/create/', views.expense_create, name='expense_create'),
    path('<int:pk>/', views.expense_detail, name='expense_detail'),
    path('<int:pk>/edit/', views.expense_update, name='expense_update'),
    path('<int:pk>/delete/', views.expense_delete, name='expense_delete'),

    # NEW URLs for ExpenseType management
    path('types/', views.expense_type_list, name='expense_type_list'),
    path('types/create/', views.expense_type_create, name='expense_type_create'),
    path('types/<int:pk>/edit/', views.expense_type_update, name='expense_type_update'),
    path('types/<int:pk>/delete/', views.expense_type_delete, name='expense_type_delete'),
]