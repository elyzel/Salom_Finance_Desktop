@echo off
chcp 65001 >nul
cd /d "%~dp0"
cls
color 0F

echo.
echo  ================================================
echo         KET FINANCE - Controle Financeiro
echo  ================================================
echo.
echo  Localizando Python...
echo.

REM Tentar encontrar o Python correto
set PYTHON_EXE=python

REM Verificar se existe o Python 3.14 especifico
if exist "C:\Users\Administrador\AppData\Local\Python\pythoncore-3.14-64\python.exe" (
    set PYTHON_EXE=C:\Users\Administrador\AppData\Local\Python\pythoncore-3.14-64\python.exe
    echo  [OK] Python 3.14 encontrado!
) else (
    echo  [INFO] Usando Python do PATH
)

echo.
echo  ------------------------------------------------
echo   Verificando dependencias...
echo  ------------------------------------------------
echo.

set FALTANDO=0

%PYTHON_EXE% -c "import customtkinter" 2>nul
if errorlevel 1 (set FALTANDO=1 & call :vermelho "  [FALTA]  CustomTkinter") else (call :verde "  [OK]     CustomTkinter")

%PYTHON_EXE% -c "import matplotlib" 2>nul
if errorlevel 1 (set FALTANDO=1 & call :vermelho "  [FALTA]  Matplotlib   ") else (call :verde "  [OK]     Matplotlib   ")

%PYTHON_EXE% -c "import pandas" 2>nul
if errorlevel 1 (set FALTANDO=1 & call :vermelho "  [FALTA]  Pandas       ") else (call :verde "  [OK]     Pandas       ")

%PYTHON_EXE% -c "import openpyxl" 2>nul
if errorlevel 1 (set FALTANDO=1 & call :vermelho "  [FALTA]  OpenPyXL     ") else (call :verde "  [OK]     OpenPyXL     ")

%PYTHON_EXE% -c "import pytz" 2>nul
if errorlevel 1 (set FALTANDO=1 & call :vermelho "  [FALTA]  PyTZ         ") else (call :verde "  [OK]     PyTZ         ")

%PYTHON_EXE% -c "import dateutil" 2>nul
if errorlevel 1 (set FALTANDO=1 & call :vermelho "  [FALTA]  DateUtil     ") else (call :verde "  [OK]     DateUtil     ")

echo.
color 0F

if %FALTANDO%==1 (
    echo  ------------------------------------------------
    echo   Dependencias faltando! Instalando agora...
    echo  ------------------------------------------------
    echo.
    %PYTHON_EXE% -m pip install -r requirements.txt --quiet
    echo.
    echo   Instalacao concluida!
    echo.
)

echo  ------------------------------------------------
echo   Tudo pronto! Abrindo o Ket Finance...
echo  ------------------------------------------------
echo.
timeout /t 1 >nul

%PYTHON_EXE% main.py
goto :eof

:verde
color 0A
echo %~1
color 0F
goto :eof

:vermelho
color 0C
echo %~1
color 0F
goto :eof
