import calendar
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from .models import (
    Friend,
    Event,
    EventParticipant,
    EventComment,
    EventPoll,
    PollOption,
    PollVote,
)
from .forms import (
    FriendForm,
    RegisterForm,
    UserProfileUpdateForm,
    EventForm,
    CommentForm,
    PollCreateForm,
)


# ==============================================================================
# REJESTRACJA, LOGOWANIE I PROFIL UŻYTKOWNIKA
# ==============================================================================

def register_view(request):
    """Rejestracja nowego konta użytkownika"""
    if request.user.is_authenticated:
        return redirect('birthdays:dashboard')

    if request.method == 'POST':
        # Pobieramy dane z formularza rejestracji
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Zapisujemy nowego użytkownika w bazie danych
            user = form.save()
            # Automatycznie logujemy użytkownika po pomyślnej rejestracji
            login(request, user)
            messages.success(request, f'Witaj w systemie, {user.username}! Twoje konto zostało utworzone.')
            return redirect('birthdays:dashboard')
    else:
        # Pusty formularz przy zapytaniu GET
        form = RegisterForm()

    return render(request, 'birthdays/register.html', {'form': form})


def login_view(request):
    """Logowanie istniejącego użytkownika"""
    if request.user.is_authenticated:
        return redirect('birthdays:dashboard')

    if request.method == 'POST':
        # Pobieramy login i hasło z żądania POST
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # Weryfikacja poprawności hasła w bazie danych Django
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
        # Pusty formularz logowania przy zapytaniu GET
        form = AuthenticationForm()

    return render(request, 'birthdays/login.html', {'form': form})


def logout_view(request):
    """Wylogowanie aktywnej sesji użytkownika"""
    logout(request)
    messages.info(request, 'Zostałeś pomyślnie wylogowany.')
    return redirect('birthdays:login')


@login_required
def profile_view(request):
    """Profil zalogowanego użytkownika oraz edycja jego danych"""
    if request.method == 'POST':
        # Aktualizacja imienia, nazwiska i adresu email
        form = UserProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Twoje dane profilowe zostały zaktualizowane!')
            return redirect('birthdays:profile')
    else:
        # Wypełniamy formularz aktualnymi danymi z bazy
        form = UserProfileUpdateForm(instance=request.user)

    # Liczba kontaktów dodanych przez tego użytkownika
    user_friends_count = Friend.objects.filter(user=request.user).count()

    context = {
        'form': form,
        'friends_count': user_friends_count,
        'user': request.user,
    }
    return render(request, 'birthdays/profile.html', context)


# ==============================================================================
# ZARZĄDZANIE ZNAJOMYMI I PULPIT (CRUD + KALENDARZ)
# ==============================================================================

@login_required
def dashboard(request):
    """Główny pulpit: podsumowanie liczbowe, najbliższe urodziny i nadchodzące imprezy"""
    # Zabezpieczenie: przypisz kontakty bez właściciela do obecnego użytkownika
    Friend.objects.filter(user__isnull=True).update(user=request.user)

    # Pobieramy z bazy (fetch) wyłącznie znajomych należących do zalogowanego użytkownika
    all_friends = list(Friend.objects.filter(user=request.user))
    # Sortujemy po liczbie dni pozostałych do urodzin (rosnąco)
    all_friends.sort(key=lambda f: f.days_until_birthday)

    # Filtrujemy jubilatów: dzisiaj, w ciągu 7 dni oraz w ciągu 30 dni
    today_birthdays = [f for f in all_friends if f.is_today]
    upcoming_7_days = [f for f in all_friends if 0 < f.days_until_birthday <= 7]
    upcoming_30_days = [f for f in all_friends if 7 < f.days_until_birthday <= 30]

    # Pobieramy z bazy nadchodzące wydarzenia użytkownika (od dzisiaj w przód, max 4)
    upcoming_events = list(Event.objects.filter(
        user=request.user,
        date__gte=date.today()
    ).order_by('date', 'time')[:4])

    events_count = Event.objects.filter(user=request.user).count()

    # Przekazujemy wszystkie dane do szablonu dashboard.html
    context = {
        'total_count': len(all_friends),
        'today_birthdays': today_birthdays,
        'upcoming_7_days': upcoming_7_days,
        'upcoming_30_days': upcoming_30_days,
        'recent_friends': all_friends[:6],
        'upcoming_events': upcoming_events,
        'events_count': events_count,
    }
    return render(request, 'birthdays/dashboard.html', context)


