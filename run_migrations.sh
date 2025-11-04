#!/bin/bash

# Django Migration Commands
echo "Creating and running Django migrations for Governorate model..."

cd /c/Users/mus_2/GitHub/TawfirProject

# Activate virtual environment
source venv/Scripts/activate

# Create migrations
python manage.py makemigrations

# Show migration plan
python manage.py showmigrations

# Apply migrations
python manage.py migrate

echo "Migrations complete!"
echo "You can now add governorates in Django Admin"
