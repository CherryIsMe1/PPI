from datetime import date
from django.db import models
from django.contrib.auth.models import User


class Friend(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='friends',
        verbose_name="Użytkownik"
    )
    first_name = models.CharField(max_length=100, verbose_name="Imię")
    last_name = models.CharField(max_length=100, verbose_name="Nazwisko")
    birth_date = models.DateField(verbose_name="Data urodzin")
    notes = models.TextField(blank=True, verbose_name="Notatka")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Numer telefonu")
    email = models.EmailField(blank=True, verbose_name="Adres e-mail")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data modyfikacji")

    class Meta:
        verbose_name = "Znajomy"
        verbose_name_plural = "Znajomi"
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def next_birthday(self):
        today = date.today()
        try:
            bday_this_year = self.birth_date.replace(year=today.year)
        except ValueError:
            # Obsługa 29 lutego w latach nieprzestępnych
            bday_this_year = self.birth_date.replace(year=today.year, day=28)

        if bday_this_year < today:
            try:
                return self.birth_date.replace(year=today.year + 1)
            except ValueError:
                return self.birth_date.replace(year=today.year + 1, day=28)
        return bday_this_year

    @property
    def days_until_birthday(self):
        return (self.next_birthday - date.today()).days

    @property
    def is_today(self):
        return self.days_until_birthday == 0

    @property
    def is_soon(self):
        """Czy urodziny przypadają w ciągu najbliższych 7 dni"""
        return 0 <= self.days_until_birthday <= 7

    @property
    def current_age(self):
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    @property
    def upcoming_age(self):
        return self.next_birthday.year - self.birth_date.year


class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('birthday', '🎂 Impreza urodzinowa'),
        ('surprise', '🎉 Przyjęcie niespodzianka'),
        ('gift', '🎁 Zrzutka na prezent'),
        ('outing', '🍕 Wypad / Wyjście do lokalu'),
        ('other', '✨ Inne wydarzenie okolicznościowe'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name="Organizator"
    )
    title = models.CharField(max_length=200, verbose_name="Tytuł wydarzenia")
    friend = models.ForeignKey(
        Friend,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
        verbose_name="Solenizant (opcjonalnie)"
    )
    event_type = models.CharField(
        max_length=30,
        choices=EVENT_TYPE_CHOICES,
        default='birthday',
        verbose_name="Rodzaj wydarzenia"
    )
    date = models.DateField(verbose_name="Data wydarzenia")
    time = models.TimeField(null=True, blank=True, verbose_name="Godzina rozpoczęcia")
    location = models.CharField(max_length=200, blank=True, verbose_name="Lokalizacja / Miejsce")
    description = models.TextField(blank=True, verbose_name="Opis i szczegóły imprezy")
    budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Składka / Budżet (zł)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data modyfikacji")

    class Meta:
        verbose_name = "Wydarzenie"
        verbose_name_plural = "Wydarzenia"
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.title} ({self.date.strftime('%d.%m.%Y')})"

    @property
    def days_until(self):
        return (self.date - date.today()).days

    @property
    def is_today(self):
        return self.days_until == 0

    @property
    def is_past(self):
        return self.days_until < 0

    @property
    def is_upcoming(self):
        return self.days_until >= 0

    @property
    def is_soon(self):
        return 0 <= self.days_until <= 7

