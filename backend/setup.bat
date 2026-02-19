@echo off
echo Starting Nexus Chat Backend Setup...

echo.
echo 1. Starting PostgreSQL with Docker...
cd ..
docker-compose up -d

echo.
echo 2. Creating virtual environment...
cd backend
if not exist venv (
    python -m venv venv
)

echo.
echo 3. Activating virtual environment...
venv\Scripts\activate

echo.
echo 4. Installing dependencies...
pip install -r requirements.txt

echo.
echo 5. Creating environment file...
if not exist .env (
    copy .env.example .env
    echo Please edit .env file with your settings
)

echo.
echo 6. Running database migrations...
python manage.py makemigrations
python manage.py migrate

echo.
echo 7. Creating superuser...
python manage.py createsuperuser

echo.
echo 8. Starting development server...
python manage.py runserver

pause
