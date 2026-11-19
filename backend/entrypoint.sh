#!/bin/bash
set -e

echo "=== DocuMind Container Initialization ==="

# If PostgreSQL is configured, wait for it to be ready
if [ -n "$DB_HOST" ]; then
  echo "Waiting for PostgreSQL at $DB_HOST:${DB_PORT:-5432}..."
  while ! nc -z "$DB_HOST" "${DB_PORT:-5432}"; do
    sleep 1
  done
  echo "PostgreSQL is ready!"
fi

# Run database migrations
if [ "$RUN_MIGRATIONS" != "false" ]; then
  echo "Applying database migrations..."
  python manage.py migrate --noinput

  # Seed initial demo data if configured
  if [ "$SEED_DATA" = "true" ]; then
    echo "Seeding initial demo users and documents..."
    python manage.py seed_data || true
  fi
fi

# Collect static files
if [ "$COLLECT_STATIC" = "true" ]; then
  echo "Collecting static files..."
  python manage.py collectstatic --noinput
fi

echo "Starting process: $@"
exec "$@"
