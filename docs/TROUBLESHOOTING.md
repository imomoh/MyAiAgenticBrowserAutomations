# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the AI Browser Agent.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Configuration Problems](#configuration-problems)
- [Browser Automation Issues](#browser-automation-issues)
- [AI Integration Problems](#ai-integration-problems)
- [Performance Issues](#performance-issues)
- [Error Messages](#error-messages)
- [Platform-Specific Issues](#platform-specific-issues)
- [Getting Help](#getting-help)

## Installation Issues

### Python Version Compatibility

**Problem**: Agent fails to start with Python version errors
```
ERROR: Python 3.8 is not supported. Please use Python 3.9 or higher.
```

**Solutions**:
1. **Check Python version**:
   ```bash
   python --version
   python3 --version
   ```

2. **Install correct Python version**:
   ```bash
   # macOS with Homebrew
   brew install python@3.11
   
   # Ubuntu/Debian
   sudo apt install python3.11 python3.11-venv
   
   # Windows: Download from python.org
   ```

3. **Use correct Python executable**:
   ```bash
   # Create venv with specific Python version
   python3.11 -m venv venv
   source venv/bin/activate
   ```

### Virtual Environment Issues

**Problem**: Cannot activate virtual environment or import errors

**Solutions**:
1. **Recreate virtual environment**:
   ```bash
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # OR
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

2. **Fix PATH issues (Windows)**:
   - Ensure Python is in system PATH
   - Use full path to Python executable
   - Check for spaces in Python installation path

3. **Permission issues (macOS/Linux)**:
   ```bash
   # Fix ownership
   sudo chown -R $USER:$USER /path/to/project
   
   # Fix permissions
   chmod +x venv/bin/activate
   ```

### Dependency Installation Failures

**Problem**: pip install fails with compilation errors

**Solutions**:
1. **Update pip and setuptools**:
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

2. **Install system dependencies**:
   ```bash
   # Ubuntu/Debian
   sudo apt install build-essential python3-dev
   
   # macOS
   xcode-select --install
   
   # Windows
   # Install Visual Studio Build Tools
   ```

3. **Use pre-compiled wheels**:
   ```bash
   pip install --only-binary=all -r requirements.txt
   ```

4. **Clear pip cache**:
   ```bash
   pip cache purge
   pip install --no-cache-dir -r requirements.txt
   ```

## Configuration Problems

### Environment Variable Issues

**Problem**: Configuration not loading or validation errors

**Diagnostic**:
```bash
# Check if .env file exists and is readable
ls -la .env
cat .env

# Test configuration loading
python -c "from src.config.settings import settings; print(settings.agent.openai_api_key[:8] + '...')"
```

**Solutions**:
1. **Fix .env file format**:
   ```env
   # Correct format
   OPENAI_API_KEY=sk-your-key-here
   HEADLESS_MODE=true
   
   # Incorrect format (don't use)
   OPENAI_API_KEY = "sk-your-key-here"  # No spaces around =
   HEADLESS_MODE="true"                 # No quotes for booleans
   ```

2. **Check file encoding**:
   ```bash
   file .env  # Should show ASCII or UTF-8
   ```

3. **Verify environment variable priority**:
   ```bash
   # Environment variables override .env file
   export OPENAI_API_KEY=your-key
   python -m src.main config
   ```

### OpenAI API Key Problems

**Problem**: Authentication errors or invalid API key

**Diagnostic**:
```bash
# Test API key directly
python -c "
import openai
client = openai.OpenAI(api_key='your-key-here')
try:
    models = client.models.list()
    print('API key is valid')
except Exception as e:
    print(f'API key error: {e}')
"
```

**Solutions**:
1. **Verify API key format**:
   - Should start with `sk-`
   - Should be exactly 51 characters long
   - No extra spaces or newlines

2. **Check API key status**:
   - Visit [platform.openai.com](https://platform.openai.com)
   - Verify key is active and has usage limits
   - Check billing status

3. **Test with minimal example**:
   ```python
   import openai
   client = openai.OpenAI(api_key="your-key")
   response = client.chat.completions.create(
       model="gpt-4",
       messages=[{"role": "user", "content": "Hello"}],
       max_tokens=10
   )
   print(response.choices[0].message.content)
   ```

## Browser Automation Issues

### Chrome Driver Problems

**Problem**: Chrome driver not found or version mismatch
```
selenium.common.exceptions.WebDriverException: Message: 'chromedriver' executable needs to be in PATH
```

**Solutions**:
1. **Let webdriver-manager handle it** (automatic):
   ```bash
   # Should work automatically, but if issues persist:
   pip uninstall webdriver-manager
   pip install webdriver-manager
   ```

2. **Manual driver management**:
   ```bash
   # Check Chrome version
   google-chrome --version
   
   # Download matching ChromeDriver from:
   # https://chromedriver.chromium.org/
   
   # Add to PATH or specify location
   export PATH=$PATH:/path/to/chromedriver
   ```

3. **Force driver update**:
   ```python
   from webdriver_manager.chrome import ChromeDriverManager
   ChromeDriverManager().install()
   ```

### Browser Permission Issues

**Problem**: Browser automation blocked by system security (macOS)

**Solutions**:
1. **Grant accessibility permissions**:
   - System Preferences → Security & Privacy → Privacy
   - Select "Accessibility" from the left panel
   - Add Terminal or your IDE to the list
   - Check the checkbox to enable

2. **Grant automation permissions**:
   - System Preferences → Security & Privacy → Privacy
   - Select "Automation" from the left panel
   - Allow Terminal to control System Events

3. **Disable System Integrity Protection** (last resort):
   ```bash
   # Boot into Recovery Mode and run:
   csrutil disable
   # Then reboot normally
   ```

### Browser Launch Failures

**Problem**: Chrome fails to start or crashes immediately

**Diagnostic**:
```bash
# Test Chrome manually
google-chrome --headless --disable-gpu --no-sandbox

# Check Chrome installation
which google-chrome
google-chrome --version
```

**Solutions**:
1. **Update Chrome**:
   ```bash
   # macOS
   brew upgrade --cask google-chrome
   
   # Ubuntu
   sudo apt update && sudo apt upgrade google-chrome-stable
   ```

2. **Fix Chrome user data directory**:
   ```bash
   # Remove corrupted user data
   rm -rf ./chrome_data
   # Agent will create new directory
   ```

3. **Use alternative Chrome flags**:
   ```env
   # In .env file, add custom flags via code modification
   # or use headless mode
   HEADLESS_MODE=true
   ```

## AI Integration Problems

### OpenAI API Rate Limiting

**Problem**: Rate limit exceeded errors
```
openai.RateLimitError: Rate limit reached for requests
```

**Solutions**:
1. **Check usage limits**:
   - Visit OpenAI platform dashboard
   - Review current usage and limits
   - Upgrade plan if necessary

2. **Add retry delays**:
   ```python
   # Increase retry wait time in settings
   MAX_RETRIES=5
   TIMEOUT_SECONDS=60
   ```

3. **Implement exponential backoff** (already built-in):
   ```python
   # The agent already uses tenacity for retries
   # Adjust settings if needed
   ```

### AI Response Parsing Errors

**Problem**: Invalid JSON from AI responses

**Diagnostic**:
```bash
# Check recent AI responses in logs
grep "AI suggested action" logs/agent.log | tail -5
```

**Solutions**:
1. **Check API model**:
   ```python
   # Ensure using a supported model
   # Currently optimized for GPT-4
   ```

2. **Validate response format**:
   ```python
   # The agent has fallback for invalid responses
   # Check logs for fallback action usage
   ```

3. **Update system prompt**:
   - AI prompt might need adjustment for newer models
   - Check `_generate_action_plan` method

### Context Analysis Failures

**Problem**: Agent cannot analyze page context

**Solutions**:
1. **Check JavaScript execution**:
   ```bash
   # Test if browser can execute JavaScript
   python -c "
   from src.browser.chrome_driver import ChromeDriver
   with ChromeDriver() as driver:
       driver.navigate_to('https://google.com')
       title = driver.execute_script('return document.title;')
       print(f'Title: {title}')
   "
   ```

2. **Verify page loading**:
   ```python
   # Add explicit waits for page loading
   TIMEOUT_SECONDS=60
   ```

## Performance Issues

### Slow Task Execution

**Problem**: Tasks take too long to complete

**Diagnostic**:
```bash
# Enable debug logging to see timing
LOG_LEVEL=DEBUG
python -m src.main execute --task "your task"
```

**Solutions**:
1. **Use headless mode**:
   ```bash
   python -m src.main execute --task "task" --headless
   ```

2. **Optimize browser settings**:
   ```env
   HEADLESS_MODE=true
   WINDOW_WIDTH=1280
   WINDOW_HEIGHT=720
   ```

3. **Reduce AI context size**:
   - Large pages may slow AI analysis
   - Consider page-specific optimizations

### High Memory Usage

**Problem**: Browser or agent consumes too much memory

**Solutions**:
1. **Monitor resource usage**:
   ```bash
   # On macOS/Linux
   top -p $(pgrep -f "chrome|python")
   
   # Or use htop for better visualization
   htop
   ```

2. **Limit browser resources**:
   ```python
   # Modify chrome options in chrome_driver.py
   chrome_options.add_argument('--memory-pressure-off')
   chrome_options.add_argument('--max_old_space_size=4096')
   ```

3. **Clean up resources**:
   ```bash
   # Clean Chrome user data periodically
   rm -rf chrome_data/
   
   # Clear logs
   rm -f logs/agent.log
   ```

## Error Messages

### Common Error Patterns

#### "ModuleNotFoundError"
```python
ModuleNotFoundError: No module named 'src'
```

**Solution**:
```bash
# Ensure you're in the project root directory
pwd  # Should show .../ai-browser-agent

# Install in development mode
pip install -e .

# Or use Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### "Permission denied" (Linux/macOS)
```bash
PermissionError: [Errno 13] Permission denied: 'logs/agent.log'
```

**Solution**:
```bash
# Fix directory permissions
sudo chown -R $USER:$USER .
chmod -R 755 .

# Create logs directory if needed
mkdir -p logs
```

#### "WebDriverException: unknown error"
```
selenium.common.exceptions.WebDriverException: Message: unknown error: Chrome failed to start
```

**Solution**:
```bash
# Try different Chrome flags
# Modify chrome_driver.py to add:
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-extensions')
```

#### "ValidationError" (Pydantic)
```
pydantic.error_wrappers.ValidationError: 1 validation error for AgentSettings
```

**Solution**:
```bash
# Check .env file format
cat .env

# Validate each setting
python -c "
from src.config.settings import AgentSettings
try:
    settings = AgentSettings()
    print('Configuration valid')
except Exception as e:
    print(f'Configuration error: {e}')
"
```

### Network-Related Errors

#### "Connection timeout"
```
requests.exceptions.ConnectTimeout: HTTPSConnectionPool
```

**Solutions**:
1. **Check internet connection**:
   ```bash
   ping google.com
   curl -I https://api.openai.com
   ```

2. **Configure proxy settings**:
   ```env
   # If behind corporate firewall
   HTTP_PROXY=http://proxy.company.com:8080
   HTTPS_PROXY=https://proxy.company.com:8080
   ```

3. **Increase timeout**:
   ```env
   TIMEOUT_SECONDS=120
   ```

## Platform-Specific Issues

### Windows Issues

#### PowerShell Execution Policy
```
execution of scripts is disabled on this system
```

**Solution**:
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Long Path Issues
```
FileNotFoundError: [Errno 2] No such file or directory
```

**Solution**:
1. Enable long paths in Windows 10/11
2. Use shorter directory names
3. Move project closer to root drive

#### Chrome User Data Directory Issues
```
OSError: [WinError 32] The process cannot access the file
```

**Solution**:
```cmd
# Kill all Chrome processes
taskkill /f /im chrome.exe
taskkill /f /im chromedriver.exe

# Clear user data
rmdir /s chrome_data
```

### macOS Issues

#### Quarantine Issues
```
"chromedriver" cannot be opened because the developer cannot be verified
```

**Solution**:
```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine /path/to/chromedriver

# Or allow in System Preferences
# Security & Privacy → General → Allow anyway
```

#### Rosetta 2 Issues (M1/M2 Macs)
```
Bad CPU type in executable
```

**Solution**:
```bash
# Install Rosetta 2
softwareupdate --install-rosetta

# Use Intel Python if needed
arch -x86_64 python3 -m venv venv
```

### Linux Issues

#### Missing System Dependencies
```
ImportError: libgobject-2.0.so.0: cannot open shared object file
```

**Solution**:
```bash
# Ubuntu/Debian
sudo apt install -y \
    libglib2.0-0 \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libasound2

# CentOS/RHEL
sudo yum install -y \
    atk \
    cups-libs \
    gtk3 \
    libXcomposite \
    libXcursor \
    libXdamage \
    libXext \
    libXi \
    libXrandr \
    libXScrnSaver \
    libXtst \
    pango \
    xorg-x11-fonts-100dpi \
    xorg-x11-fonts-75dpi \
    xorg-x11-fonts-cyrillic \
    xorg-x11-fonts-misc \
    xorg-x11-fonts-Type1 \
    xorg-x11-utils
```

#### Display Server Issues (Headless Systems)
```
selenium.common.exceptions.WebDriverException: Message: unknown error: cannot find Chrome binary
```

**Solution**:
```bash
# Install virtual display
sudo apt install xvfb

# Run with virtual display
xvfb-run -a python -m src.main execute --task "your task"

# Or force headless mode
HEADLESS_MODE=true python -m src.main execute --task "your task"
```

## Debugging Techniques

### Enable Verbose Logging

```env
# In .env file
LOG_LEVEL=DEBUG
LOG_FORMAT=text
DEBUG=true
```

### Capture Debug Information

```bash
# Run with full debugging
python -m src.main execute --task "test task" --screenshot 2>&1 | tee debug.log

# Check browser console
# Modify chrome_driver.py to add:
# logs = driver.get_log('browser')
# print(logs)
```

### Interactive Debugging

```python
# Add to code for breakpoint debugging
import pdb; pdb.set_trace()

# Or use rich for better debugging
from rich.console import Console
console = Console()
console.print_exception()
```

### Test Minimal Examples

```python
# Test browser only
from src.browser.chrome_driver import ChromeDriver
with ChromeDriver() as driver:
    driver.navigate_to("https://google.com")
    print("Browser test successful")

# Test AI only
import openai
client = openai.OpenAI(api_key="your-key")
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=10
)
print("AI test successful")
```

## Getting Help

### Before Asking for Help

1. **Check the logs**:
   ```bash
   tail -50 logs/agent.log
   ```

2. **Run with debug mode**:
   ```bash
   LOG_LEVEL=DEBUG python -m src.main execute --task "your task"
   ```

3. **Test with minimal example**:
   ```bash
   python -m src.main execute --task "take a screenshot" --headless
   ```

4. **Check system resources**:
   ```bash
   # Memory and CPU usage
   top
   
   # Disk space
   df -h
   ```

### Creating a Bug Report

Include the following information:

1. **System Information**:
   ```bash
   python --version
   google-chrome --version
   cat /etc/os-release  # Linux
   sw_vers              # macOS
   systeminfo           # Windows
   ```

2. **Environment Details**:
   ```bash
   pip list | grep -E "(selenium|openai|pydantic|click)"
   echo $SHELL
   env | grep -E "(PATH|PYTHON|OPENAI)"
   ```

3. **Error Information**:
   - Complete error message and stack trace
   - Log file contents around the error time
   - Steps to reproduce the issue
   - Expected vs actual behavior

4. **Configuration**:
   ```bash
   # Sanitized version (remove sensitive data)
   python -m src.main config
   ```

### Community Resources

- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share usage patterns
- **Documentation**: Check all documentation files in `/docs`

### Professional Support

For enterprise users or complex integration scenarios:
- Custom development and integration services
- Priority support and consulting
- Training and best practices guidance

Remember: Most issues have been encountered before. Check existing GitHub issues and documentation before creating new support requests.