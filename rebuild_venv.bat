@echo off
SET "VENV_DIR=venv"
SET "REQ_FILE=requirements.txt"

echo Checking virtual environment...

IF EXIST "%VENV_DIR%\pyenv.cfg" (
    echo venv exists and looks healthy.
) ELSE (
    echo venv missing or broken. Rebuilding...
    IF EXIST "%VENV_DIR%" (
        rmdir /s /q "%VENV_DIR%"
    )
    python -m venv "%VENV_DIR%"
)

echo Activating venv...
call "%VENV_DIR%\Scripts\activate.bat"

echo Upgrading pip and wheel...
pip install --upgrade pip setuptools wheel

REM Use a workaround to avoid ELSE parsing issues
IF EXIST "%REQ_FILE%" (
    echo installing from %REQ_FILE%...
    pip install -r "%REQ_FILE%"
) 
IF NOT EXIST "%REQ_FILE%" (
    echo No requirements.txt found. Skipping pip install.
)

echo Environment ready!
pause
