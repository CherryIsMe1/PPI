from django.urls import path
from . import views

app_name = 'birthdays'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('friends/', views.friend_list, name='friend_list'),
    path('friends/add/', views.friend_create, name='friend_create'),
    path('friends/<int:pk>/edit/', views.friend_update, name='friend_update'),
    path('friends/<int:pk>/delete/', views.friend_delete, name='friend_delete'),
    path('calendar/', views.calendar_view, name='calendar'),
]
