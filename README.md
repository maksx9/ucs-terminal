# UCS Terminal 2.3

**UART Command Sender** — nowoczesny graficzny terminal do komunikacji i automatyzacji komend UART na wybranym porcie szeregowym.

![Windows](https://img.shields.io/badge/Windows-0078D4?style=flat&logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)

## Pobierz

📦 **[Pobierz najnowszą wersję UCS_Terminal (Windows x64) →](https://github.com/maksx9/ucs-terminal/releases)**

Wystarczy pobrać i uruchomić `UCS_Terminal.exe`. Bez instalacji, bez konieczności posiadania Pythona.

---

## Najważniejsze funkcje (v2.3)

- **Nowoczesny interfejs (Fluent UI):** Zaokrąglone karty i przyciski, przełączniki suwakowe, obsługa High-DPI oraz wybór motywu (**Jasny / Ciemny Indygo**).
- **Tryb Uproszczony i Zaawansowany:** Szybkie przełączanie widoku w prawym górnym rogu — ukrywa lub odkrywa parametry inżynierskie (`Format 8N1`, `DTR/RTS`, `HEX`, `Koniec linii`, `Szukaj`, `Etykiety`).
- **Wbudowana Instrukcja Obsługi:** Dostępny pod ręką przewodnik opisujący każdą funkcję programu.
- **Sekwencje i Makra Komend:** Wysyłanie pojedyncze (`▶`), jednorazowe wykonanie listy lub praca w pętli (`Loop`) z indywidualnym czasem oczekiwania (`ms`) oraz możliwością włączania/wyłączania poszczególnych pozycji.
- **Monitor RX/TX z czasem do milisekund:** Kolorowanie kierunków transmisji, podgląd **ASCII / HEX**, filtrowanie w czasie rzeczywistym oraz licznik przesłanych bajtów.
- **Obsługa znaków końca linii i ramek binarnych:** Wybór `LF (\n)`, `CRLF (\r\n)`, `CR (\r)` lub `Brak` oraz wysyłanie ciągów szesnastkowych (`HEX`).
- **Auto-Reconnect:** Automatyczne wznawianie połączenia po chwilowym odłączeniu przejściówki USB-UART.
- **Zapis i eksport:** Profile konfiguracyjne `JSON` oraz eksport logów do plików `TXT` i `CSV`.

---

## Budowanie ze źródeł

```bash
pip install pyserial pyinstaller
pyinstaller --onefile --name "UCS_Terminal" --windowed --icon="assets/UCS_Terminal.ico" --add-data "assets;assets" --noupx uart_terminal.py
```
