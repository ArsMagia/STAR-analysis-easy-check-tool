@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Starting STAR Analysis System...
python star_gui.py
pause