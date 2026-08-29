#!/bin/bash
echo "Building the project..."

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate --noinput

# Create superuser (if it doesn't exist)
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
user, created = User.objects.get_or_create(
    username='Lekan',
    defaults={
        'email': 'jegedeolajide1@gmail.com',
        'is_superuser': True,
        'is_staff': True
    }
)
if created:
    user.set_password('Test@1234')
    user.save()
    print("Superuser created.")
else:
    print("Superuser already exists.")
EOF

echo "Build complete."