#!/bin/bash
set -e

echo "🚀 Starting Boosty Uzbekistan application..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
python << END
import sys
import time
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boosty_project.settings')
django.setup()

from django.db import connection
from django.db.utils import OperationalError

max_attempts = 30
attempt = 0

while attempt < max_attempts:
    try:
        connection.ensure_connection()
        print("✅ Database is ready!")
        sys.exit(0)
    except OperationalError:
        attempt += 1
        print(f"⏳ Attempt {attempt}/{max_attempts}: Database not ready yet, waiting...")
        time.sleep(2)

print("❌ Database connection failed after maximum attempts")
sys.exit(1)
END

# Run migrations
echo "📦 Running database migrations..."
python manage.py migrate --noinput

# Check if data exists (check if there are any users)
echo "🔍 Checking if sample data exists..."
USER_COUNT=$(python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.count())" 2>/dev/null || echo "0")

if [ "$USER_COUNT" -eq "0" ]; then
    echo "📝 No users found. Creating sample data..."
    python manage.py create_sample_data --creators 5 --users 10 --posts 30 --comments 80
    echo "✅ Sample data created successfully!"
else
    echo "✅ Data already exists (${USER_COUNT} users found). Skipping sample data creation."
fi

# Start the Django development server
echo "🌟 Starting Django development server..."
exec python manage.py runserver 0.0.0.0:8000

