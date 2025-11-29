#!/bin/bash

echo "=========================================="
echo "Movie Recommendation API Setup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "Warning: PostgreSQL is not installed. Please install PostgreSQL 13 or higher."
fi

# Check if Redis is installed
if ! command -v redis-cli &> /dev/null; then
    echo "Warning: Redis is not installed. Please install Redis 6 or higher."
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Copy .env.example to .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo ""
    echo "Important: Please edit .env file with your configuration:"
    echo "  - Add your TMDb API key"
    echo "  - Configure database credentials"
    echo "  - Update other settings as needed"
    echo ""
fi

# Create logs directory
echo "Creating logs directory..."
mkdir -p logs

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Create PostgreSQL database: createdb movie_recommendation_db"
echo "3. Start Redis server: redis-server"
echo "4. Run migrations: python manage.py migrate"
echo "5. Create superuser: python manage.py createsuperuser"
echo "6. Start server: python manage.py runserver"
echo ""
echo "API Documentation will be available at: http://localhost:8000/api/docs/"
echo ""
