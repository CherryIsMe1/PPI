import calendar
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Friend
from .forms import FriendForm


def dashboard(request):
    """Główny pulpit z podsumowaniem i powiadomieniami o nadchodzących urodzinach"""
    all_friends = list(Friend.objects.all())
    # Sortuj według najbliższych urodzin
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


def friend_list(request):
    """Lista wszystkich znajomych z wyszukiwaniem i sortowaniem"""
    query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', 'next_bday')

    friends = Friend.objects.all()
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


def friend_create(request):
    """Formularz dodawania nowego znajomego"""
    if request.method == 'POST':
        form = FriendForm(request.POST)
        if form.is_valid():
            friend = form.save()
            messages.success(request, f'Pomyślnie dodano znajomego: {friend.first_name} {friend.last_name}!')
            return redirect('birthdays:friend_list')
    else:
        form = FriendForm()

    return render(request, 'birthdays/friend_form.html', {
        'form': form,
        'title': 'Dodaj nowego znajomego',
        'btn_text': 'Zapisz znajomego'
    })


def friend_update(request, pk):
    """Edycja danych znajomego"""
    friend = get_object_or_404(Friend, pk=pk)
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


def friend_delete(request, pk):
    """Usuwanie znajomego z bazy"""
    friend = get_object_or_404(Friend, pk=pk)
    if request.method == 'POST':
        name = f"{friend.first_name} {friend.last_name}"
        friend.delete()
        messages.info(request, f'Usunięto znajomego: {name}.')
        return redirect('birthdays:friend_list')

    return render(request, 'birthdays/friend_confirm_delete.html', {'friend': friend})


def calendar_view(request):
    """Widok kalendarza urodzin z podziałem na miesiące oraz widok miesięczny"""
    today = date.today()
    selected_month = int(request.GET.get('month', today.month))
    selected_year = int(request.GET.get('year', today.year))

    polish_months = [
        '', 'Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec',
        'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień'
    ]

    all_friends = list(Friend.objects.all())

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

    # Przygotuj mapę dni w wybranym miesiącu: {dzień: [znajomi]}
    days_map = {}
    for f in all_friends:
        if f.birth_date.month == selected_month:
            d = f.birth_date.day
            if d not in days_map:
                days_map[d] = []
            days_map[d].append(f)

    # Przyciski poprzedni/następny miesiąc
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
