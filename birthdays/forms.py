from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Friend, Event, EventComment, EventPoll, PollOption


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'friend', 'event_type', 'date', 'time', 'location', 'description', 'budget', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'np. 21. urodziny Adama – domówka'
            }),
            'friend': forms.Select(attrs={
                'class': 'form-select'
            }),
            'event_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'np. Klub Cyber / Działka / Mieszkanie'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'np. Plan imprezy, pomysły na niespodziankę, co zabrać...'
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'np. 50.00',
                'step': '0.01'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'title': 'Tytuł wydarzenia',
            'friend': 'Solenizant (opcjonalnie)',
            'event_type': 'Rodzaj wydarzenia',
            'date': 'Data wydarzenia',
            'time': 'Godzina rozpoczęcia',
            'location': 'Lokalizacja / Adres',
            'description': 'Opis i szczegóły imprezy',
            'budget': 'Przewidywany budżet / Składka (zł)',
            'is_public': 'Wydarzenie otwarte (widoczne dla wszystkich i umożliwiające zapisy)',
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['friend'].queryset = Friend.objects.filter(user=user)
        self.fields['friend'].empty_label = "-- Brak solenizanta (wydarzenie ogólne) --"


class CommentForm(forms.ModelForm):
    class Meta:
        model = EventComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Napisz komentarz, propozycję lub wiadomość do uczestników...'
            })
        }
        labels = {
            'content': 'Twój komentarz',
        }


class PollCreateForm(forms.ModelForm):
    options_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Wpisz opcje do wyboru, każdą w nowej linii:\nnp.\nKarta podarunkowa do sklepu\nZestaw klocków LEGO\nWspólny wypad na gokarty\nGra planszowa'
        }),
        label="Opcje do wyboru",
        help_text="Wpisz każdą opcję w nowej linii (minimum 2 opcje)."
    )

    class Meta:
        model = EventPoll
        fields = ['question']
        widgets = {
            'question': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'np. Co kupujemy solenizantowi na prezent?'
            })
        }
        labels = {
            'question': 'Pytanie w ankiecie',
        }

    def clean_options_text(self):
        text = self.cleaned_data.get('options_text', '').strip()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if len(lines) < 2:
            raise forms.ValidationError("Podaj co najmniej dwie różne opcje do wyboru.")
        return lines



class FriendForm(forms.ModelForm):
    class Meta:
        model = Friend
        fields = ['first_name', 'last_name', 'birth_date', 'notes', 'phone_number', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'np. Jan'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'np. Kowalski'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'np. Pomysły na prezent, hobby, rozmiar koszulki...'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'np. +48 123 456 789'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'np. jan.kowalski@example.com'
            }),
        }
        labels = {
            'first_name': 'Imię',
            'last_name': 'Nazwisko',
            'birth_date': 'Data urodzin',
            'notes': 'Notatki (np. prezenty, zainteresowania)',
            'phone_number': 'Numer telefonu',
            'email': 'Adres e-mail',
        }


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50,
        required=False,
        label="Imię",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Twoje imię'})
    )
    last_name = forms.CharField(
        max_length=50,
        required=False,
        label="Nazwisko",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Twoje nazwisko'})
    )
    email = forms.EmailField(
        required=True,
        label="Adres e-mail",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'twoj.email@example.com'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username': 'Nazwa użytkownika (login)',
        }
        help_texts = {
            'username': 'Wymagane. Dozwolone litery, cyfry i znaki @/./+/-/_.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'np. netrunner99'
        })
        if 'password' in self.fields:
            self.fields['password'].widget.attrs.update({'class': 'form-control'})
        if 'password_2' in self.fields:
            self.fields['password_2'].widget.attrs.update({'class': 'form-control'})
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Imię'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nazwisko'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Adres e-mail'}),
        }
        labels = {
            'first_name': 'Imię',
            'last_name': 'Nazwisko',
            'email': 'Adres e-mail',
        }
