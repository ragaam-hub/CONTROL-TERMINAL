@echo off
REM Build CONTROL TERMINAL jadi .exe (jalankan di Windows yang sudah ada Python 3)
python -m pip install --upgrade pyinstaller
python -m PyInstaller --onefile --noconsole --name ControlTerminal control_terminal.py
echo.
echo Selesai! File ada di folder dist\ControlTerminal.exe
pause
