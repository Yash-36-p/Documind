#!/usr/bin/env bash
# Start Celery Worker for DocuMind
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "Starting Celery worker for DocuMind..."
venv/bin/celery -A config worker -l INFO --concurrency=2
