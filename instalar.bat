@echo off
cd /d "%~dp0"

rem Usa o lancador "py" do Python oficial (python.org); o python do MSYS2 nao tem os pacotes de visao computacional
echo Criando ambiente Python...
py -3 -m venv .venv || goto erro
.venv\Scripts\python.exe -m pip install --upgrade pip || goto erro
.venv\Scripts\python.exe -m pip install -r requirements.txt || goto erro

echo.
echo Instalacao concluida. Use iniciar.bat para abrir o contador.
pause
exit /b 0

:erro
echo.
echo Falha na instalacao. Verifique se o Python de python.org esta instalado (comando "py").
pause
exit /b 1
