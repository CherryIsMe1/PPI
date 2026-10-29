from django.contrib import admin
from .models import Friend


@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'user', 'birth_date', 'days_until_birthday', 'upcoming_age', 'email')
    list_filter = ('user', 'birth_date')
    search_fields = ('first_name', 'last_name', 'email', 'user__username', 'notes')
    ordering = ('first_name', 'last_name')
