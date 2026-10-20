@echo off
cd /d "%~dp0iva_key_app\src"
start "" "%~dp0..\..\..\.venv\Scripts\pythonw.exe" main.py
