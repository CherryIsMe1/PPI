from django.contrib import admin
from .models import Friend, Event

# Personalizacja panelu administracyjnego na język polski
admin.site.site_header = "Panel Administracyjny UrodzinkiApp"
admin.site.site_title = "UrodzinkiApp Admin"
admin.site.index_title = "Zarządzanie Portalem"


@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'user',
        'birth_date',
        'display_days_until_birthday',
        'display_upcoming_age',
        'email',
    )
    list_filter = ('user', 'birth_date')
    search_fields = ('first_name', 'last_name', 'email', 'user__username', 'notes')
    ordering = ('first_name', 'last_name')

    @admin.display(description="Dni do urodzin")
    def display_days_until_birthday(self, obj):
        return obj.days_until_birthday

    @admin.display(description="Nadchodzący wiek")
    def display_upcoming_age(self, obj):
        return obj.upcoming_age


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'user',
        'friend',
        'event_type',
        'date',
        'time',
        'location',
        'display_days_until',
    )
    list_filter = ('event_type', 'date', 'user')
    search_fields = ('title', 'location', 'description', 'friend__first_name', 'friend__last_name', 'user__username')
    ordering = ('date', 'time')

    @admin.display(description="Status / Dni do terminu")
    def display_days_until(self, obj):
        if obj.is_today:
            return "DZIŚ!"
        elif obj.is_past:
            return f"Odbyło się ({abs(obj.days_until)} dni temu)"
        return f"za {obj.days_until} dni"


