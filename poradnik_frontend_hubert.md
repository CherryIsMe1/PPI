# KOMPLETNY PORADNIK OBRONY PROJEKTU: FRONTEND
**Projekt:** UrodzinkiApp (System organizacji urodzin, wydarzeń i ankiet)  
**Rola:** FRONTEND DEVELOPER  
**Autor:** Hubert Jakubowski (nr albumu: 32037)  
**Prowadząca laboratoria:** dr inż. Ewa Adamus  

---

## 1. TWOJA ROLA W PROJEKCIE
Jako Frontend Developer odpowiadasz za:
1. **Warstwę wizualną i UI/UX**: Zaprojektowanie i wdrożenie nowoczesnego, czytelnego, ciemnego interfejsu (*Cyberpunk Slate / Dark Mode*).
2. **Strukturę szablonów Django (DTL - Django Template Language)**: Dziedziczenie szablonów (`{% extends 'base.html' %}`), bloki (`{% block content %}`), pętle (`{% for %}`), warunki (`{% if %}`) oraz filtry dat i formatowania (`|date:"d.m.Y"`, `|default:""`).
3. **Responsywność (RWD)**: Pełne dopasowanie interfejsu do komputerów, tabletów i telefonów (Bootstrap 5 Grid System: `col-12`, `col-md-6`, `col-lg-4`).
4. **Interaktywne komponenty Bootstrap 5**: Karty (`card`), paski postępu ankiet (`progress-bar`), modale, odznaki (`badge`), formularze, rozwijane panele (`collapse`).
5. **Dedykowany arkusz CSS**: `static/css/custom.css` – zmienne CSS (`:root`), gradienty, spójna wysokość przycisków w navbarze (38px), równe kółka statystyk (56x56px), zapobieganie problemom z pamięcią podręczną przeglądarki (cache-busting).

---

## 2. MAPA TWOICH PLIKÓW (CO GDZIE JEST)

### A. Arkusz stylów CSS
* `static/css/custom.css`:
  * **Zmienne kolorów (`:root`)**: Definicja ciemnego tła (`--cyber-bg: #070b10`), powierzchni kart (`--cyber-card: #101924`), neonowego cyjanu (`--omi-cyan: #00f0ff`), fioletu (`--omi-purple: #a855f7`) i zieleni akcentowej (`--omi-green`).
  * **Pasek nawigacji (`.cyber-navbar`)**: Efekt rozmycia tła (`backdrop-filter: blur(12px)`), sztywna wysokość przycisków `height: 38px !important;` dla równego ułożenia.
  * **Kółka statystyk (`.stat-icon-circle`)**: Wymiary `56px x 56px`, `border-radius: 50%`, `flex-shrink: 0` – gwarantujące, że ikony nigdy się nie spłaszczają na małych ekranach.
  * **Pigułki odznak (`.badge-cyber-pill`)**: Ciemne tło `#0b131c` z wyrazistym błękitnym tekstem `#38bdf8`, zapewniające czytelność WCAG.
  * **Animacja dzisiejszych urodzin (`@keyframes pulse-cyber`)**: Delikatne pulsowanie czerwonego badge'a „TO DZISIAJ!”.
  * **Siatka kalendarza (`.calendar-cell`)**: Komórki kalendarza o minimalnej wysokości 110px z wyróżnieniem dnia dzisiejszego neonową ramką.

### B. Szablony wspólne (layout)
* `templates/base.html`:
  * Główny szkielet strony HTML5.
  * Podpięcie Bootstrap 5 (CDN), Bootstrap Icons oraz Google Fonts (*Chakra Petch* i *Inter*).
  * Podpięcie `custom.css` z parametrem wersji: `{% static 'css/custom.css' %}?v=2.2` (mechanizm Cache-Busting – dzięki temu przeglądarka prowadzącej zawsze pobierze najświeższy plik CSS bez wciskania Ctrl+F5).
  * Dołączenie paska nawigacji (`{% include 'navbar.html' %}`), komunikatów flash (`{% include 'messages.html' %}`) oraz stopki (`{% include 'footer.html' %}`).
