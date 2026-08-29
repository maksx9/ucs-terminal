# UART Terminal - Instalator dla Windows
# Uruchom jako Administrator (kliknij prawym -> Uruchom jako Administrator)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  UART Terminal - Instalator Windows     " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Sprawdz czy Python jest zainstalowany
$python = Get-Command python* -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $python) {
    Write-Host "[BLAD] Python nie jest zainstalowany!" -ForegroundColor Red
    Write-Host "Pobierz Python 3 z https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Pamiataj o zaznaczeniu 'Add Python to PATH' podczas instalacji." -ForegroundColor Yellow
    pause
    exit
}

Write-Host "[OK] Python: $($python.Source)" -ForegroundColor Green
Write-Host ""

# Instaluj pyserial
Write-Host "Instalowanie pyserial..." -ForegroundColor Yellow
& $python.Source -m pip install pyserial
if ($LASTEXITCODE -ne 0) {
    Write-Host "[BLAD] Nie udalo sie zainstalowac pyserial." -ForegroundColor Red
    pause
    exit
}

Write-Host "[OK] pyserial zainstalowany." -ForegroundColor Green
Write-Host ""

# Zainstaluj PyInstaller (opcjonalnie)
$installPyInstaller = Read-Host "Czy chcesz zainstalowac PyInstaller aby skompilowac .exe? (t/n)"
if ($installPyInstaller -eq 't') {
    Write-Host "Instalowanie PyInstaller..." -ForegroundColor Yellow
    & $python.Source -m pip install pyinstaller
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] PyInstaller zainstalowany." -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Instalacja zakonczona!                 " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Mozesz teraz uruchomic aplikacje:" -ForegroundColor White
Write-Host '  python uart_terminal.py' -ForegroundColor Yellow
Write-Host ""
Write-Host "Lub skompilowac do .exe:" -ForegroundColor White
Write-Host '  pyinstaller --onefile --windowed uart_terminal.py' -ForegroundColor Yellow
Write-Host ""
pause
