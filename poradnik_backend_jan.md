# KOMPLETNY PORADNIK OBRONY PROJEKTU: BACKEND
**Projekt:** UrodzinkiApp (System organizacji urodzin, wydarzeń i ankiet)  
**Rola:** BACKEND DEVELOPER  
**Autor:** Jan Zaborowski (nr albumu: 31401)  
**Prowadząca laboratoria:** dr inż. Ewa Adamus  

---

## 1. TWOJA ROLA W PROJEKCIE
Jako Backend Developer odpowiadasz za:
1. **Architekturę bazy danych i modele (ORM Django)**: Zaprojektowanie 7 powiązanych relacjami tabel (`Friend`, `Event`, `EventParticipant`, `EventComment`, `EventPoll`, `PollOption`, `PollVote`).
2. **Logikę biznesową i kontrolery widoków (`views.py`)**: Izolacja danych na poziomie użytkownika (`request.user`), ochrona tras dekoratorem `@login_required`, obsługa operacji CRUD, zapytań POST i przekierowań.
3. **Optymalizację zapytań SQL**: Eliminacja problemu N+1 za pomocą `select_related()` (dla relacji `ForeignKey`) oraz `prefetch_related()` (dla relacji odwrotnych i list opcji/głosów).
4. **Formularze i walidację (`forms.py`)**: `ModelForm`, walidatory pól (np. `clean_options_text`), rozszerzenie `UserCreationForm`.
5. **Testy jednostkowe (`tests.py`)**: Pełny zestaw 8 automatycznych testów jednostkowych pokrywających logikę modeli, autoryzację i wszystkie mechanizmy Etapu 5.
6. **Panel administracyjny (`admin.py`)**: Konfiguracja modeli w Django Admin z polskimi nagłówkami kolumn, filtrami i wyszukiwarką.

---

## 2. MAPA TWOICH PLIKÓW I STRUKTURA KODU

### A. Modele bazodanowe (`birthdays/models.py`)
W projekcie zdefiniowano 7 kluczowych modeli:

1. **`Friend` (Kontakty / Jubilaci)**:
   * Pola: `user` (FK do User), `first_name`, `last_name`, `birth_date`, `email`, `phone_number`, `notes`.
   * Właściwości obliczeniowe (`@property`):
     * `next_birthday`: Oblicza najbliższe urodziny. Posiada zabezpieczenie na 29 lutego w latach nieprzestępnych (`except ValueError -> replace(day=28)`).
     * `days_until_birthday`: Zwraca liczbę dni pozostałych do urodzin `(self.next_birthday - date.today()).days`.
     * `current_age`: Wylicza bieżący wiek osoby na podstawie daty dzisiejszej.
     * `upcoming_age`: Wiek, jaki osoba osiągnie w najbliższe urodziny.
     * `is_today`: Zwraca `True`, jeśli `days_until_birthday == 0`.

2. **`Event` (Wydarzenia i imprezy okolicznościowe)**:
   * Pola: `user` (organizator, FK), `friend` (opcjonalny solenizant, FK z `on_delete=models.SET_NULL`), `title`, `event_type` (wybór z `EVENT_TYPE_CHOICES`), `date`, `time`, `location`, `description`, `budget`, `is_public`.
   * Właściwości: `days_until`, `is_today`, `is_past`, `is_upcoming`, `is_soon`.

3. **`EventParticipant` (Uczestnicy i deklaracje RSVP)**:
   * Pola: `event` (FK), `user` (FK), `status` (`going` / `maybe` / `declined`), `joined_at`.
   * Ograniczenie unikalności: `unique_together = ('event', 'user')` – gwarantuje na poziomie bazy danych, że jeden użytkownik może mieć dokładnie jedną deklarację na dane wydarzenie (nie da się zdublować wpisu).

4. **`EventComment` (Dyskusja pod wydarzeniem)**:
   * Pola: `event` (FK), `author` (FK), `content`, `created_at`, `updated_at`.

5. **`EventPoll`, `PollOption`, `PollVote` (System ankiet i głosowania)**:
   * `EventPoll`: pytanie ankiety (`question`), flaga `is_active`. Metoda `@property total_votes` zwraca sumę wszystkich głosów.
   * `PollOption`: tekst opcji (`text`), `votes_count` (liczba głosów na tę opcję), `percentage()` (oblicza procent: `(votes_count / total_votes) * 100`).
   * `PollVote`: oddany głos (`poll`, `option`, `user`). Ograniczenie `unique_together = ('poll', 'user')` wymusza zasadę **1 głos na użytkownika w danej ankiecie**.

