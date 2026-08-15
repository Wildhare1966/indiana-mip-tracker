@echo off
rem MRD front-end local server.
rem Serves this folder at http://localhost:8778 so the app loads over http.
rem The app itself is at:  http://localhost:8778/mrd-ad682070b7/
rem
rem It must NOT be opened as file:// -- a file: page sends Origin: null, which
rem makes the Apps Script /exec POST redirect 404, and the page's CSP
rem (default-src 'self') cannot match a file: sibling, so styles.css and both
rem embedded dashboards are refused. See EVAL-REPORT_local-migration.md in the
rem private tracker repo.
rem
rem Idempotent: if something already listens on 8778 it starts nothing. Uses
rem python.exe with a hidden window - NOT pythonw, whose console-less stderr
rem (None) crashes http.server per request. Binds 127.0.0.1 only (not the LAN).
rem Run at login via the Startup-folder script (serve-mrd.vbs) or by hand.
cd /d "%~dp0"
powershell -NoProfile -Command "if(-not (Get-NetTCPConnection -LocalPort 8778 -State Listen -ErrorAction SilentlyContinue)){Start-Process -WindowStyle Hidden python -ArgumentList '-m','http.server','8778','--bind','127.0.0.1' -WorkingDirectory '%~dp0'}"
