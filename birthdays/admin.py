from django.contrib import admin
from .models import Friend


@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birth_date', 'days_until_birthday', 'upcoming_age', 'email')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('birth_date',)
