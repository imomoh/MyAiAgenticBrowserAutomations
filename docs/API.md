# API Reference

Complete reference documentation for the AI Browser Agent API, configuration options, and programmatic usage.

## Table of Contents

- [Core Classes](#core-classes)
- [Configuration](#configuration)
- [Action Types](#action-types)
- [Data Models](#data-models)
- [CLI Reference](#cli-reference)
- [Environment Variables](#environment-variables)
- [Error Handling](#error-handling)

## Core Classes

### BrowserAgent

The main agent class that orchestrates AI-powered browser automation.

```python
from src.agent.browser_agent import BrowserAgent

class BrowserAgent:
    def __init__(self) -> None
    def start(self) -> None
    def stop(self) -> None
    def execute_task(self, task_description: str) -> ActionResult
    def get_action_history(self) -> List[Dict[str, Any]]
```

#### Constructor

```python
agent = BrowserAgent()
```

Creates a new browser agent instance with default configuration from environment variables.

#### Methods

##### `start() -> None`

Initializes the browser driver and AI client.

```python
agent = BrowserAgent()
agent.start()
```

**Raises:**
- `AgentError`: If browser or AI initialization fails

##### `stop() -> None`

Closes the browser and cleans up resources.

```python
agent.stop()
```

##### `execute_task(task_description: str) -> ActionResult`

Executes a natural language task description.

```python
result = agent.execute_task("navigate to google.com")
print(result.success)  # True/False
print(result.data)     # Task-specific data
```

**Parameters:**
- `task_description` (str): Natural language description of the task

**Returns:**
- `ActionResult`: Result object containing success status and data

**Example:**
```python
with BrowserAgent() as agent:
    result = agent.execute_task("take a screenshot")
    if result.success:
        print(f"Screenshot saved: {result.screenshot_path}")
    else:
        print(f"Task failed: {result.error}")
```

##### `get_action_history() -> List[Dict[str, Any]]`

Returns the complete history of executed actions.

```python
history = agent.get_action_history()
for action in history:
    print(f"Task: {action['task']}")
    print(f"Success: {action['result']['success']}")
    print(f"Timestamp: {action['timestamp']}")
```

**Returns:**
- List of action history dictionaries

#### Context Manager Support

The BrowserAgent supports context manager protocol:

```python
with BrowserAgent() as agent:
    result = agent.execute_task("navigate to example.com")
    # Agent automatically started and will be stopped when exiting
```

### ChromeDriver

Low-level browser automation interface.

```python
from src.browser.chrome_driver import ChromeDriver

class ChromeDriver:
    def __init__(self) -> None
    def start(self) -> None
    def stop(self) -> None
    def navigate_to(self, url: str) -> None
    def find_element(self, by: By, value: str, timeout: Optional[int] = None) -> WebElement
    def click_element(self, by: By, value: str, timeout: Optional[int] = None) -> None
    def send_keys(self, by: By, value: str, text: str, timeout: Optional[int] = None) -> None
    def take_screenshot(self, filename: str) -> bool
    def execute_script(self, script: str) -> Any
```

#### Example Usage

```python
from selenium.webdriver.common.by import By
from src.browser.chrome_driver import ChromeDriver

with ChromeDriver() as driver:
    driver.navigate_to("https://example.com")
    driver.click_element(By.ID, "submit-button")
    success = driver.take_screenshot("example.png")
```

## Configuration

### Settings Classes

The configuration system uses Pydantic for type-safe settings management.

#### AgentSettings

```python
from src.config.settings import AgentSettings

class AgentSettings(BaseSettings):
    openai_api_key: str
    agent_name: str = "BrowserAgent"
    agent_description: str = "AI agent for browser automation"
    max_retries: int = 3
    timeout_seconds: int = 30
```

#### BrowserSettings

```python
class BrowserSettings(BaseSettings):
    browser_type: str = "chrome"
    headless_mode: bool = False
    window_width: int = 1920
    window_height: int = 1080
    user_data_dir: str = "./chrome_data"
    allowed_domains: str = "*"
    blocked_domains: str = ""
```

#### LoggingSettings

```python
class LoggingSettings(BaseSettings):
    log_level: str = "INFO"
    log_file: str = "logs/agent.log"
    log_format: str = "json"
```

#### Accessing Configuration

```python
from src.config.settings import settings

# Access agent settings
print(settings.agent.max_retries)
print(settings.agent.timeout_seconds)

# Access browser settings
print(settings.browser.headless_mode)
print(settings.browser.window_width)

# Access logging settings
print(settings.logging.log_level)
```

## Action Types

The agent supports various action types for browser automation.

### ActionType Enum

```python
from src.agent.browser_agent import ActionType

class ActionType(str, Enum):
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    GET_TEXT = "get_text"
    GET_ATTRIBUTE = "get_attribute"
    EXECUTE_SCRIPT = "execute_script"
```

### Action Descriptions

#### NAVIGATE
Navigate to a specific URL.

**Parameters:**
- `url` (str): Target URL

**Example AI Generation:**
```json
{
  "action": "navigate",
  "parameters": {"url": "https://example.com"},
  "description": "Navigate to example.com"
}
```

#### CLICK
Click on a page element.

**Parameters:**
- `selector` (str): Element selector
- `by` (str): Selector method (css, xpath, id, etc.)

**Example AI Generation:**
```json
{
  "action": "click",
  "parameters": {
    "selector": "button#submit",
    "by": "css"
  },
  "description": "Click the submit button"
}
```

#### TYPE
Type text into an input element.

**Parameters:**
- `selector` (str): Element selector
- `text` (str): Text to type
- `by` (str): Selector method

**Example AI Generation:**
```json
{
  "action": "type",
  "parameters": {
    "selector": "input[name='search']",
    "text": "python selenium",
    "by": "css"
  },
  "description": "Type search query"
}
```

#### SCREENSHOT
Capture a screenshot of the current page.

**Parameters:**
- `filename` (str): Output filename

**Example AI Generation:**
```json
{
  "action": "screenshot",
  "parameters": {"filename": "page_capture.png"},
  "description": "Take a screenshot"
}
```

#### GET_TEXT
Extract text content from an element.

**Parameters:**
- `selector` (str): Element selector
- `by` (str): Selector method

#### GET_ATTRIBUTE
Get an attribute value from an element.

**Parameters:**
- `selector` (str): Element selector
- `attribute` (str): Attribute name
- `by` (str): Selector method

#### SCROLL
Scroll the page.

**Parameters:**
- `direction` (str): "up" or "down"
- `amount` (int): Pixels to scroll

#### WAIT
Pause execution for a specified time.

**Parameters:**
- `seconds` (int): Time to wait

#### EXECUTE_SCRIPT
Execute JavaScript code in the browser.

**Parameters:**
- `script` (str): JavaScript code

## Data Models

### BrowserAction

Represents an action to be executed by the browser.

```python
from src.agent.browser_agent import BrowserAction

class BrowserAction(BaseModel):
    action: ActionType
    parameters: Dict[str, Any]
    description: str
```

**Example:**
```python
action = BrowserAction(
    action=ActionType.NAVIGATE,
    parameters={"url": "https://example.com"},
    description="Navigate to example website"
)
```

### ActionResult

Contains the result of an executed action.

```python
from src.agent.browser_agent import ActionResult

class ActionResult(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    screenshot_path: Optional[str] = None
```

**Example:**
```python
result = ActionResult(
    success=True,
    data={"url": "https://example.com"},
    error=None,
    screenshot_path=None
)
```

## CLI Reference

### Main Command

```bash
python -m src.main [OPTIONS] COMMAND [ARGS]...
```

**Global Options:**
- `--version`: Show version and exit
- `--help`: Show help message

### Commands

#### execute

Execute a single browser automation task.

```bash
python -m src.main execute [OPTIONS]
```

**Options:**
- `--task TEXT`: Task description (required)
- `--headless`: Run browser in headless mode
- `--screenshot`: Take screenshot after task
- `--help`: Show command help

**Examples:**
```bash
python -m src.main execute --task "navigate to google.com"
python -m src.main execute --task "take a screenshot" --headless
python -m src.main execute --task "search for python" --screenshot
```

#### interactive

Start interactive mode for continuous task execution.

```bash
python -m src.main interactive
```

**Example Session:**
```bash
python -m src.main interactive
# Interactive prompts follow
```

#### config

Show current configuration.

```bash
python -m src.main config
```

**Output Example:**
```
╭───────────────╮
│ Configuration │
╰───────────────╯
Agent Name: BrowserAgent
Max Retries: 3
Timeout: 30s
Browser: chrome
Headless: False
Window Size: 1920x1080
Log Level: INFO
Log File: logs/agent.log
```

#### setup-guide

Generate setup instructions.

```bash
python -m src.main setup-guide [OPTIONS]
```

**Options:**
- `--output TEXT`: Output file (default: setup_instructions.md)

## Environment Variables

### Required Variables

| Variable | Type | Description |
|----------|------|-------------|
| `OPENAI_API_KEY` | string | OpenAI API key for AI functionality |

### Agent Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `AGENT_NAME` | string | "BrowserAgent" | Agent identifier |
| `AGENT_DESCRIPTION` | string | "AI agent for browser automation" | Agent description |
| `MAX_RETRIES` | integer | 3 | Maximum retry attempts for failed actions |
| `TIMEOUT_SECONDS` | integer | 30 | Default timeout for browser operations |

### Browser Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `BROWSER_TYPE` | string | "chrome" | Browser type (currently only chrome) |
| `HEADLESS_MODE` | boolean | false | Run browser without GUI |
| `WINDOW_WIDTH` | integer | 1920 | Browser window width |
| `WINDOW_HEIGHT` | integer | 1080 | Browser window height |
| `USER_DATA_DIR` | string | "./chrome_data" | Chrome user data directory |

### Security Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ALLOWED_DOMAINS` | string | "*" | Comma-separated list of allowed domains |
| `BLOCKED_DOMAINS` | string | "" | Comma-separated list of blocked domains |

### Logging Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LOG_LEVEL` | string | "INFO" | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `LOG_FILE` | string | "logs/agent.log" | Log file path |
| `LOG_FORMAT` | string | "json" | Log format (json or text) |

### Development Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DEBUG` | boolean | false | Enable debug mode |
| `DEVELOPMENT_MODE` | boolean | false | Enable development features |

## Error Handling

### Exception Hierarchy

```python
# Base exception
class AgentError(Exception):
    """Base exception for agent-related errors"""
    pass

# Browser-specific errors
class BrowserError(AgentError):
    """Browser automation errors"""
    pass

# Configuration errors
class ConfigurationError(AgentError):
    """Configuration validation errors"""
    pass

# AI service errors
class AIServiceError(AgentError):
    """OpenAI API related errors"""
    pass
```

### Error Handling Examples

```python
from src.agent.browser_agent import BrowserAgent
from src.utils.exceptions import AgentError, BrowserError

try:
    with BrowserAgent() as agent:
        result = agent.execute_task("invalid task")
        if not result.success:
            print(f"Task failed: {result.error}")
            
except BrowserError as e:
    print(f"Browser error: {e}")
except AIServiceError as e:
    print(f"AI service error: {e}")
except AgentError as e:
    print(f"General agent error: {e}")
```

### Retry Mechanism

The agent automatically retries failed actions using the tenacity library:

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def execute_task(self, task_description: str) -> ActionResult:
    # Task execution with automatic retry
```

**Configuration:**
- Maximum attempts: Controlled by `MAX_RETRIES` environment variable
- Wait strategy: Exponential backoff (4-10 seconds)
- Retry conditions: Most exceptions except configuration errors

### Logging Integration

All errors are automatically logged with structured information:

```json
{
  "timestamp": "2025-07-01 19:50:27.486",
  "level": "ERROR",
  "module": "browser_agent",
  "function": "execute_task",
  "line": 196,
  "message": "Failed to execute task 'invalid task': Navigation failed"
}
```

## Advanced Usage

### Custom Action Execution

For advanced users who need direct control:

```python
from src.agent.browser_agent import BrowserAgent, BrowserAction, ActionType

with BrowserAgent() as agent:
    # Create custom action
    action = BrowserAction(
        action=ActionType.EXECUTE_SCRIPT,
        parameters={"script": "window.scrollTo(0, document.body.scrollHeight);"},
        description="Scroll to bottom of page"
    )
    
    # Execute directly
    result = agent._execute_action(action)
    print(result.success)
```

### Browser Context Access

Access browser context information:

```python
with BrowserAgent() as agent:
    # Get page context (internal method)
    context = agent._get_page_context()
    print(f"Current URL: {context['current_url']}")
    print(f"Page title: {context['page_title']}")
    print(f"Visible elements: {len(context['visible_elements'])}")
```

### Configuration Override

Override configuration programmatically:

```python
import os
from src.config.settings import Settings

# Override environment variables
os.environ['HEADLESS_MODE'] = 'true'
os.environ['LOG_LEVEL'] = 'DEBUG'

# Reload settings
settings = Settings.load()

# Use with agent
with BrowserAgent() as agent:
    # Agent will use updated settings
    pass
```

This completes the comprehensive API reference. For more examples and advanced usage patterns, see the [Usage Tutorial](USAGE.md) and [Architecture Documentation](ARCHITECTURE.md).