* `templates/navbar.html`:
  * Górne menu aplikacji.
  * Warunkowe renderowanie: jeśli użytkownik jest zalogowany (`{% if user.is_authenticated %}`) – widoczne linki do Pulpitu, Znajomych, Kalendarza, Wydarzeń, przycisk „+ Dodaj”, profil oraz Wyloguj. Jeśli gość – przyciski Logowanie i Rejestracja.
* `templates/messages.html`:
  * Dynamiczne alerty Bootstrapa (`alert-success`, `alert-danger`, `alert-info`) wyświetlające komunikaty wysyłane z backendu (np. „Dodano jubilata”, „Zapisano głos”).
* `templates/footer.html`:
  * Stopka z nazwą aplikacji oraz stopką autorów z numerami albumów.

### C. Szablony widoków aplikacji (`birthdays/templates/birthdays/`)
1. `dashboard.html` (Pulpit):
   * 4 kafelki podsumowujące: Łącznie znajomych, Urodziny dzisiaj, Urodziny w 7 dni, Zaplanowane imprezy.
   * Czerwony baner ostrzegawczy renderowany tylko gdy ktoś ma dziś urodziny (`{% if today_birthdays %}`).
   * Dwie sekcje pod spodem: Ostatnio dodani znajomi oraz Najbliższe imprezy z szybkimi akcjami.
2. `friend_list.html` (Lista znajomych):
   * Formularz wyszukiwarki tekstowej oraz select do sortowania (po dacie, po nazwisku, po wieku).
   * Tabela kontaktów z wyróżnieniem wieku (`{{ friend.current_age }} lat`), daty urodzin oraz odliczania dni.
   * Przyciski akcji w wierszu tabeli: Edycja (ołówek) oraz Usuń (kosz).
3. `friend_form.html` (Dodawanie / Edycja jubilata):
   * Uniwersalny formularz w wyśrodkowanej karcie Bootstrapa.
   * Pola formularza (`{{ form.first_name }}`, itp.) stylizowane klasami `.form-control`.
4. `friend_confirm_delete.html` (Potwierdzenie usunięcia jubilata):
   * Bezpieczny ekran ostrzegawczy z czerwoną ramką przed wykonaniem żądania POST usuwającego rekord.
5. `calendar.html` (Kalendarz):
   * Pigułki nawigacyjne miesięcy (Styczeń – Grudzień) z licznikiem osób w danym miesiącu.
   * Miesięczna siatka 7-kolumnowa (Poniedziałek – Niedziela) z kafelkami dni, oznaczaniem dzisiejszego dnia oraz etykietami urodzin i imprez.
6. `event_list.html` (Lista wydarzeń):
   * Kafelki filtrów: Wszystkie, Nadchodzące, Zakończone, Moje imprezy, Imprezy w których biorę udział.
   * Wyszukiwarka imprez po nazwie, miejscu lub solenizancie.
   * Lista kafelkowa wydarzeń z oznaczeniem daty, godziny, składki budżetowej i statusu.
7. `event_detail.html` (**Główny ekran Etapu 5 – wizytówka projektu**):
   * Nagłówek wydarzenia z odznakami typu imprezy oraz czasem do wydarzenia.
   * Kafelki parametrów: Termin, Lokalizacja, Budżet / Składka na osobę.
   * **Moduł RSVP**: 3 przyciski wyboru statusu (Będę obecny / Być może / Nie mogę) z dynamicznym podświetleniem aktywnego wyboru oraz liczbowe podsumowanie obecności.
   * **Moduł Głosowań / Ankiet**: Pytanie ankiety, opcje jako radio-buttony, przycisk oddania głosu oraz animowane paski postępu (`.progress-bar`) z procentowym i liczbowym udziałem głosów.
   * **Moduł Komentarzy**: Pole wpisania wiadomości, lista komentarzy z datą, awatarem autora i możliwością usunięcia wpisu przez autora lub organizatora.
