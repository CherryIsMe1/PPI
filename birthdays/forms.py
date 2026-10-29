from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Friend


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
