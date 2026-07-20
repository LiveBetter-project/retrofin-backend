#!/bin/sh

set -eu

# Wait for postgres to be ready
echo "Waiting for PostgreSQL..."

while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.1
done

echo "PostgreSQL started"

# Apply committed migrations and collect Django/admin static assets.
python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
