import calendar
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from .models import Friend
from .forms import FriendForm, RegisterForm, UserProfileUpdateForm


# ==============================================================================
# AUTHENTICATION & PROFILE (Etap 3: Użytkownicy)
# ==============================================================================

def register_view(request):
    """Rejestracja nowego użytkownika"""
    if request.user.is_authenticated:
        return redirect('birthdays:dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Witaj w systemie, {user.username}! Twoje konto zostało utworzone.')
            return redirect('birthdays:dashboard')
    else:
        form = RegisterForm()

    return render(request, 'birthdays/register.html', {'form': form})


def login_view(request):
    """Logowanie użytkownika"""
    if request.user.is_authenticated:
        return redirect('birthdays:dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Zalogowano pomyślnie. Witaj z powrotem, {user.username}!')
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('birthdays:dashboard')
        else:
            messages.error(request, 'Nieprawidłowy login lub hasło. Spróbuj ponownie.')
    else:
        form = AuthenticationForm()

    return render(request, 'birthdays/login.html', {'form': form})


def logout_view(request):
    """Wylogowanie użytkownika"""
    logout(request)
    messages.info(request, 'Zostałeś pomyślnie wylogowany.')
    return redirect('birthdays:login')


@login_required
def profile_view(request):
    """Profil zalogowanego użytkownika i edycja danych"""
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Twoje dane profilowe zostały zaktualizowane!')
            return redirect('birthdays:profile')
    else:
        form = UserProfileUpdateForm(instance=request.user)

    user_friends_count = Friend.objects.filter(user=request.user).count()

    context = {
        'form': form,
        'friends_count': user_friends_count,
        'user': request.user,
    }
    return render(request, 'birthdays/profile.html', context)


# ==============================================================================
# GŁÓWNA APLIKACJA (Zabezpieczona: dostęp tylko do własnych kontaktów)
# ==============================================================================

@login_required
def dashboard(request):
    """Główny pulpit z podsumowaniem i powiadomieniami o nadchodzących urodzinach"""
    # Przypisz ewentualne stare kontakty bez właściciela do pierwszego zalogowanego użytkownika
    Friend.objects.filter(user__isnull=True).update(user=request.user)

    # Pobieraj tylko kontakty zalogowanego użytkownika
    all_friends = list(Friend.objects.filter(user=request.user))
    all_friends.sort(key=lambda f: f.days_until_birthday)

    today_birthdays = [f for f in all_friends if f.is_today]
    upcoming_7_days = [f for f in all_friends if 0 < f.days_until_birthday <= 7]
    upcoming_30_days = [f for f in all_friends if 7 < f.days_until_birthday <= 30]

    context = {
        'total_count': len(all_friends),
        'today_birthdays': today_birthdays,
        'upcoming_7_days': upcoming_7_days,
        'upcoming_30_days': upcoming_30_days,
        'recent_friends': all_friends[:6],
    }
    return render(request, 'birthdays/dashboard.html', context)


@login_required
def friend_list(request):
    """Lista znajomych zalogowanego użytkownika z wyszukiwaniem i sortowaniem"""
    query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', 'next_bday')

    friends = Friend.objects.filter(user=request.user)
    if query:
        friends = friends.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(notes__icontains=query)
        )

    friend_list = list(friends)

    if sort_by == 'name':
        friend_list.sort(key=lambda f: (f.last_name.lower(), f.first_name.lower()))
    elif sort_by == 'age':
        friend_list.sort(key=lambda f: f.current_age, reverse=True)
    else:  # 'next_bday' domyślnie
        friend_list.sort(key=lambda f: f.days_until_birthday)

    context = {
        'friends': friend_list,
        'query': query,
        'sort_by': sort_by,
        'total_count': len(friend_list),
    }
    return render(request, 'birthdays/friend_list.html', context)


@login_required
def friend_create(request):
    """Formularz dodawania nowego znajomego dla zalogowanego użytkownika"""
    if request.method == 'POST':
        form = FriendForm(request.POST)
        if form.is_valid():
            friend = form.save(commit=False)
            friend.user = request.user
            friend.save()
            messages.success(request, f'Pomyślnie dodano znajomego: {friend.first_name} {friend.last_name}!')
            return redirect('birthdays:friend_list')
    else:
        form = FriendForm()

    return render(request, 'birthdays/friend_form.html', {
        'form': form,
        'title': 'Dodaj nowego znajomego',
        'btn_text': 'Zapisz znajomego'
    })


@login_required
def friend_update(request, pk):
    """Edycja danych znajomego (zabezpieczona przed edycją cudzych kontaktów)"""
    friend = get_object_or_404(Friend, pk=pk, user=request.user)
    if request.method == 'POST':
        form = FriendForm(request.POST, instance=friend)
        if form.is_valid():
            form.save()
            messages.success(request, f'Zaktualizowano dane dla: {friend.first_name} {friend.last_name}.')
            return redirect('birthdays:friend_list')
    else:
        form = FriendForm(instance=friend)

    return render(request, 'birthdays/friend_form.html', {
        'form': form,
        'friend': friend,
        'title': f'Edycja: {friend.first_name} {friend.last_name}',
        'btn_text': 'Zapisz zmiany'
    })


@login_required
def friend_delete(request, pk):
    """Usuwanie znajomego z bazy (zabezpieczone przed usuwaniem cudzych kontaktów)"""
    friend = get_object_or_404(Friend, pk=pk, user=request.user)
    if request.method == 'POST':
        name = f"{friend.first_name} {friend.last_name}"
        friend.delete()
        messages.info(request, f'Usunięto znajomego: {name}.')
        return redirect('birthdays:friend_list')

    return render(request, 'birthdays/friend_confirm_delete.html', {'friend': friend})


@login_required
def calendar_view(request):
    """Widok kalendarza urodzin dla kontaktów zalogowanego użytkownika"""
    today = date.today()
    selected_month = int(request.GET.get('month', today.month))
    selected_year = int(request.GET.get('year', today.year))

    polish_months = [
        '', 'Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec',
        'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień'
    ]

    all_friends = list(Friend.objects.filter(user=request.user))

    # Pogrupowanie znajomych według miesięcy urodzin (1..12)
    months_data = []
    for m in range(1, 13):
        m_friends = [f for f in all_friends if f.birth_date.month == m]
        m_friends.sort(key=lambda f: f.birth_date.day)
        months_data.append({
            'month_number': m,
            'month_name': polish_months[m],
            'is_current': (m == today.month),
            'friends': m_friends,
            'count': len(m_friends)
        })

    # Widok wybranego miesiąca (siatka dni)
    cal = calendar.Calendar(firstweekday=0) # Poniedziałek
    month_days = cal.monthdays2calendar(selected_year, selected_month)

    # Mapa dni: {dzień: [znajomi]}
    days_map = {}
    for f in all_friends:
        if f.birth_date.month == selected_month:
            d = f.birth_date.day
            if d not in days_map:
                days_map[d] = []
            days_map[d].append(f)

    # Poprzedni/następny miesiąc
    prev_month = 12 if selected_month == 1 else selected_month - 1
    prev_year = selected_year - 1 if selected_month == 1 else selected_year
    next_month = 1 if selected_month == 12 else selected_month + 1
    next_year = selected_year + 1 if selected_month == 12 else selected_year

    context = {
        'months_data': months_data,
        'today': today,
        'selected_month': selected_month,
        'selected_month_name': polish_months[selected_month],
        'selected_year': selected_year,
        'month_days': month_days,
        'days_map': days_map,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }
    return render(request, 'birthdays/calendar.html', context)
