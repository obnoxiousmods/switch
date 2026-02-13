@echo off
title swdl launcher
REM This batch file is used to launch the swdl application using uvicorn.
uvicorn app.main:app --host 0.0.0 --port 6069 --reload
pause