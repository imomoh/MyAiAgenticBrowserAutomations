# Setup Guide

This guide provides detailed instructions for setting up the AI Browser Agent on different platforms.

## Table of Contents

- [System Requirements](#system-requirements)
- [Platform-Specific Setup](#platform-specific-setup)
- [Installation Steps](#installation-steps)
- [Configuration](#configuration)
- [Verification](#verification)
- [Common Issues](#common-issues)

## System Requirements

### Minimum Requirements
- **Python**: 3.9 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB free space
- **Internet**: Active connection for AI API calls

### Browser Requirements
- **Chrome**: Latest stable version (automatically managed by webdriver-manager)
- **ChromeDriver**: Automatically downloaded and managed

### API Requirements
- **OpenAI API Key**: Required for AI functionality
- **API Credits**: Ensure sufficient credits for usage

## Platform-Specific Setup

### macOS

1. **Install Python:**
   ```bash
   # Using Homebrew (recommended)
   brew install python@3.11
   
   # Or download from python.org
   # https://www.python.org/downloads/
   ```

2. **Install Chrome:**
   ```bash
   # Using Homebrew
   brew install --cask google-chrome
   
   # Or download from chrome.google.com
   ```

3. **Install Git (if not already installed):**
   ```bash
   brew install git
   ```

### Linux (Ubuntu/Debian)

1. **Install Python:**
   ```bash
   sudo apt update
   sudo apt install python3.11 python3.11-venv python3-pip
   ```

2. **Install Chrome:**
   ```bash
   wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
   sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
   sudo apt update
   sudo apt install google-chrome-stable
   ```

3. **Install Git:**
   ```bash
   sudo apt install git
   ```

### Windows

1. **Install Python:**
   - Download from [python.org](https://www.python.org/downloads/)
   - ⚠️ **Important**: Check "Add Python to PATH" during installation

2. **Install Chrome:**
   - Download from [chrome.google.com](https://www.google.com/chrome/)

3. **Install Git:**
   - Download from [git-scm.com](https://git-scm.com/download/win)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ai-browser-agent.git
cd ai-browser-agent
```

### 2. Create Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Set Up Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your configuration
# On macOS/Linux:
nano .env

# On Windows:
notepad .env
```

### 5. Configure OpenAI API Key

Edit the `.env` file and add your OpenAI API key:

```env
OPENAI_API_KEY=your_actual_api_key_here
```

**How to get an OpenAI API Key:**
1. Visit [platform.openai.com](https://platform.openai.com)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste it into your `.env` file

## Configuration

### Environment Variables

The `.env` file contains all configuration options:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Agent Configuration
AGENT_NAME=BrowserAgent
AGENT_DESCRIPTION=AI agent for browser automation
MAX_RETRIES=3
TIMEOUT_SECONDS=30

# Browser Configuration  
BROWSER_TYPE=chrome
HEADLESS_MODE=false
WINDOW_WIDTH=1920
WINDOW_HEIGHT=1080
USER_DATA_DIR=./chrome_data

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/agent.log
LOG_FORMAT=json

# Security
ALLOWED_DOMAINS=*
BLOCKED_DOMAINS=

# Development
DEBUG=false
DEVELOPMENT_MODE=false
```

### Configuration Options Explained

#### Browser Settings
- `BROWSER_TYPE`: Currently only supports "chrome"
- `HEADLESS_MODE`: Set to "true" for background operation
- `WINDOW_WIDTH/HEIGHT`: Browser window dimensions
- `USER_DATA_DIR`: Chrome profile data location

#### Logging Settings
- `LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `LOG_FORMAT`: "json" for structured logs, "text" for readable format

#### Security Settings
- `ALLOWED_DOMAINS`: Comma-separated list or "*" for all
- `BLOCKED_DOMAINS`: Comma-separated list of blocked domains

## Verification

### 1. Test Installation

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Test the CLI
python -m src.main --help
```

Expected output:
```
Usage: python -m src.main [OPTIONS] COMMAND [ARGS]...

  AI Browser Agent - Automate browser tasks with AI

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  config       Show current configuration
  execute      Execute a single browser automation task
  interactive  Start interactive mode for continuous task execution
  serve        Start the agent as a web service (future implementation)
  setup-guide  Generate setup instructions
```

### 2. Test Configuration

```bash
python -m src.main config
```

This should display your current configuration without errors.

### 3. Test Browser Integration

```bash
# Test headless mode (won't open browser window)
python -m src.main execute --task "take a screenshot" --headless
```

### 4. Test AI Integration

```bash
# Test with a simple navigation task
python -m src.main execute --task "navigate to google.com" --headless
```

### 5. Test Interactive Mode

```bash
python -m src.main interactive
```

Then type `quit` to exit.

## Post-Installation Setup

### 1. Development Tools (Optional)

For development and contributing:

```bash
# Install development dependencies
pip install -e .

# Set up pre-commit hooks
pre-commit install

# Run tests to verify everything works
pytest tests/
```

### 2. Make Commands (Optional)

The project includes a Makefile for common tasks:

```bash
# View available commands
make help

# Run all tests
make test

# Check code quality
make quality

# Format code
make format
```

### 3. IDE Setup (Optional)

**VS Code:**
1. Install Python extension
2. Select the virtual environment as Python interpreter
3. Install recommended extensions (shown in workspace)

**PyCharm:**
1. Open project folder
2. Configure Python interpreter to use the virtual environment
3. Enable code formatting with Black

## Common Issues

### Chrome Driver Issues

**Problem**: Chrome driver not found or incompatible version
```
selenium.common.exceptions.WebDriverException: Message: 'chromedriver' executable needs to be in PATH
```

**Solution**: The webdriver-manager should handle this automatically. If issues persist:
```bash
# Force update Chrome driver
pip install --upgrade webdriver-manager
```

### Permission Issues (macOS)

**Problem**: Chrome automation blocked by security settings

**Solution**: 
1. System Preferences → Security & Privacy → Privacy
2. Add Terminal to "Accessibility" and "Automation" lists
3. Allow Terminal to control System Events

### Python Path Issues (Windows)

**Problem**: Python not found in PATH

**Solution**: 
1. Reinstall Python with "Add to PATH" checked
2. Or manually add Python to PATH environment variable

### Virtual Environment Issues

**Problem**: Cannot activate virtual environment

**Solution**:
```bash
# Remove and recreate virtual environment
rm -rf venv  # On Windows: rmdir /s venv
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### OpenAI API Issues

**Problem**: Authentication errors or quota exceeded

**Solution**:
1. Verify API key is correct and active
2. Check billing and usage at platform.openai.com
3. Ensure sufficient credits are available

### Network/Firewall Issues

**Problem**: Cannot connect to OpenAI API or download dependencies

**Solution**:
1. Check internet connection
2. Configure proxy settings if behind corporate firewall
3. Add exceptions for:
   - api.openai.com
   - pypi.org
   - github.com

## Next Steps

After successful setup:

1. Read the [Usage Tutorial](USAGE.md)
2. Explore [API Reference](API.md)
3. Check out [Example Use Cases](USAGE.md#example-use-cases)
4. Review [Architecture Documentation](ARCHITECTURE.md)

## Getting Help

If you encounter issues not covered here:

1. Check [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Search [GitHub Issues](https://github.com/your-username/ai-browser-agent/issues)
3. Create a new issue with:
   - Operating system and version
   - Python version
   - Error messages and logs
   - Steps to reproduce