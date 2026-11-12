from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import (
    Friend,
    Event,
    EventParticipant,
    EventComment,
    EventPoll,
    PollOption,
    PollVote,
)


class BirthdayAndEventTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.other_user = User.objects.create_user(username='guestuser', password='password123')
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
            budget=150.00,
            is_public=True
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
            'is_public': True,
        }
        create_res = self.client.post(reverse('birthdays:event_create'), new_event_data)
        self.assertEqual(create_res.status_code, 302)
        self.assertEqual(Event.objects.filter(title='Grill urodzinowy').count(), 1)

    def test_event_rsvp(self):
        """Etap 5: Test deklaracji obecności (RSVP)"""
        self.client.login(username='guestuser', password='password123')
        rsvp_res = self.client.post(
            reverse('birthdays:event_rsvp', kwargs={'pk': self.event.pk}),
            {'status': 'going'}
        )
        self.assertEqual(rsvp_res.status_code, 302)
        participant = EventParticipant.objects.get(event=self.event, user=self.other_user)
        self.assertEqual(participant.status, 'going')

    def test_event_comment(self):
        """Etap 5: Test dodawania komentarza"""
        self.client.login(username='guestuser', password='password123')
        comment_res = self.client.post(
            reverse('birthdays:event_comment_add', kwargs={'pk': self.event.pk}),
            {'content': 'Cześć! Przyniosę przekąski.'}
        )
        self.assertEqual(comment_res.status_code, 302)
        self.assertEqual(EventComment.objects.filter(event=self.event, author=self.other_user).count(), 1)

    def test_event_poll_and_voting(self):
        """Etap 5: Test tworzenia ankiety i oddawania głosu"""
        # Organizator tworzy ankietę
        poll = EventPoll.objects.create(event=self.event, question='Jaki prezent kupujemy?')
        opt1 = PollOption.objects.create(poll=poll, text='Książka')
        opt2 = PollOption.objects.create(poll=poll, text='Gra planszowa')

        # Użytkownik głosuje
        self.client.login(username='guestuser', password='password123')
        vote_res = self.client.post(
            reverse('birthdays:event_poll_vote', kwargs={'pk': self.event.pk, 'poll_pk': poll.pk}),
            {'option_id': opt2.pk}
        )
        self.assertEqual(vote_res.status_code, 302)
        self.assertEqual(PollVote.objects.filter(poll=poll, user=self.other_user).count(), 1)
        self.assertEqual(opt2.votes_count, 1)
        self.assertEqual(opt1.votes_count, 0)
        self.assertEqual(opt2.percentage(), 100)