@login_required
def friend_list(request):
    """Lista znajomych zalogowanego użytkownika z wyszukiwarką i sortowaniem"""
    # Odczytujemy parametry zapytania GET z paska URL (?q=...&sort=...)
    query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', 'next_bday')

    # Pobieramy z bazy (fetch) rekordy przypisane do zalogowanego konta
    friends = Friend.objects.filter(user=request.user)
    
    # Filtrowanie wyszukiwarką po kilku polach (imię, nazwisko, email, notatki)
    if query:
        friends = friends.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(notes__icontains=query)
        )

    friend_list = list(friends)

    # Sortowanie w pamięci Pythona (po nazwisku, po wieku lub po najbliższych urodzinach)
    if sort_by == 'name':
        friend_list.sort(key=lambda f: (f.last_name.lower(), f.first_name.lower()))
    elif sort_by == 'age':
        friend_list.sort(key=lambda f: f.current_age, reverse=True)
    else:  # 'next_bday' - domyślnie wg dni do najbliższych urodzin
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
    """Tworzenie nowego kontaktu (formularz FriendForm)"""
    if request.method == 'POST':
        form = FriendForm(request.POST)
        if form.is_valid():
            # commit=False pozwala ustawić pole user przed fizycznym zapisem do bazy
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
    """Edycja danych kontaktu (zabezpieczona filtrem user=request.user)"""
    # get_object_or_404 wyrzuci 404, jeśli obiekt nie istnieje lub należy do innego usera
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
    """Usuwanie kontaktu z bazy danych"""
    friend = get_object_or_404(Friend, pk=pk, user=request.user)
    if request.method == 'POST':
        name = f"{friend.first_name} {friend.last_name}"
        friend.delete()
        messages.info(request, f'Usunięto znajomego: {name}.')
        return redirect('birthdays:friend_list')

    return render(request, 'birthdays/friend_confirm_delete.html', {'friend': friend})


@login_required
def calendar_view(request):
    """Kalendarz urodzin: generowanie siatki miesięcy i dni z dopasowanymi jubilatami"""
    today = date.today()
    selected_month = int(request.GET.get('month', today.month))
    selected_year = int(request.GET.get('year', today.year))

    polish_months = [
        '', 'Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec',
        'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień'
    ]

    all_friends = list(Friend.objects.filter(user=request.user))

    # Grupowanie znajomych według 12 miesięcy do zakładek (tabów)
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

    # Generowanie siatki dni wybranego miesiąca (od poniedziałku)
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdays2calendar(selected_year, selected_month)

    # Słownik dopasowania: {dzień_miesiąca: [lista solenizantów]}
    days_map = {}
    for f in all_friends:
        if f.birth_date.month == selected_month:
            d = f.birth_date.day
            if d not in days_map:
                days_map[d] = []
            days_map[d].append(f)

    # Pobieranie wydarzeń z bazy przypisanych do tego miesiąca
    month_events = Event.objects.filter(
        user=request.user,
        date__year=selected_year,
        date__month=selected_month
    ).order_by('time')
    events_map = {}
    for ev in month_events:
        d = ev.date.day
        if d not in events_map:
            events_map[d] = []
        events_map[d].append(ev)

    # Nawigacja: poprzedni i kolejny miesiąc
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
        'events_map': events_map,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }
    return render(request, 'birthdays/calendar.html', context)


# ==============================================================================
# ZARZĄDZANIE WYDARZENIAMI (CRUD: lista, szczegóły, dodawanie, edycja, usuwanie)
# ==============================================================================

@login_required
def event_list(request):
    """Lista wydarzeń – własnych i publicznych – z filtrowaniem i wyszukiwarką"""
    # Parametry filtrowania z paska URL (?q=...&type=...&status=...&scope=...)
    query = request.GET.get('q', '').strip()
    event_type = request.GET.get('type', '')
    status_filter = request.GET.get('status', 'upcoming')  # 'upcoming', 'past', 'all'
    scope = request.GET.get('scope', 'all')  # 'all', 'mine', 'joined'

    # Pobieramy z bazy (fetch) wydarzenia własne użytkownika oraz wszystkie publiczne
    events = Event.objects.filter(Q(user=request.user) | Q(is_public=True)).distinct()

    # Filtr zakresu: tylko moje / tylko te na które jestem zapisany
    if scope == 'mine':
        events = events.filter(user=request.user)
    elif scope == 'joined':
        events = events.filter(participants__user=request.user, participants__status='going')

    # Wyszukiwarka tekstowa po kilku polach jednocześnie (Q = OR)
    if query:
        events = events.filter(
            Q(title__icontains=query) |
            Q(location__icontains=query) |
            Q(description__icontains=query) |
            Q(friend__first_name__icontains=query) |
            Q(friend__last_name__icontains=query) |
            Q(user__username__icontains=query)
        )

    if event_type:
        events = events.filter(event_type=event_type)

    # Filtr statusu czasowego
    today = date.today()
    if status_filter == 'upcoming':
        events = events.filter(date__gte=today).order_by('date', 'time')
    elif status_filter == 'past':
        events = events.filter(date__lt=today).order_by('-date', '-time')
    else:  # 'all'
        events = events.order_by('date', 'time')

    events_list = list(events)

    # Liczniki do kafelków statystyk na górze strony
    user_visible = Event.objects.filter(Q(user=request.user) | Q(is_public=True)).distinct()
    upcoming_count = user_visible.filter(date__gte=today).count()
    past_count = user_visible.filter(date__lt=today).count()
    my_events_count = Event.objects.filter(user=request.user).count()

    context = {
        'events': events_list,
        'query': query,
        'event_type': event_type,
        'status_filter': status_filter,
        'scope': scope,
        'event_types': Event.EVENT_TYPE_CHOICES,
        'total_count': len(events_list),
        'upcoming_count': upcoming_count,
        'past_count': past_count,
        'my_events_count': my_events_count,
        'today': today,
    }
    return render(request, 'birthdays/event_list.html', context)


