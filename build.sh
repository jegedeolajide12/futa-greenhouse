#!/bin/bash
# Build script for Render

echo "Building the project..."

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations (only if you want them to run automatically)
python manage.py migrate

echo "Build complete."