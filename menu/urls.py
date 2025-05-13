from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.home, name='home'),  # главная страница
    path('about/', views.about, name='about'),  # страница "О нас"
    ]