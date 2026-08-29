# UCS Terminal

**UART Command Sender** — graficzny terminal do wysyłania komend UART na wybranym porcie szeregowym.

![Windows](https://img.shields.io/badge/Windows-0078D4?style=flat&logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)

## Pobierz

📦 **[Pobierz UCS_Terminal.exe (Windows x64) →](https://github.com/maksx9/ucs-terminal/releases/download/latest/UCS_Terminal.zip)**

Wystarczy rozpakować ZIP i uruchomić `UCS_Terminal.exe`. Bez instalacji, bez Pythona.

---

## Funkcje

- Wybór portu COM i prędkości (9600–921600 baud)
- Wysyłanie komend: pojedynczo, sekwencyjnie lub w pętli
- Lista komend z edycją i zapisem/ładowaniem z pliku JSON
- Monitorowanie RX/TX z timestamp i kolorowaniem
- Eksport logów do pliku TXT
- Automatyczny reconnect przy utracie połączenia

---

## Budowanie ze źródeł

### Windows
```bash
pip install pyserial pyinstaller
pyinstaller --onefile --name "UCS_Terminal" --windowed uart_terminal.py
```

### Automatycznie przez GitHub Actions
Każdy commit na `master` automatycznie buduje `.exe` — pobierz z **Actions** → **Build Windows .exe** → **Artifacts**.

---

## Plik konfiguracyjny

Ustawienia i listy komend można zapisać do pliku JSON.

```json
{
  "port": "COM3",
  "baudrate": 115200,
  "commands": [
    {"cmd": "AT\r", "label": "Test AT"},
    {"cmd": "ATI\r", "label": "Info"}
  ]
}
```
