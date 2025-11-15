#!/bin/bash

# Setup script for Face Recognition Attendance System
# For macOS

echo "========================================="
echo "Face Recognition Attendance System Setup"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Failed to install dependencies."
    echo "If you're on Apple Silicon (M1/M2/M3), try installing cmake first:"
    echo "  brew install cmake"
    exit 1
fi

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p static/enrolled_faces
mkdir -p static/attendance_images
mkdir -p data/logs

# Check if running on Apple Silicon
echo ""
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    echo "Detected Apple Silicon (M1/M2/M3)."
    echo "InsightFace models will be downloaded on first run."
    echo "This may take a few minutes on initial startup."
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "To start the application:"
echo "  1. Activate the virtual environment:"
echo "     source .venv/bin/activate"
echo "  2. Run the application:"
echo "     python app.py"
echo "  3. Open your browser and navigate to:"
echo "     http://localhost:5000"
echo ""
echo "For detailed instructions, see README.md"
echo ""
