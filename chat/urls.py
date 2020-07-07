# chat/urls.py
from . import views
from django.urls import path

urlpatterns = [
    path('', views.room, name='room'),
    path('start/', views.start, name='start'),
    path('start/operator/', views.start_operator, name='start_operator'),
    path('stop/<str:room_uuid>/', views.stop, name='stop'),
]