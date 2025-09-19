#!/bin/sh

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

exec python manage.py runserver 0.0.0.0:8000
