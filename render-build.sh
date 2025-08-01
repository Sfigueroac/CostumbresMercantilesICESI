#!/usr/bin/env bash
# Render build script

set -o errexit  # Exit on error

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create database if it doesn't exist
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully!')
"
