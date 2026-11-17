#!/usr/bin/env bash

# DocuMind One-Click Development Launch Script
# Starts Django REST API (port 8000) and React Vite Frontend (port 3000)

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=========================================================="
echo "      🚀 Launching DocuMind Intelligent Processing        "
echo "=========================================================="

# Ensure migrations are applied
echo "Checking backend database..."
backend/venv/bin/python backend/manage.py migrate --noinput

# Run seed data if needed
backend/venv/bin/python backend/manage.py seed_data

echo ""
echo "Starting Backend API on http://127.0.0.1:8000"
echo "Starting Frontend UI on http://localhost:3000"
echo "Swagger API Docs on http://127.0.0.1:8000/api/docs/"
echo ""

# Trap SIGINT to kill background jobs on exit
trap 'kill $(jobs -p) 2>/dev/null' EXIT

# Start backend server in background
(cd backend && venv/bin/python manage.py runserver 0.0.0.0:8000) &

# Start frontend dev server
(cd frontend && npx vite --port 3000 --host)

