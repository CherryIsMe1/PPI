from django import forms
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
