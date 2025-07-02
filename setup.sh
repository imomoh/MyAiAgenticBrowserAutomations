#!/bin/bash

# AI Browser Agent Setup Script
# This script sets up the project for development and running

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🤖 AI Browser Agent Setup"
echo "=========================="

# Check if Make is available
if ! command -v make &> /dev/null; then
    echo "❌ Make is not installed. Please install it first:"
    echo "   macOS: brew install make"
    echo "   Ubuntu/Debian: sudo apt-get install make"
    echo "   Windows: Install via Chocolatey or WSL"
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.9"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo "❌ Python 3.9 or higher is required. Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Check if Chrome is installed
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null && ! command -v chrome &> /dev/null; then
    echo "⚠️  Chrome browser not detected. Please install Google Chrome for browser automation."
    echo "   You can continue setup, but you'll need Chrome to run the agent."
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your OpenAI API key before running the agent."
    echo "   Required: OPENAI_API_KEY=your_openai_api_key_here"
fi

# Build the project
echo "🔨 Building project..."
make build

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "Quick Start Commands:"
echo "  make run                              # Start interactive mode"
echo "  make run-execute TASK=\"your task\"    # Execute single task"
echo "  make clean                            # Clean up everything"
echo ""
echo "⚠️  Don't forget to:"
echo "  1. Add your OpenAI API key to .env file"
echo "  2. Install Google Chrome if not already installed"
echo ""
echo "📚 Run 'make help' to see all available commands"