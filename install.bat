@echo off
title UART Terminal - Instalator
echo ========================================
echo   UART Terminal - Instalator Windows
echo ========================================
echo.

:: Sprawdz czy Python jest zainstalowany
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [BLAD] Python nie jest zainstalowany!
    echo Pobierz Python 3 z https://www.python.org/downloads/
    echo Pamiataj o zaznaczeniu "Add Python to PATH" podczas instalacji.
    pause
    exit /b 1
)

echo [OK] Python znaleziony:
python --version
echo.

:: Instaluj pyserial
echo Instalowanie pyserial...
pip install pyserial
if %errorlevel% neq 0 (
    echo [BLAD] Nie udalo sie zainstalowac pyserial.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Instalacja zakonczona!
echo ========================================
echo.
echo Uruchom aplikacje komenda:
echo   python uart_terminal.py
echo.
echo Lub skompilowac do .exe:
echo   pip install pyinstaller
echo   pyinstaller --onefile --windowed uart_terminal.py
echo.
pause
