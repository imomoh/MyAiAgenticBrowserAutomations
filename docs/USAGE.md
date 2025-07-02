# Usage Tutorial

This comprehensive guide shows you how to use the AI Browser Agent effectively for various automation tasks.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Command Line Interface](#command-line-interface)
- [Interactive Mode](#interactive-mode)
- [Task Examples](#task-examples)
- [Advanced Features](#advanced-features)
- [Best Practices](#best-practices)
- [Common Patterns](#common-patterns)

## Basic Usage

The AI Browser Agent can be used in three main ways:

1. **Single Task Execution**: Execute one-off automation tasks
2. **Interactive Mode**: Conversational browser automation
3. **Programmatic API**: Import and use in your Python scripts

## Command Line Interface

### Available Commands

```bash
# View all available commands
python -m src.main --help

# Show current configuration
python -m src.main config

# Execute a single task
python -m src.main execute --task "description"

# Start interactive mode
python -m src.main interactive

# Generate setup guide
python -m src.main setup-guide
```

### Execute Command Options

```bash
python -m src.main execute [OPTIONS]

Options:
  --task TEXT       Task description (required)
  --headless        Run browser in headless mode
  --screenshot      Take screenshot after task completion
  --help            Show help message
```

## Interactive Mode

Interactive mode provides a conversational interface for browser automation:

```bash
python -m src.main interactive
```

### Interactive Session Example

```
╭─ Starting Interactive Mode ──╮
│ Interactive AI Browser Agent │
╰──────────────────────────────╯

Agent started successfully!
Type 'quit' or 'exit' to stop

Enter task: navigate to github.com
✓ Success
Result: {'url': 'https://github.com'}

Enter task: take a screenshot
✓ Success  
Result: {'filename': 'screenshot.png'}

Enter task: get the page title
✓ Success
Result: {'text': 'GitHub: Let's build from here · GitHub'}

Enter task: quit
Goodbye!
```

### Interactive Mode Features

- **Persistent Session**: Browser stays open between tasks
- **Context Awareness**: Each task builds on the previous state
- **Real-time Feedback**: Immediate success/failure indication
- **Action History**: All actions are tracked and logged

## Task Examples

### Navigation Tasks

```bash
# Basic navigation
python -m src.main execute --task "go to google.com"
python -m src.main execute --task "navigate to https://github.com"
python -m src.main execute --task "visit wikipedia.org"

# Navigation with context
python -m src.main execute --task "go to the Python official website"
python -m src.main execute --task "navigate to GitHub and go to trending repositories"
```

### Screenshot Tasks

```bash
# Basic screenshot
python -m src.main execute --task "take a screenshot"

# Screenshot with navigation
python -m src.main execute --task "go to google.com and take a screenshot"

# Screenshot in headless mode
python -m src.main execute --task "capture a screenshot" --headless
```

### Information Extraction

```bash
# Get page information
python -m src.main execute --task "get the page title"
python -m src.main execute --task "find the main heading on the page"
python -m src.main execute --task "get the text from the first paragraph"

# Extract specific data
python -m src.main execute --task "find all links on the page"
python -m src.main execute --task "get the meta description"
```

### Form Interaction

```bash
# Search operations
python -m src.main execute --task "search for 'python selenium' on Google"
python -m src.main execute --task "type 'hello world' in the search box"

# Form filling (be careful with real forms)
python -m src.main execute --task "fill the contact form with test data"
python -m src.main execute --task "enter 'test@example.com' in the email field"
```

### Page Interaction

```bash
# Clicking elements
python -m src.main execute --task "click the login button"
python -m src.main execute --task "click on the first search result"

# Scrolling
python -m src.main execute --task "scroll down the page"
python -m src.main execute --task "scroll to the bottom of the page"

# Waiting
python -m src.main execute --task "wait for 3 seconds"
python -m src.main execute --task "wait for the page to load completely"
```

## Advanced Features

### Complex Multi-Step Tasks

The AI can handle complex tasks that require multiple steps:

```bash
# Multi-step workflow
python -m src.main execute --task "go to github.com, search for selenium, and click on the first repository"

# Data collection workflow
python -m src.main execute --task "visit news website, find today's top headline, and save a screenshot"

# Testing workflow
python -m src.main execute --task "navigate to login page, attempt login with invalid credentials, and capture the error message"
```

### Conditional Logic

The AI can make decisions based on page content:

```bash
# Conditional actions
python -m src.main execute --task "if there's a cookie banner, accept it, then navigate to the about page"

# Error handling
python -m src.main execute --task "try to click the submit button, if it fails, take a screenshot for debugging"
```

### Context-Aware Operations

```bash
# Using page context
python -m src.main execute --task "find the search box and enter the site's main topic"

# Adaptive behavior
python -m src.main execute --task "locate the navigation menu and click on the contact link"
```

## Best Practices

### Task Description Guidelines

1. **Be Specific**: Provide clear, detailed descriptions
   ```bash
   # Good
   python -m src.main execute --task "navigate to amazon.com and search for wireless headphones"
   
   # Less optimal
   python -m src.main execute --task "go shopping"
   ```

2. **Use Natural Language**: Write as you would speak
   ```bash
   # Natural and clear
   python -m src.main execute --task "go to the GitHub homepage and take a screenshot"
   
   # Too technical
   python -m src.main execute --task "GET https://github.com then execute screenshot action"
   ```

3. **Break Down Complex Tasks**: For very complex operations, use interactive mode
   ```bash
   # Interactive approach for complex workflows
   python -m src.main interactive
   # Then: "navigate to site"
   # Then: "login with credentials" 
   # Then: "navigate to dashboard"
   # Then: "extract data table"
   ```

### Performance Optimization

1. **Use Headless Mode**: For scripts and automation
   ```bash
   python -m src.main execute --task "task description" --headless
   ```

2. **Batch Similar Tasks**: Use interactive mode for multiple related tasks

3. **Configure Timeouts**: Adjust timeout settings for slow sites
   ```env
   TIMEOUT_SECONDS=60  # In .env file
   ```

### Error Prevention

1. **Start Simple**: Test with basic navigation before complex tasks

2. **Use Screenshots**: Visual verification of automation state
   ```bash
   python -m src.main execute --task "navigate to site and take screenshot" --screenshot
   ```

3. **Check Logs**: Monitor the logs for detailed execution information

## Common Patterns

### Web Scraping Pattern

```bash
# 1. Navigate to target site
python -m src.main execute --task "navigate to target-website.com"

# 2. Extract specific information
python -m src.main execute --task "get all product names from the page"

# 3. Capture evidence
python -m src.main execute --task "take a screenshot of the results"
```

### Testing Pattern

```bash
# Interactive testing session
python -m src.main interactive

# Then execute test steps:
# "navigate to application login page"
# "enter test credentials"
# "click login button"
# "verify dashboard is displayed"
# "take screenshot for test evidence"
# "logout"
```

### Monitoring Pattern

```bash
# Site health check
python -m src.main execute --task "navigate to production site and verify it loads correctly" --headless

# Capture current state
python -m src.main execute --task "take screenshot of homepage" --headless
```

### Data Collection Pattern

```bash
# Sequential data collection
python -m src.main interactive

# Interactive commands:
# "navigate to data source website"
# "search for today's data"
# "extract the main table data"
# "navigate to export options"
# "download the data file"
```

## Programmatic Usage

You can also use the agent programmatically in your Python scripts:

```python
from src.agent.browser_agent import BrowserAgent

# Basic usage
with BrowserAgent() as agent:
    result = agent.execute_task("navigate to google.com")
    if result.success:
        print("Navigation successful!")
    
    # Take screenshot
    screenshot_result = agent.execute_task("take a screenshot")
    print(f"Screenshot saved: {screenshot_result.screenshot_path}")
    
    # Get action history
    history = agent.get_action_history()
    print(f"Executed {len(history)} actions")
```

### Advanced Programmatic Usage

```python
from src.agent.browser_agent import BrowserAgent, ActionType, BrowserAction

with BrowserAgent() as agent:
    # Execute multiple tasks
    tasks = [
        "navigate to github.com",
        "search for selenium",
        "click on first result",
        "take a screenshot"
    ]
    
    results = []
    for task in tasks:
        result = agent.execute_task(task)
        results.append(result)
        if not result.success:
            print(f"Task failed: {task}")
            break
    
    # Check final state
    if all(r.success for r in results):
        print("All tasks completed successfully!")
        
        # Get comprehensive history
        history = agent.get_action_history()
        for i, action in enumerate(history):
            print(f"Action {i+1}: {action['task']}")
            print(f"  Result: {action['result']['success']}")
```

## Example Use Cases

### 1. Website Monitoring

Monitor website availability and performance:

```bash
# Daily health check
python -m src.main execute --task "navigate to company website and verify homepage loads correctly" --headless

# Performance check
python -m src.main execute --task "navigate to site, wait for full page load, then take performance screenshot" --headless
```

### 2. Automated Testing

Automate web application testing:

```bash
# User registration flow test
python -m src.main interactive

# Test steps:
# "navigate to signup page"
# "fill registration form with test data"
# "submit form"
# "verify success message appears"
# "take screenshot of confirmation"
```

### 3. Content Management

Automate content publishing workflows:

```bash
# Content verification
python -m src.main execute --task "navigate to blog, find today's post, and verify it displays correctly"

# Social media posting
python -m src.main execute --task "navigate to social platform, create new post with predefined content"
```

### 4. Data Collection

Automate data gathering from websites:

```bash
# Market research
python -m src.main execute --task "navigate to competitor website, capture pricing information, take screenshot"

# News aggregation  
python -m src.main execute --task "visit news site, find top 3 headlines, extract text content"
```

### 5. E-commerce Automation

Automate online shopping tasks:

```bash
# Price monitoring
python -m src.main execute --task "navigate to product page, check current price, compare with target price"

# Inventory checking
python -m src.main execute --task "visit store website, search for specific product, check availability status"
```

## Tips and Tricks

### 1. Debugging Failed Tasks

```bash
# Add screenshot for debugging
python -m src.main execute --task "your failing task" --screenshot

# Check logs for detailed error information
tail -f logs/agent.log

# Use interactive mode to step through manually
python -m src.main interactive
```

### 2. Handling Dynamic Content

```bash
# Wait for content to load
python -m src.main execute --task "navigate to site, wait 5 seconds for content to load, then extract data"

# Handle loading states
python -m src.main execute --task "wait for loading spinner to disappear, then interact with page"
```

### 3. Working with Different Page Types

```bash
# Single Page Applications (SPAs)
python -m src.main execute --task "navigate to app, wait for React app to initialize, then interact with components"

# Pop-ups and modals
python -m src.main execute --task "if popup appears, close it, then continue with main task"
```

### 4. Error Recovery

```bash
# Graceful error handling
python -m src.main execute --task "try to complete task, if error occurs, take screenshot and report issue"

# Retry mechanisms
# The agent automatically retries failed actions up to MAX_RETRIES times
```

## Next Steps

- Explore [API Reference](API.md) for detailed technical documentation
- Read [Architecture](ARCHITECTURE.md) to understand how the system works
- Check [Development Guide](DEVELOPMENT.md) to contribute or customize
- Review [Troubleshooting](TROUBLESHOOTING.md) for common issues and solutions