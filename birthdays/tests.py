from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Friend, Event


class BirthdayAndEventTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client = Client()

        today = date.today()
        self.friend = Friend.objects.create(
            user=self.user,
            first_name='Kasia',
            last_name='Kowalska',
            birth_date=date(today.year - 20, today.month, today.day),
            email='kasia@example.com'
        )

        self.event = Event.objects.create(
            user=self.user,
            title='20. urodziny Kasi',
            friend=self.friend,
            event_type='birthday',
            date=date.today() + timedelta(days=5),
            location='Klub Cyber',
            budget=150.00
        )

    def test_friend_properties(self):
        """Sprawdzenie wyliczeń wieku i dni do urodzin"""
        self.assertEqual(self.friend.current_age, 20)
        self.assertIsNotNone(self.friend.days_until_birthday)

    def test_event_properties(self):
        """Sprawdzenie statusu i odliczania do wydarzenia"""
        self.assertEqual(self.event.days_until, 5)
        self.assertTrue(self.event.is_upcoming)
        self.assertFalse(self.event.is_past)

    def test_login_required_protection(self):
        """Upewnienie się, że niezalogowany gość jest przekierowywany do logowania"""
        response = self.client.get(reverse('birthdays:event_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('birthdays:login'), response.url)

    def test_authenticated_event_list(self):
        """Zalogowany użytkownik widzi swoje wydarzenia"""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('birthdays:event_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '20. urodziny Kasi')
        self.assertContains(response, 'Klub Cyber')

    def test_event_crud_flow(self):
        """Test tworzenia i usuwania wydarzenia"""
        self.client.login(username='testuser', password='password123')
        new_event_data = {
            'title': 'Grill urodzinowy',
            'event_type': 'outing',
            'date': (date.today() + timedelta(days=10)).strftime('%Y-%m-%d'),
            'location': 'Działka',
            'budget': '100.00',
        }
        create_res = self.client.post(reverse('birthdays:event_create'), new_event_data)
        self.assertEqual(create_res.status_code, 302)
        self.assertEqual(Event.objects.filter(title='Grill urodzinowy').count(), 1)
