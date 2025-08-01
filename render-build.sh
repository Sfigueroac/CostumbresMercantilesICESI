#!/usr/bin/env bash
set -o errexit  # Exit on error

echo "🚀 Starting build process..."

# Update pip
echo "📦 Updating pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Dependencies installed successfully!"

# Note: Database tables will be created automatically when the app starts
echo "🗄️ Database will be initialized on first app start..."

echo "✨ Build completed successfully!"