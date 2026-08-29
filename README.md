# UCS Terminal

**UART Command Sender** — graficzny terminal do wysyłania komend UART na wybranym porcie szeregowym.

![Windows](https://img.shields.io/badge/Windows-0078D4?style=flat&logo=windows&logoColor=white)

## Pobierz

📦 **[Pobierz UCS_Terminal_v2.exe (Windows x64) →](https://github.com/maksx9/ucs-terminal/releases/download/v1.0.0/UCS_Terminal_v2.zip)**

Wystarczy rozpakować ZIP i uruchomić UCS_Terminal.exe. Bez instalacji, bez Pythona.

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

```bash
pip install pyserial pyinstaller
pyinstaller --onefile --name "UCS_Terminal" --windowed --icon=\"assets/UCS_Terminal.ico\" uart_terminal.py
```

---

## Plik konfiguracyjny

```json
{
  \"port\": \"COM3\",
  \"baudrate\": 115200,
  \"commands\": [
    {\"cmd\": \"AT\\r\", \"label\": \"Test AT\"}
  ]
}
```