---

### B. Kontrolery i logika biznesowa (`birthdays/views.py`)
Plik zorganizowany w 4 czytelne sekcje:

1. **Autoryzacja i profil użytkownika**:
   * `register_view`: Obsługuje `RegisterForm`. Po udanej walidacji tworzy konto (`form.save()`) i od razu wywołuje funkcję `login(request, user)`.
   * `login_view`: Używa `AuthenticationForm` i `authenticate(username, password)`. Obsługuje parametr powrotu `next`.
   * `logout_view`: Wywołuje `logout(request)` i przekierowuje do logowania.
   * `profile_view`: Edycja danych zalogowanego użytkownika (`UserProfileUpdateForm`).

2. **Pulpit i zarządzanie kontaktami (CRUD)**:
   * `dashboard`: Pobiera tylko kontakty zalogowanego użytkownika: `Friend.objects.filter(user=request.user)`. Sortuje w pamięci po `days_until_birthday` i dzieli na: dzisiaj, 7 dni, 30 dni. Pobiera też najbliższe imprezy (`date__gte=today`).
   * `friend_list`: Wyszukiwanie wielopolowe przy użyciu obiektów `Q`:
     ```python
     friends.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query) | ...)
     ```
   * `friend_create`: Zapis z użyciem `commit=False`:
     ```python
     friend = form.save(commit=False)
     friend.user = request.user
     friend.save()
     ```
   * `friend_update` & `friend_delete`: Używają `get_object_or_404(Friend, pk=pk, user=request.user)`, co uniemożliwia podglądanie i edycję cudzych kontaktów.

3. **Kalendarz (`calendar_view`)**:
   * Wykorzystuje standardowy moduł Pythona `calendar.Calendar(firstweekday=0)`.
   * Generuje strukturę `monthdays2calendar(year, month)` i mapuje do słowników: `days_map[dzień]` (urodziny) oraz `events_map[dzień]` (imprezy).

4. **Wydarzenia, RSVP, Ankiety i Komentarze (Etap 5)**:
   * `event_list`: Pobiera wydarzenia własne LUB publiczne:
     ```python
     Event.objects.filter(Q(user=request.user) | Q(is_public=True)).distinct()
     ```
   * `event_detail`: Optymalizacja zapytań SQL:
     * `participants.select_related('user')` (jedno zapytanie SQL zamiast N).
     * `polls.prefetch_related('options__votes')` (pobiera ankiety, opcje i powiązane głosy w zaledwie 2 zapytaniach).
   * `event_rsvp`: Wykorzystuje bezpieczną metodę Django ORM:
     ```python
     participant, created = EventParticipant.objects.update_or_create(
         event=event, user=request.user, defaults={'status': status}
     )
     ```
   * `event_poll_vote`: Zastosowanie `update_or_create` na modelu `PollVote`, co pozwala użytkownikowi zmienić zdanie i zagłosować na inną opcję, nie tworząc duplikatu głosu.
   * `event_comment_delete`: Weryfikacja uprawnień: komentarz może usunąć wyłącznie jego autor LUB organizator całego wydarzenia.

---

### C. Formularze (`birthdays/forms.py`)
* `EventForm`: Zdefiniowane widgety z klasami Bootstrapa oraz dynamiczne filtrowanie listy solenizantów w `__init__`:
  ```python
  if user:
      self.fields['friend'].queryset = Friend.objects.filter(user=user)
  ```
* `PollCreateForm`: Własne pole `options_text` (Textarea). W metodzie `clean_options_text()` tekst jest rozbijany na linie, sprawdzany pod kątem pustych znaków oraz weryfikowany warunek minimum 2 opcji do wyboru.
* `RegisterForm`: Dziedziczy po `UserCreationForm`, dodając wymagane pole email oraz opcjonalne imię i nazwisko.

---

