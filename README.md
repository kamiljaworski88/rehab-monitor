# Rehab Monitor

> Custom integration for Home Assistant — monitors free rehabilitation slots on the [Intermedicus](https://erj.intermedicus.pl) portal and displays them in a dedicated Lovelace card.

![HA Version](https://img.shields.io/badge/HA-2024.1%2B-blue)
![HACS](https://img.shields.io/badge/HACS-Custom-orange)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Funkcje

- Automatyczne sprawdzanie wolnych terminów rehabilitacyjnych w portalu Intermedicus
- Powiadomienia push przy pojawieniu się nowego wolnego terminu
- Własna karta Lovelace (`custom:rehab-monitor-card`) w stylu wizualnym HomePulse
- Konfigurowalny harmonogram skanowania (godziny aktywności + interwał)
- Filtr godzinowy wizyt (np. pokaż tylko terminy od 8:00)
- Obsługa dwóch lokalizacji: **Terapia Dzieci** i **SI** (lub obu naraz)
- Pełna obsługa trybu ciemnego i jasnego HA

---

## Wymagania

- Home Assistant **2024.1.0** lub nowszy
- Konto w portalu [erj.intermedicus.pl](https://erj.intermedicus.pl) (opcjonalne — bez logowania widoczne są terminy publiczne)
- [HACS](https://hacs.xyz) (zalecane) lub instalacja ręczna

---

## Instalacja przez HACS (zalecane)

1. Otwórz **HACS** w Home Assistant
2. Przejdź do menu **⋮ → Repozytoria niestandardowe**
3. Wpisz URL:
   ```
   https://github.com/kamiljaworski88/rehab-monitor
   ```
   i wybierz kategorię **Integration**
4. Kliknij **Dodaj**, wróć do HACS i wyszukaj **Rehab Monitor**
5. Zainstaluj i **uruchom ponownie Home Assistant**
6. Zrób **Ctrl+Shift+R** w przeglądarce (rejestracja zasobu Lovelace)

---

## Instalacja ręczna

1. Pobierz zawartość folderu `custom_components/rehab_monitor/` z tego repozytorium
2. Skopiuj go do `<config>/custom_components/rehab_monitor/`
3. Uruchom ponownie Home Assistant

---

## Konfiguracja

Po restarcie HA:

1. Przejdź do **Ustawienia → Urządzenia i usługi → Dodaj integrację**
2. Wyszukaj **Rehab Monitor**
3. Wypełnij formularz:

| Pole | Opis | Wymagane |
|------|------|----------|
| Login | Login do portalu Intermedicus | Nie |
| Hasło | Hasło do portalu | Nie |
| Serwis powiadomień | Np. `mobile_app_moj_telefon` | Nie |
| Place ID — Terapia | ID lokalizacji (domyślny: `30`) | Tak |
| Place ID — SI | ID lokalizacji SI (domyślny: `31`) | Tak |

> **Tip:** Place ID możesz odczytać z DevTools przeglądarki podczas przeglądania strony z terminami w portalu Intermedicus (zakładka Network → FreeTermsFilter → payload `PlaceId`).

---

## Encje

Po skonfigurowaniu integracja tworzy następujące encje:

| Encja | Typ | Opis |
|-------|-----|------|
| `binary_sensor.rehab_dostepnosc` | Binary sensor | `on` gdy są wolne terminy |
| `sensor.rehab_wolne_terminy` | Sensor | Liczba wolnych terminów; atrybut `terminy` zawiera listę slotów |
| `switch.rehab_monitor_active` | Switch | Włącz / wyłącz monitorowanie |
| `select.rehab_miejsce` | Select | Wybór lokalizacji: *Terapia dzieci*, *SI*, *Oba* |
| `button.rehab_sprawdz_teraz` | Button | Natychmiastowe sprawdzenie (z pominięciem okna godzinowego) |
| `number.rehab_scan_interval` | Number | Interwał skanowania w minutach (5–120) |
| `number.rehab_hour_start` | Number | Godzina rozpoczęcia skanowania (0–23) |
| `number.rehab_hour_end` | Number | Godzina zakończenia skanowania (0–23) |
| `number.rehab_visit_hour_min` | Number | Ignoruj terminy wcześniejsze niż ta godzina (0 = brak filtra) |

---

## Karta Lovelace

Integracja automatycznie rejestruje kartę `custom:rehab-monitor-card` przy starcie HA.

Aby dodać kartę do dashboardu:

1. Otwórz edytor Lovelace
2. Kliknij **Dodaj kartę**
3. Wyszukaj **Rehab Monitor** lub wklej ręcznie:

```yaml
type: custom:rehab-monitor-card
title: Rehab Monitor
```

### Podgląd karty

```
┌─────────────────────────────────────────┐
│ 🏥 Rehab Monitor                   [🔄] │
├─────────────────────────────────────────┤
│  📅  2026-04-20  10:00                  │
│      👤 Kowalski Jan  ·  🏥 Terapia     │
│      ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓     │
├─────────────────────────────────────────┤
│  ✚  Monitorowanie              [ ● ]    │
│  📍 Szukaj miejsca    [Terapia dzieci ▾]│
├─────────────────────────────────────────┤
│  ˅  Harmonogram skanowania  co 15 min  │
└─────────────────────────────────────────┘
```

---

## Automatyzacje — przykład

```yaml
automation:
  - alias: "Powiadom o wolnym terminie rehab"
    trigger:
      - platform: state
        entity_id: binary_sensor.rehab_dostepnosc
        to: "on"
    action:
      - service: notify.mobile_app_moj_telefon
        data:
          title: "Wolny termin!"
          message: >
            {{ state_attr('sensor.rehab_wolne_terminy', 'terminy')
               | map(attribute='data') | list | join(', ') }}
```

---

## Rozwiązywanie problemów

**Karta nie pojawia się w edytorze Lovelace**
→ Uruchom ponownie HA, następnie zrób Ctrl+Shift+R w przeglądarce.

**Błąd `button.rehab_sprawdz_teraz` missing**
→ Integracja nie jest jeszcze skonfigurowana — przejdź do Ustawienia → Integracje i dodaj Rehab Monitor.

**Brak terminów mimo że portal pokazuje wolne miejsca**
→ Sprawdź Place ID w konfiguracji integracji (domyślne wartości mogą różnić się między placówkami).

**HTTP 400 przy skanowaniu**
→ Token CSRF wygasł — integracja odświeży go automatycznie przy następnym skanowaniu. Można też kliknąć przycisk „Sprawdź teraz".

---

## Licencja

MIT © [kamiljaworski88](https://github.com/kamiljaworski88)
