@echo off
REM Run after start_backend.bat in a second window
call .venv\Scripts\activate
python -m app.frontend.app
