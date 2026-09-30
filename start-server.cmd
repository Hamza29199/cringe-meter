@echo off
rem Starts the local Cringe Meter server (port 8780). Leave this window open while you use the meter.
rem It prints nothing until the model has loaded (up to a minute), then: "Cringe Meter on http://127.0.0.1:8780/"
cd /d "%~dp0"
".venv\Scripts\python.exe" server.py %*
pause
