#!/bin/bash
echo "Building the project..."

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate --noinput

# Create superuser (if it doesn't exist)
# Create superuser from environment variable
echo "from django.contrib.auth import get_user_model; User = get_user_model(); user, created = User.objects.get_or_create(username='admin', defaults={'email':'admin@example.com', 'is_superuser':True, 'is_staff':True}); if created: user.set_password('$ADMIN_PASSWORD'); user.save()" | python manage.py shell

echo "Build complete."