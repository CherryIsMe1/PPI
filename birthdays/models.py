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
