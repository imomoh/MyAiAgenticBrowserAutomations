# Development Guide

This guide provides everything you need to know to contribute to, modify, or extend the AI Browser Agent project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Contributing](#contributing)
- [Project Structure](#project-structure)
- [Adding Features](#adding-features)
- [Debugging](#debugging)

## Getting Started

### Prerequisites for Development

- Python 3.9 or higher
- Git
- Chrome browser
- OpenAI API key (for testing AI features)
- IDE/Editor with Python support (VS Code, PyCharm, etc.)

### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-username/ai-browser-agent.git
cd ai-browser-agent

# Set up development environment
make dev
# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
pre-commit install
```

### Verify Setup

```bash
# Run tests to ensure everything works
make test

# Check code quality
make quality

# Try the CLI
python -m src.main --help
```

## Development Environment

### Recommended IDE Setup

#### VS Code
1. Install Python extension
2. Configure Python interpreter:
   - Command Palette → Python: Select Interpreter
   - Choose the virtual environment Python
3. Install recommended extensions:
   - Python
   - Pylance
   - Black Formatter
   - GitLens

#### PyCharm
1. Open project folder
2. Configure Python interpreter (Settings → Project → Python Interpreter)
3. Enable:
   - Black for code formatting
   - Pylint for linting
   - Type checking

### Environment Variables

Create a `.env` file for development:

```env
# Required for AI functionality
OPENAI_API_KEY=your_development_api_key

# Development settings
DEBUG=true
DEVELOPMENT_MODE=true
LOG_LEVEL=DEBUG
LOG_FORMAT=text
HEADLESS_MODE=true

# Test settings
TIMEOUT_SECONDS=10
MAX_RETRIES=1
```

### Make Commands

The project includes a comprehensive Makefile:

```bash
# View all available commands
make help

# Development workflow
make dev              # Set up development environment
make test             # Run all tests
make test-unit        # Run unit tests only
make test-integration # Run integration tests only
make coverage         # Run tests with coverage report

# Code quality
make format           # Format code with Black
make format-check     # Check code formatting
make lint             # Run linting with Flake8
make type-check       # Run type checking with MyPy
make quality          # Run all quality checks

# Maintenance
make clean            # Clean generated files
make pre-commit       # Run pre-commit hooks
```

## Code Standards

### Code Style

The project follows strict code quality standards:

#### Black Formatting
- Line length: 88 characters
- Automatic formatting on save (recommended)
- Pre-commit hook enforces formatting

```bash
# Format all code
make format

# Check formatting without changes
make format-check
```

#### Linting with Flake8
- Max line length: 88
- Extended ignore: E203 (conflicts with Black)
- Custom configuration in `pyproject.toml`

```bash
# Run linting
make lint
```

#### Type Checking with MyPy
- Strict mode enabled
- No untyped function definitions allowed
- All public APIs must have type hints

```bash
# Check types
make type-check
```

### Code Organization

#### File Naming
- Use snake_case for Python files
- Use descriptive names: `browser_agent.py`, not `agent.py`
- Test files: `test_module_name.py`

#### Import Organization
```python
# Standard library imports
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Third-party imports
import click
from loguru import logger
from pydantic import BaseModel

# Local imports
from ..config.settings import settings
from ..utils.exceptions import AgentError
```

#### Docstrings
Use Google-style docstrings:

```python
def execute_task(self, task_description: str) -> ActionResult:
    """Execute a natural language task description.
    
    Args:
        task_description: Natural language description of the task to perform
        
    Returns:
        ActionResult containing success status and execution data
        
    Raises:
        AgentError: If the task cannot be executed
        BrowserError: If browser automation fails
        
    Example:
        >>> agent = BrowserAgent()
        >>> result = agent.execute_task("navigate to google.com")
        >>> print(result.success)
        True
    """
```

#### Error Handling
```python
# Use specific exception types
try:
    result = self.driver.navigate_to(url)
except BrowserError as e:
    logger.error(f"Navigation failed: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise AgentError(f"Navigation failed: {e}")
```

## Testing

### Test Structure

```
tests/
├── unit/                 # Unit tests for individual components
│   ├── test_browser_agent.py
│   ├── test_chrome_driver.py
│   └── test_config.py
├── integration/          # Integration tests for complete workflows
│   ├── test_full_workflow.py
│   └── test_ai_integration.py
└── fixtures/             # Test data and fixtures
    ├── mock_responses.json
    └── test_pages.html
```

### Writing Tests

#### Unit Tests
```python
import pytest
from unittest.mock import Mock, patch
from src.agent.browser_agent import BrowserAgent

class TestBrowserAgent:
    @pytest.fixture
    def mock_driver(self):
        with patch('src.agent.browser_agent.ChromeDriver') as mock:
            yield mock.return_value
    
    def test_execute_task_success(self, mock_driver):
        """Test successful task execution."""
        # Arrange
        mock_driver.get_current_url.return_value = "https://example.com"
        agent = BrowserAgent()
        
        # Act
        result = agent.execute_task("take a screenshot")
        
        # Assert
        assert result.success is True
        mock_driver.take_screenshot.assert_called_once()
```

#### Integration Tests
```python
@pytest.mark.integration
class TestFullWorkflow:
    def test_complete_automation_workflow(self):
        """Test complete automation workflow with mocked dependencies."""
        with patch('src.agent.browser_agent.openai.OpenAI') as mock_openai:
            # Setup mocks for complete workflow test
            pass
```

### Running Tests

```bash
# Run all tests
make test

# Run specific test types
make test-unit
make test-integration

# Run specific test file
pytest tests/unit/test_browser_agent.py -v

# Run specific test method
pytest tests/unit/test_browser_agent.py::TestBrowserAgent::test_execute_task_success -v

# Run with coverage
make coverage

# Generate HTML coverage report
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

### Test Utilities

#### Mock Helpers
```python
# tests/conftest.py
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": '{"action": "screenshot", "parameters": {"filename": "test.png"}}'
                }
            }
        ]
    }

@pytest.fixture
def sample_browser_action():
    """Sample browser action for testing."""
    from src.agent.browser_agent import BrowserAction, ActionType
    return BrowserAction(
        action=ActionType.SCREENSHOT,
        parameters={"filename": "test.png"},
        description="Take a test screenshot"
    )
```

## Contributing

### Workflow

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/your-username/ai-browser-agent.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/new-feature-name
   ```

3. **Make your changes**
   - Follow code standards
   - Add tests for new functionality
   - Update documentation as needed

4. **Test your changes**
   ```bash
   make test
   make quality
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add new feature: description"
   # Pre-commit hooks will run automatically
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/new-feature-name
   # Create PR on GitHub
   ```

### Commit Message Guidelines

Use conventional commit format:

```
type(scope): description

Examples:
feat(agent): add support for Firefox browser
fix(browser): handle timeout errors gracefully
docs(api): update action type documentation
test(unit): add tests for configuration loading
refactor(cli): simplify command structure
```

### Code Review Process

1. **Automated Checks**: CI must pass
2. **Code Review**: At least one maintainer review
3. **Testing**: New features must include tests
4. **Documentation**: Public APIs must be documented

## Project Structure

### Source Code Organization

```
src/
├── agent/                # Core agent logic
│   ├── __init__.py
│   └── browser_agent.py  # Main agent implementation
├── browser/              # Browser automation
│   ├── __init__.py
│   └── chrome_driver.py  # Chrome WebDriver wrapper
├── config/               # Configuration management
│   ├── __init__.py
│   └── settings.py       # Pydantic settings
├── utils/                # Utility modules
│   ├── __init__.py
│   ├── exceptions.py     # Custom exceptions
│   └── logger.py         # Logging configuration
└── main.py              # CLI entry point
```

### Key Design Patterns

#### Dependency Injection
```python
class BrowserAgent:
    def __init__(self, driver: Optional[ChromeDriver] = None):
        self.driver = driver or ChromeDriver()
        # Allows for easy testing and extension
```

#### Configuration Management
```python
# Centralized configuration
from src.config.settings import settings

# Type-safe access
timeout = settings.agent.timeout_seconds
headless = settings.browser.headless_mode
```

#### Error Handling Strategy
```python
# Specific exceptions for different failure modes
class AgentError(Exception):
    """Base exception for agent errors"""
    pass

class BrowserError(AgentError):
    """Browser-specific errors"""
    pass
```

## Adding Features

### Adding New Action Types

1. **Define the action type**
   ```python
   # In src/agent/browser_agent.py
   class ActionType(str, Enum):
       # Existing actions...
       NEW_ACTION = "new_action"
   ```

2. **Implement execution logic**
   ```python
   def _execute_new_action(self, action: BrowserAction) -> ActionResult:
       """Execute new action type."""
       try:
           # Implementation
           return ActionResult(success=True, data={"result": "success"})
       except Exception as e:
           return ActionResult(success=False, error=str(e))
   ```

3. **Update the execution dispatcher**
   ```python
   def _execute_action(self, action: BrowserAction) -> ActionResult:
       if action.action == ActionType.NEW_ACTION:
           return self._execute_new_action(action)
       # ... existing actions
   ```

4. **Update AI prompt**
   ```python
   system_prompt = """
   Available actions:
   - new_action: {"action": "new_action", "parameters": {...}}
   """
   ```

5. **Add tests**
   ```python
   def test_execute_new_action(self, browser_agent):
       action = BrowserAction(
           action=ActionType.NEW_ACTION,
           parameters={},
           description="Test new action"
       )
       result = browser_agent._execute_action(action)
       assert result.success is True
   ```

### Adding New Browser Support

1. **Create browser driver**
   ```python
   # src/browser/firefox_driver.py
   class FirefoxDriver:
       def start(self) -> None:
           # Firefox-specific implementation
           pass
   ```

2. **Update configuration**
   ```python
   # In src/config/settings.py
   browser_type: str = Field("chrome", env="BROWSER_TYPE")
   # Validate against: ["chrome", "firefox"]
   ```

3. **Add factory method**
   ```python
   def create_driver(browser_type: str):
       if browser_type == "firefox":
           return FirefoxDriver()
       return ChromeDriver()
   ```

### Adding New CLI Commands

1. **Define command**
   ```python
   # In src/main.py
   @cli.command()
   @click.option("--option", help="Command option")
   def new_command(option: str):
       """New command description."""
       # Implementation
   ```

2. **Add tests**
   ```python
   def test_new_command():
       from click.testing import CliRunner
       runner = CliRunner()
       result = runner.invoke(cli, ['new-command', '--option', 'value'])
       assert result.exit_code == 0
   ```

## Debugging

### Development Debugging

#### Enable Debug Mode
```env
# In .env
DEBUG=true
LOG_LEVEL=DEBUG
LOG_FORMAT=text
```

#### Interactive Debugging
```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use rich debugger
from rich.console import Console
console = Console()
console.print_exception()
```

#### Browser Debugging
```python
# Disable headless mode for visual debugging
HEADLESS_MODE=false

# Take screenshots for debugging
python -m src.main execute --task "your task" --screenshot
```

### Common Issues

#### OpenAI API Issues
```bash
# Test API connection
python -c "
import openai
client = openai.OpenAI(api_key='your-key')
response = client.models.list()
print('API connection successful')
"
```

#### Browser Issues
```bash
# Check Chrome installation
google-chrome --version

# Manually test WebDriver
python -c "
from selenium import webdriver
driver = webdriver.Chrome()
driver.get('https://google.com')
print('Browser test successful')
driver.quit()
"
```

#### Import Issues
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Test package imports
python -c "from src.agent.browser_agent import BrowserAgent; print('Import successful')"
```

### Performance Profiling

#### Execution Time Profiling
```python
import time
from functools import wraps

def profile_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper

# Use on methods for profiling
```

#### Memory Profiling
```bash
# Install memory profiler
pip install memory-profiler

# Profile script
python -m memory_profiler your_script.py
```

### Logging and Monitoring

#### Custom Log Analysis
```bash
# Filter error logs
grep "ERROR" logs/agent.log

# Monitor real-time logs
tail -f logs/agent.log | grep "execute_task"

# Analyze action patterns
jq '.action' logs/agent.log | sort | uniq -c
```

#### Performance Monitoring
```python
# Add timing to critical paths
import time
from loguru import logger

start_time = time.time()
# ... operation
execution_time = time.time() - start_time
logger.info(f"Operation completed in {execution_time:.2f}s")
```

## Release Process

### Version Management

1. **Update version in pyproject.toml**
2. **Update CHANGELOG.md**
3. **Create release tag**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

### Testing Before Release

```bash
# Full test suite
make test

# Code quality check
make quality

# Integration test with real browser
python -m src.main execute --task "navigate to google.com" --screenshot

# Documentation check
# Ensure all new features are documented
```

### Continuous Integration

The project uses GitHub Actions for CI/CD:

- **On Push/PR**: Run tests, linting, type checking
- **On Release**: Build and publish package
- **Security Scanning**: Bandit for security issues

This development guide provides the foundation for contributing to and extending the AI Browser Agent. For additional help, consult the other documentation files or reach out to the maintainers.