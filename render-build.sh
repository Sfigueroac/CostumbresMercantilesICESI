set -o errexit  # Exit on error

echo "🚀 Starting build process..."

# Update pip
echo "📦 Updating pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create database tables
echo "🗄️ Creating database tables..."
python -c "
import os
print(f'🌍 Environment: {os.environ.get(\"RENDER\", \"local\")}')
from app import app, db
with app.app_context():
    db.create_all()
    print('✅ Database tables created successfully!')
"

echo "✨ Build completed successfully!"