from django.contrib import admin
from django.urls import path, include
from budget import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('', views.dashboard, name='dashboard'),
    path('finance/', views.finance_manager, name='finance_manager'),
    path('savings/', views.savings_view, name='savings_view'),
    path('debts/', views.debt_view, name='debt_view'), 
    path('debts/', views.debt_view, name='debt_view'),
]