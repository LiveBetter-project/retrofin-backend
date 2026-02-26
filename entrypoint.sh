#!/bin/bash

# Wait for postgres to be ready
echo "Waiting for PostgreSQL..."

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done

echo "PostgreSQL started"

# Run migrations
python manage.py makemigrations --noinput
python manage.py migrate --noinput

exec "$@"