### D. Testy automatyczne (`birthdays/tests.py`)
Zestaw 8 testów uruchamiany komendą:
```bash
python manage.py test
```
**Pokrycie testowe:**
1. `test_friend_properties`: Poprawność wyliczania wieku i odliczania dni do urodzin.
2. `test_event_properties`: Sprawdzenie flag `is_upcoming` i `is_past`.
3. `test_login_required_protection`: Weryfikacja kodu HTTP 302 i przekierowania do `/login/` dla niezalogowanego gościa.
4. `test_authenticated_event_list`: Potwierdzenie, że zalogowany użytkownik widzi własne imprezy w kodzie HTML odpowiedzi (kod 200).
5. `test_event_crud_flow`: Test dodania imprezy przez POST i weryfikacja jej obecności w bazie (`Event.objects.count()`).
6. `test_event_rsvp`: Test deklaracji obecności na wydarzeniu przez POST (`status='going'`).
7. `test_event_comment`: Test opublikowania komentarza przez innego użytkownika.
8. `test_event_poll_and_voting`: Test utworzenia ankiety, oddania głosu oraz sprawdzenia metody `percentage()` (100% dla wybranej opcji, 0% dla drugiej).

---

## 3. JAK PRZEDSTAWIĆ PROJEKT PROWADZĄCEJ (SCENARIUSZ PREZENTACJI BACKENDU)

### Krok 1: Wstęp architektoniczny
* **Co powiedzieć:**
  > „Dzień dobry. Jako Backend Developer odpowiadałem za modelowanie relacyjnej bazy danych, logikę biznesową w widokach, autoryzację użytkowników, walidację danych oraz testy jednostkowe. Całość zrealizowana jest w architekturze MVT (Model-View-Template) oferowanej przez Django.”

### Krok 2: Uruchomienie testów jednostkowych
* Otwórz terminal i wpisz:
  ```bash
  python manage.py test
  ```
* Pokaż wynik: `Ran 8 tests in ... OK`.
* **Co powiedzieć:**
  > „Projekt posiada pełny zestaw 8 testów automatycznych pokrywających autoryzację, izolację danych, kalkulacje wiekowe oraz wszystkie elementy Etapu 5 – zapisy RSVP, komentarze i głosowanie w ankietach.”

### Krok 3: Wyjaśnienie modeli i relacji (Etap 5)
* Otwórz `birthdays/models.py`.
* Wskaż modele `EventParticipant` oraz `PollVote`.
* **Co powiedzieć:**
  > „W modelach Etapu 5 kluczowe było zagwarantowanie integralności danych. W modelu `EventParticipant` oraz `PollVote` zastosowałem regułę `unique_together`. Dzięki temu na poziomie bazy danych Postgres/SQLite niemożliwe jest zdublowanie głosu przez jednego użytkownika w tej samej ankiecie. Z kolei w modelu `PollOption` zaimplementowałem metodę `percentage()`, która dynamicznie wylicza procent głosów na podstawie relacji odwrotnej.”

### Krok 4: Bezpieczeństwo i optymalizacja w widokach
* Otwórz `birthdays/views.py` i wskaż funkcję `event_detail`.
* **Co powiedzieć:**
  > „W widokach zadbałem o dwie kwestie:
  > 1. **Bezpieczeństwo**: Wszystkie widoki prywatne posiadają dekorator `@login_required`, a zapytania filtrują obiekty po `user=request.user`.
  > 2. **Wydajność bazy danych**: W widoku `event_detail` zastosowałem `select_related('user')` dla uczestników oraz `prefetch_related('options__votes')` dla ankiet. Dzięki temu uniknęliśmy problemu N+1 zapytań SQL przy renderowaniu listy uczestników i wyników głosowania.”

---

## 4. NAJCZĘSTSZE PYTANIA PROWADZĄCEJ I TWOJE ODPOWIEDZI

#### Pytanie 1: *„Co to jest problem N+1 zapytań i jak go rozwiązaliście w projekcie?”*
* **Co otworzyć:** `birthdays/views.py` (linie w funkcji `event_detail`).
* **Twoja odpowiedź:**
  > „Problem N+1 pojawia się, gdy po pobraniu N obiektów (np. 10 uczestników) pętla w szablonie odpytuje bazę danych o powiązanego użytkownika (`p.user.username`) osobnym zapytaniem dla każdego wiersza. Wtedy wykonuje się 1 + N zapytań SQL. Rozwiązałem to za pomocą `select_related('user')`, co powoduje wykonanie zapytania SQL z klauzulą `JOIN`. Natomiast dla relacji 'wiele do wielu' i relacji odwrotnych w ankietach użyłem `prefetch_related('options__votes')`, co pobiera powiązane obiekty w zaledwie 2 zapytaniach.”

