# UCS Terminal

**UART Command Sender** — graficzny terminal do wysyłania komend UART na wybranym porcie szeregowym.

![Windows](https://img.shields.io/badge/Windows-0078D4?style=flat&logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)

## Pobierz

📦 **[Pobierz najnowszą wersję ze stronu Releases →](https://github.com/YOUR_USERNAME/ucs-terminal/releases/latest)**

Wystarczy rozpakować ZIP i uruchomić `UCS_Terminal.exe`. Bez instalacji, bez Pythona.

---

## Funkcje

- Wybór portu COM i prędkości (9600–921600 baud)
- Wysyłanie komend: pojedynczo, sekwencyjnie lub w pętli
- Lista komend z edycją i zapisem/ładowaniem z pliku JSON
- Monitorowanie RX/TX z timestamp i kolorowaniem
- Eksport logów do pliku TXT
- Automatyczny reconnect przy utracie połączenia
- Konfiguracja wielu urządzeń (zapis/ładowanie profilów)

---

## Jak zbudować samemu

### Wymagania
- Python 3.12+
- Windows 10/11

### Kompilacja

```bash
pip install pyserial pyinstaller
pyinstaller --onefile --name "UCS_Terminal" --windowed uart_terminal.py
```

Plik znajdziesz w `dist/UCS_Terminal.exe`.

### Automatyczna kompilacja przez GitHub Actions

1. Wrzuć kod na GitHub
2. Kliknij **Actions** → **Build Windows .exe** → **Run workflow**
3. Po zakończeniu pobierz `UCS_Terminal.zip` z **Artifacts**

---

## Jak używać

1. Podłącz urządzenie UART do portu USB komputera
2. Uruchom `UCS_Terminal.exe`
3. Wybierz port COM i prędkość → kliknij **Connect**
4. Dodaj komendy do listy → kliknij **Send** lub uruchom sekwencję
5. Odpowiedzi urządzenia pojawią się w oknie logu

---

## Konfiguracja

Ustawienia i listy komend można zapisać do pliku JSON i wczytać przy następnym uruchomieniu.

```bash
# Przykładowy plik konfiguracyjny (uart_config.json)
{
  "port": "COM3",
  "baudrate": 115200,
  "commands": [
    {"cmd": "AT\r", "label": "Test AT"},
    {"cmd": "ATI\r", "label": "Info"}
  ]
}
```
