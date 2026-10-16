@echo off
rem Wrapper so install.ps1 can be double-clicked / run despite the execution policy.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
pause