8. `login.html` & `register.html`:
   * Eleganckie, wycentrowane karty autoryzacji z ikonami tarczy i klucza.
9. `profile.html`:
   * Karta użytkownika, statystyki utworzonych kontaktów i imprez oraz formularz edycji danych osobowych.

---

## 3. JAK PRZEDSTAWIĆ PROJEKT PROWADZĄCEJ (SCENARIUSZ PREZENTACJI FRONTENDU)

### Krok 1: Otwórz stronę główną i zaloguj się
* Pokaż czysty, ciemny interfejs.
* **Co powiedzieć:**
  > „Dzień dobry. Jako Frontend Developer odpowiadałem za zaprojektowanie i wdrożenie kompletnej warstwy wizualnej w aplikacji UrodzinkiApp. Zbudowałem spójny system w oparciu o Bootstrap 5, własny arkusz CSS oraz system szablonów Django (DTL). Interfejs powstał w estetyce Dark Cyberpunk, z dbałością o kontrast, czytelność danych i pełną responsywność.”

### Krok 2: Pulpit główny (Dashboard)
* Wskaż 4 kafelki na samej górze.
* **Co powiedzieć:**
  > „Na pulpicie głównym stworzyłem kafelki statystyczne. Każdy kafelek ma zdefiniowaną sztywną ikonę w klasie `.stat-icon-circle` (56x56px), dzięki czemu układ nie ulega deformacji przy skalowaniu ekranu. Jeśli w bazie pojawi się jubilat mający urodziny w dniu dzisiejszym, szablon dynamicznie wyświetla pulsujący czerwony alert dzięki regule `@keyframes pulse-cyber`.”

### Krok 3: Lista znajomych i Kalendarz
* Kliknij w menu „Znajomi”, a potem „Kalendarz”.
* **Co powiedzieć:**
  > „W widoku listy znajomych wdrożyłem tabelę z wyszukiwarką i filtrami sortowania. Zadbałem o czytelne odznaki wieku i dni do urodzin. Z kolei w widoku Kalendarza wykorzystałem Bootstrapowe zakładki (`nav-pills`), w których dynamicznie wyświetlam polskie nazwy miesięcy wraz z liczbą jubilatów, a pod spodem responsywną 7-kolumnową siatkę dni z zaznaczeniem dzisiejszej daty.”

### Krok 4: Wydarzenie – Szczegóły, RSVP, Ankiety i Komentarze (Etap 5)
* Wejdź w dowolne wydarzenie (np. „21. urodziny Adama”).
* **Co powiedzieć:**
  > „To jest najbardziej rozbudowany widok w aplikacji – `event_detail.html`. Zintegrowałem tutaj trzy kluczowe mechanizmy interaktywne:
  > 1. **Deklaracje obecności (RSVP)**: Użytkownik jednym kliknięciem wybiera status. Aktywny status podświetla się odpowiednim kolorem (zielony, żółty, czerwony), a pod spodem wyświetlamy listę potwierdzonych osób z pigułkami obecności.
  > 2. **Ankiety z głosowaniem**: Wyniki głosowań prezentowane są w postaci dynamicznych pasków postępu (`progress-bar`), gdzie szerokość w procentach jest wyliczana i wstrzykiwana bezpośrednio przez DTL (`style="width: {{ opt.percentage }}%"`).
  > 3. **Wątek dyskusji**: Karty komentarzy z przypisanym autorem, znacznikiem organizatora i czasem dodania.”

---

## 4. NAJCZĘSTSZE PYTANIA PROWADZĄCEJ I TWOJE ODPOWIEDZI

#### Pytanie 1: *„W jaki sposób zorganizowane jest dziedziczenie szablonów w Waszym projekcie?”*
* **Co otworzyć:** `templates/base.html` oraz `birthdays/templates/birthdays/dashboard.html`.
* **Twoja odpowiedź:**
  > „Stosujemy wzorzec nadrzędnego szablonu `base.html`. Znajduje się tam cała sekcja `<head>`, importy stylów, skryptów oraz stałe elementy interfejsu: navbar, kontener na komunikaty flash i footer. Wszystkie podstrony dziedziczą ten szkielet za pomocą tagu `{% extends 'base.html' %}` i nadpisują dedykowane bloki, głównie `{% block content %}` oraz opcjonalnie `{% block title %}`.”

