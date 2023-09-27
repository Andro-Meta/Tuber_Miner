@echo off
REM Create a virtual environment named "venv"
IF NOT EXIST "venv" (
    python -m venv venv
)

REM Activate the virtual environment and install dependencies
CALL venv\Scripts\activate.bat
pip install yt-dlp moviepy pyinstaller

REM Create an executable for the Python script
pyinstaller --onefile --windowed --icon=vs.ico Tube_Miner.py

REM Deactivate the virtual environment
CALL venv\Scripts\deactivate.bat

echo Setup complete!
pause
