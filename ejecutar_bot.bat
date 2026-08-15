@echo off
title Rey Taco Picks Bot 6.0
color 0E
echo ============================================================
echo      TACO REY TACO PICKS 6.0 - EJECUTOR LOCAL PLAYDOIT
echo ============================================================
echo.
cd /d "%~dp0backend"
echo [1/2] Iniciando escaneo profundo en Playdoit con Google Chrome...
python scraper.py
echo.
echo [2/2] Proceso completado. Revisa tu web y canal de Telegram.
echo ============================================================
pause
