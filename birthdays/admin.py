from django.contrib import admin
from .models import (
    Friend,
    Event,
    EventParticipant,
    EventComment,
    EventPoll,
    PollOption,
    PollVote,
)

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


class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 3
    verbose_name = "Opcja do wyboru"
    verbose_name_plural = "Opcje do wyboru"


class EventParticipantInline(admin.TabularInline):
    model = EventParticipant
    extra = 0
    verbose_name = "Uczestnik"
    verbose_name_plural = "Uczestnicy"


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
        'is_public',
        'display_days_until',
    )
    list_filter = ('event_type', 'date', 'is_public', 'user')
    search_fields = ('title', 'location', 'description', 'friend__first_name', 'friend__last_name', 'user__username')
    ordering = ('date', 'time')
    inlines = [EventParticipantInline]

    @admin.display(description="Status / Dni do terminu")
    def display_days_until(self, obj):
        if obj.is_today:
            return "DZIŚ!"
        elif obj.is_past:
            return f"Odbyło się ({abs(obj.days_until)} dni temu)"
        return f"za {obj.days_until} dni"


@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'status', 'joined_at')
    list_filter = ('status', 'joined_at')
    search_fields = ('event__title', 'user__username')


@admin.register(EventComment)
class EventCommentAdmin(admin.ModelAdmin):
    list_display = ('event', 'author', 'short_content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('event__title', 'author__username', 'content')

    @admin.display(description="Treść")
    def short_content(self, obj):
        return obj.content[:60] + '...' if len(obj.content) > 60 else obj.content


@admin.register(EventPoll)
class EventPollAdmin(admin.ModelAdmin):
    list_display = ('question', 'event', 'is_active', 'total_votes', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('question', 'event__title')
    inlines = [PollOptionInline]


@admin.register(PollVote)
class PollVoteAdmin(admin.ModelAdmin):
    list_display = ('poll', 'option', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('poll__question', 'option__text', 'user__username')