@login_required
def event_detail(request, pk):
    """Szczegóły jednego wydarzenia: uczestnicy, komentarze i ankiety"""
    # Dostęp tylko jeśli użytkownik jest organizatorem lub wydarzenie jest publiczne
    event = get_object_or_404(
        Event.objects.filter(Q(user=request.user) | Q(is_public=True)).distinct(),
        pk=pk
    )

    # Pobieramy listę uczestników z danymi o użytkowniku (select_related = jedno zapytanie SQL)
    participants = event.participants.select_related('user').all()
    going_list = [p for p in participants if p.status == 'going']
    maybe_list = [p for p in participants if p.status == 'maybe']
    declined_list = [p for p in participants if p.status == 'declined']

    # Sprawdzamy aktualny status RSVP zalogowanego użytkownika (going/maybe/declined/None)
    user_rsvp = None
    for p in participants:
        if p.user == request.user:
            user_rsvp = p.status
            break

    # Komentarze posortowane od najstarszego, z danymi autora (unikamy N+1)
    comments = event.comments.select_related('author').order_by('created_at')
    comment_form = CommentForm()

    # Ankiety z opcjami i głosami – prefetch_related pobiera wszystko w 2 zapytaniach SQL
    polls = event.polls.prefetch_related('options__votes').all()
    # Formularz tworzenia ankiety tylko dla organizatora
    poll_form = PollCreateForm() if event.user == request.user else None

    # Słownik głosów zalogowanego użytkownika: {poll_id: option_id}
    user_votes = {}
    for poll in polls:
        vote = poll.votes.filter(user=request.user).first()
        if vote:
            user_votes[poll.id] = vote.option_id

    context = {
        'event': event,
        'participants': participants,
        'going_list': going_list,
        'maybe_list': maybe_list,
        'declined_list': declined_list,
        'user_rsvp': user_rsvp,
        'comments': comments,
        'comment_form': comment_form,
        'polls': polls,
        'poll_form': poll_form,
        'user_votes': user_votes,
        'is_organizer': (event.user == request.user),
    }
    return render(request, 'birthdays/event_detail.html', context)


