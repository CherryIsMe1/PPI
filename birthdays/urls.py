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
    
    # Etap 3: Użytkownicy & Autoryzacja
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # Etap 4: Wydarzenia (CRUD)
    path('events/', views.event_list, name='event_list'),
    path('events/add/', views.event_create, name='event_create'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/<int:pk>/edit/', views.event_update, name='event_update'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),

    # Etap 5: Uczestnicy, Komentarze i Głosowanie
    path('events/<int:pk>/rsvp/', views.event_rsvp, name='event_rsvp'),
    path('events/<int:pk>/comment/', views.event_comment_add, name='event_comment_add'),
    path('events/<int:pk>/comment/<int:comment_pk>/delete/', views.event_comment_delete, name='event_comment_delete'),
    path('events/<int:pk>/poll/add/', views.event_poll_create, name='event_poll_create'),
    path('events/<int:pk>/poll/<int:poll_pk>/vote/', views.event_poll_vote, name='event_poll_vote'),
]
