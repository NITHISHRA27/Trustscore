@echo off
REM One-time setup (uses your existing .venv if present)
if not exist .venv python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist .env copy .env.example .env
echo.
echo Setup complete. Optional: install Tesseract OCR and add it to PATH.
echo Start the app with start_app.bat