@login_required
def event_create(request):
    """Tworzenie nowego wydarzenia; opcjonalnie z przypisanym solenizantem z URL (?friend=ID)"""
    initial = {}
    # Jeśli kliknięto "Zaplanuj wydarzenie" z karty znajomego, wypełniamy pole solenizanta
    friend_id = request.GET.get('friend')
    if friend_id:
        initial['friend'] = friend_id

    if request.method == 'POST':
        form = EventForm(request.POST, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            # Organizator automatycznie dostaje status "going" (będę obecny)
            EventParticipant.objects.create(event=event, user=request.user, status='going')
            messages.success(request, f'Pomyślnie utworzono wydarzenie: {event.title}!')
            return redirect('birthdays:event_detail', pk=event.pk)
    else:
        form = EventForm(user=request.user, initial=initial)

    return render(request, 'birthdays/event_form.html', {
        'form': form,
        'title': 'Zaplanuj nowe wydarzenie',
        'btn_text': 'Zapisz wydarzenie'
    })


@login_required
def event_update(request, pk):
    """Edycja wydarzenia – dostępna tylko dla jego organizatora"""
    event = get_object_or_404(Event, pk=pk, user=request.user)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Zaktualizowano wydarzenie: {event.title}!')
            return redirect('birthdays:event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event, user=request.user)

    return render(request, 'birthdays/event_form.html', {
        'form': form,
        'event': event,
        'title': f'Edycja: {event.title}',
        'btn_text': 'Zapisz zmiany'
    })


@login_required
def event_delete(request, pk):
    """Usuwanie wydarzenia z bazy danych – tylko organizator może to zrobić"""
    event = get_object_or_404(Event, pk=pk, user=request.user)
    if request.method == 'POST':
        title = event.title
        event.delete()
        messages.info(request, f'Usunięto wydarzenie: {title}.')
        return redirect('birthdays:event_list')

    return render(request, 'birthdays/event_confirm_delete.html', {'event': event})


# ==============================================================================
# ZAPISY (RSVP), KOMENTARZE I GŁOSOWANIE (Etap 5)
# ==============================================================================

@login_required
def event_rsvp(request, pk):
    """Obsługa deklaracji obecności (going / maybe / declined / remove)"""
    event = get_object_or_404(
        Event.objects.filter(Q(user=request.user) | Q(is_public=True)),
        pk=pk
    )
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['going', 'maybe', 'declined']:
            # update_or_create: jeśli rekord istnieje – zmienia status, jeśli nie – tworzy nowy
            participant, created = EventParticipant.objects.update_or_create(
                event=event,
                user=request.user,
                defaults={'status': status}
            )
            labels = {
                'going': 'Zadeklarowano obecność na wydarzeniu.',
                'maybe': 'Zaznaczono status: Być może.',
                'declined': 'Zgłoszono brak możliwości uczestnictwa.'
            }
            messages.success(request, labels.get(status, 'Zaktualizowano status.'))
        elif status == 'remove':
            # Usunięcie wpisu RSVP z tabeli EventParticipant
            EventParticipant.objects.filter(event=event, user=request.user).delete()
            messages.info(request, 'Wycofano Twoją deklarację uczestnictwa.')

    return redirect('birthdays:event_detail', pk=event.pk)


@login_required
def event_comment_add(request, pk):
    """Publikacja nowego komentarza pod wydarzeniem"""
    event = get_object_or_404(
        Event.objects.filter(Q(user=request.user) | Q(is_public=True)),
        pk=pk
    )
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            # commit=False pozwala ręcznie przypisać event i autora przed zapisem do bazy
            comment = form.save(commit=False)
            comment.event = event
            comment.author = request.user
            comment.save()
            messages.success(request, 'Twój komentarz został opublikowany!')
        else:
            messages.error(request, 'Wpisz treść komentarza przed wysłaniem.')

    return redirect('birthdays:event_detail', pk=event.pk)


@login_required
def event_comment_delete(request, pk, comment_pk):
    """Usuwanie komentarza – może to zrobić jego autor LUB organizator wydarzenia"""
    event = get_object_or_404(Event, pk=pk)
    comment = get_object_or_404(EventComment, pk=comment_pk, event=event)

    # Sprawdzenie uprawnień przed usunięciem
    if comment.author == request.user or event.user == request.user:
        comment.delete()
        messages.info(request, 'Komentarz został usunięty.')
    else:
        messages.error(request, 'Nie masz uprawnień do usunięcia tego komentarza.')

    return redirect('birthdays:event_detail', pk=event.pk)


@login_required
def event_poll_create(request, pk):
    """Tworzenie nowej ankiety – wyłącznie przez organizatora wydarzenia"""
    event = get_object_or_404(Event, pk=pk, user=request.user)
    if request.method == 'POST':
        form = PollCreateForm(request.POST)
        if form.is_valid():
            poll = form.save(commit=False)
            poll.event = event
            poll.save()
            # Opcje wpisane w polu tekstowym: każda linia = jedna opcja głosowania
            options = form.cleaned_data['options_text']
            for opt_text in options:
                PollOption.objects.create(poll=poll, text=opt_text)
            messages.success(request, f'Pomyślnie utworzono głosowanie: „{poll.question}”!')
        else:
            messages.error(request, 'Błąd w ankiecie. Podaj pytanie oraz co najmniej dwie opcje w nowej linii.')

    return redirect('birthdays:event_detail', pk=event.pk)


@login_required
def event_poll_vote(request, pk, poll_pk):
    """Oddanie lub zmiana głosu w ankiecie (jeden głos na użytkownika per ankieta)"""
    event = get_object_or_404(
        Event.objects.filter(Q(user=request.user) | Q(is_public=True)),
        pk=pk
    )
    # Pobieramy ankietę tylko jeśli jest aktywna (is_active=True)
    poll = get_object_or_404(EventPoll, pk=poll_pk, event=event, is_active=True)

    if request.method == 'POST':
        option_id = request.POST.get('option_id')
        if option_id:
            option = get_object_or_404(PollOption, pk=option_id, poll=poll)
            # update_or_create: umożliwia zmianę głosu – jeden głos per użytkownik per ankieta
            PollVote.objects.update_or_create(
                poll=poll,
                user=request.user,
                defaults={'option': option}
            )
            messages.success(request, f'Twój głos na „{option.text}” został zapisany!')
        else:
            messages.warning(request, 'Wybierz jedną z opcji przed zatwierdzeniem głosu.')

    return redirect('birthdays:event_detail', pk=event.pk)