#### Pytanie 2: *„Dlaczego macie szablony w dwóch różnych miejscach: `templates/` i `birthdays/templates/`?”*
* **Twoja odpowiedź:**
  > „To oficjalny standard Django (tzw. namespacing szablonów). W folderze głównym `templates/` trzymamy elementy globalne dla całego projektu (`base.html`, `navbar.html`, `footer.html`, `messages.html`). Natomiast szablony widoków powiązane ściśle z logiką danej aplikacji umieszczamy w jej podkatalogu `birthdays/templates/birthdays/`. Dzięki temu unikamy konfliktów nazw szablonów, gdybyśmy dodali kolejne aplikacje.”

#### Pytanie 3: *„Jak radzicie sobie z pamięcią podręczną przeglądarki (cache) przy zmianach w pliku CSS?”*
* **Co otworzyć:** `templates/base.html` (linia 18).
* **Twoja odpowiedź:**
  > „Zastosowałem technikę Cache-Bustingu. W tagu linkującym styl dopisuję parametr wersji: `<link rel="stylesheet" href="{% static 'css/custom.css' %}?v=2.2">`. Gdy zmieniam wersję w parametrze query string, przeglądarka klienta natychmiast wie, że należy pobrać świeży plik z serwera, zamiast korzystać ze starej wersji z dysku.”

#### Pytanie 4: *„Jak zrobiliście animowane paski postępu w ankietach?”*
* **Co otworzyć:** `birthdays/templates/birthdays/event_detail.html` (okolice linii 275-285).
* **Twoja odpowiedź:**
  > „Użyłem komponentu Bootstrap 5 `.progress` oraz `.progress-bar`. Z backendu model dostarcza metodę `percentage()`, która wylicza udział procentowy danych głosów. W szablonie przypisuję tę wartość bezpośrednio do atrybutu liniowego: `style="width: {{ opt.percentage }}%"` oraz do atrybutów dostępności `aria-valuenow`. Dodatkowo nadałem paskom gradient z palety projektu łączący błękit z fioletem.”

#### Pytanie 5: *„Czy strona jest w pełni responsywna (RWD)?”*
* **Twoja odpowiedź:**
  > „Tak. Całość opiera się na 12-kolumnowym systemie siatki Bootstrapa (`row` i `col-12 col-md-6 col-lg-4`). Tabele są owinięte w klasę `.table-responsive`, dzięki czemu na telefonach nie rozpychają ekranu, lecz dają możliwość płynnego przewijania poziomego. Ponadto navbar zwija się w hamburger menu (`navbar-toggler`) na mniejszych ekranach.”

---

## 5. SŁOWNICZEK POJĘĆ DLA FRONTENDU
* **DTL (Django Template Language)**: Silnik szablonów Django – pozwala łączyć statyczny HTML z dynamicznymi danymi z Pythona za pomocą tagów `{% ... %}` oraz zmiennych `{{ ... }}`.
* **Cache-Busting**: Wymuszanie odświeżenia pliku statycznego przez zmianę parametru wersji w adresie URL (`custom.css?v=2.2`).
* **CSS Custom Properties (`:root`)**: Zmienne CSS (np. `var(--cyber-bg)`), umożliwiające centralną zmianę całej palety kolorystycznej serwisu w jednym miejscu.
* **Bootstrap 5**: Najpopularniejszy framework CSS/JS do szybkiego tworzenia responsywnych interfejsów opartych na flexboxie i 12-kolumnowej siatce.
* **Flexbox**: Model układu CSS służący do wyrównywania i rozmieszczania elementów w kontenerze (np. `d-flex align-items-center justify-content-between`).
