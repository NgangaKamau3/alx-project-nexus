@echo off
echo Migrating schema to Neon PostgreSQL...
echo.

REM Apply migrations to Neon database
python manage.py migrate

echo.
echo Migration complete!
pause
