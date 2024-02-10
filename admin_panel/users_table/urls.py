from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_list, name='user_list'),
    path('send_message/', views.send_message, name='send_message')
]