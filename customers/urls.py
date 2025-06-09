# customers/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.customer_list, name='customer_list'),
    path('create/', views.customer_create, name='customer_create'),
    path('<int:pk>/', views.customer_detail, name='customer_detail'),
    path('<int:pk>/edit/', views.customer_update, name='customer_update'),
    path('<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    
    # Customer Attachments URLs
    path('<int:customer_pk>/attachments/upload/', views.customer_attachment_upload, name='customer_attachment_upload'), # <--- ADDED
    path('attachments/<int:pk>/delete/', views.customer_attachment_delete, name='customer_attachment_delete'), # <--- ADDED
]