#### Pytanie 2: *„Jak zapobiegacie wielokrotnemu głosowaniu przez tego samego użytkownika?”*
* **Co otworzyć:** `birthdays/models.py` (klasa `PollVote`) oraz `birthdays/views.py` (`event_poll_vote`).
* **Twoja odpowiedź:**
  > „Na poziomie modelu `PollVote` zdefiniowaliśmy ograniczenie `unique_together = ('poll', 'user')`. Z kolei w widoku `event_poll_vote` używamy metody `PollVote.objects.update_or_create(poll=poll, user=request.user, defaults={'option': option})`. Jeśli użytkownik głosuje po raz pierwszy – tworzy się nowy wpis. Jeśli klika inną opcję – jego poprzedni głos zostaje po prostu zaktualizowany.”

#### Pytanie 3: *„Jak obsługujecie sytuację, gdy ktoś urodził się 29 lutego w roku przestępnym?”*
* **Co otworzyć:** `birthdays/models.py` (właściwość `next_birthday` w modelu `Friend`).
* **Twoja odpowiedź:**
  > „Standardowe wywołanie `birth_date.replace(year=today.year)` rzuciłoby wyjątek `ValueError` w roku nieprzestępnym. Przechwyciliśmy ten wyjątek w bloku `except ValueError:` i w takim roku przypisujemy datę urodzin na 28 lutego. Dzięki temu aplikacja nigdy nie rzuca błędu serwera 500.”

#### Pytanie 4: *„Do czego służy `commit=False` w formularzach Django?”*
* **Co otworzyć:** `birthdays/views.py` (funkcja `friend_create` lub `event_create`).
* **Twoja odpowiedź:**
  > „`form.save(commit=False)` tworzy instancję modelu w pamięci Pythona, ale nie wykonuje jeszcze instrukcji SQL `INSERT` do bazy danych. Daje nam to możliwość uzupełnienia pól, których użytkownik nie wpisuje w formularzu – w naszym przypadku przypisujemy zalogowanego użytkownika jako właściciela rekordu: `instance.user = request.user`, a następnie wywołujemy `instance.save()`.”

#### Pytanie 5: *„Gdzie skonfigurowana jest baza danych i język polski?”*
* **Co otworzyć:** `config/settings.py`.
* **Twoja odpowiedź:**
  > „W pliku `settings.py`:
  > * `LANGUAGE_CODE = 'pl'` – zapewnia polskie komunikaty walidacji w formularzach i panelu admina.
  > * `TIME_ZONE = 'Europe/Warsaw'` – prawidłowe strefy czasowe dla dat i godzin wydarzeń.
  > * `DATABASES` – domyślny silnik SQLite (`db.sqlite3`), który jest bezobsługowy i idealnie sprawdza się w środowisku laboratoryjnym oraz na PythonAnywhere.”

---

## 5. SŁOWNICZEK POJĘĆ DLA BACKENDU
* **ORM (Object-Relational Mapping)**: Warstwa Django mapująca tabele relacyjnej bazy danych na klasy Pythona (`models.Model`), eliminująca konieczność ręcznego pisania zapytań SQL.
* **QuerySet**: Kolekcja obiektów pobranych z bazy (np. `Friend.objects.filter(...)`). Jest 'leniwa' (lazy) – zapytanie SQL do bazy wykonywane jest dopiero w momencie iteracji lub rzutowania na listę.
* **select_related**: Metoda QuerySet wykonująca `SQL JOIN`. Stosowana przy relacjach jeden-do-jednego i kluczach obcych (`ForeignKey`).
* **prefetch_related**: Metoda wykonująca osobne zapytanie SQL i łącząca obiekty w pamięci Pythona. Stosowana przy relacjach wiele-do-wielu i relacjach odwrotnych.
* **update_or_create**: Metoda sprawdzająca, czy rekord o podanych kryteriach istnieje – jeśli tak, aktualizuje pola w `defaults`, jeśli nie – tworzy nowy rekord.
* **unique_together**: Ograniczenie unikalności nałożone na kombinację dwóch lub więcej kolumn w tabeli bazy danych.
* **MVT (Model - View - Template)**: Wzorzec architektoniczny Django, w którym Model zarządza danymi, View logiką biznesową, a Template prezentacją.
