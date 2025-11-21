# usuarios/urls.py
from django.urls import path
from . import views   # ← ESTO FALTABA

urlpatterns = [
    path('login/', views.login_email, name='login'),
    path('registro/', views.registro, name='registro'),
]
