@echo off
title MO KHOA TUONG LUA WINDOWS - THPT SO 2 BAO YEN
color 1F
echo ================================================================
echo   DANG XIN QUYEN QUAN TRI DE MO KHOA TUONG LUA WINDOWS...
echo ================================================================
echo.
echo * Neu man hinh xuat hien hop thoai hoi:
echo   "Do you want to allow this app to make changes to your device?"
echo   ==^> Thay/Co hay bam [ YES ] (Dong y) nhe!
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process netsh -ArgumentList 'advfirewall firewall add rule name=StreamlitBanTru dir=in action=allow protocol=TCP localport=8501' -Verb RunAs -Wait"

echo.
echo ================================================================
echo   DA MO KHOA THANH CONG!
echo.
echo   Bao gio Thay/Co hay lay dien thoai (bat Wi-Fi):
echo   1. Mo trinh duyet Safari hoac Chrome
echo   2. Go dia chi: http://192.168.1.15:8501
echo ================================================================
echo.
pause
