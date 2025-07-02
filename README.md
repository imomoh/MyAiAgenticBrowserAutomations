# AI Browser Agent

[![CI](https://github.com/your-username/ai-browser-agent/workflows/CI/badge.svg)](https://github.com/your-username/ai-browser-agent/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent AI-powered browser automation agent that understands natural language commands and performs web automation tasks using OpenAI's GPT models and Selenium WebDriver.

## 🌟 Features

- **Natural Language Control**: Describe what you want to do in plain English
- **Intelligent Action Planning**: AI analyzes the current page context and plans optimal actions
- **Multi-Step Task Execution**: Automatically breaks down complex tasks into step-by-step plans
- **Profile Mode**: Use your existing Chrome profile to access logged-in accounts (Gmail, Facebook, LinkedIn, etc.)
- **Browser Automation**: Full Chrome browser control with Selenium WebDriver
- **Screenshot Capture**: Automatic screenshot generation for visual verification
- **Action History**: Track all performed actions with detailed logging
- **CLI Interface**: Professional command-line interface with rich formatting
- **Error Recovery**: Robust error handling with step-level recovery mechanisms
- **Transparent Planning**: See exactly what the agent plans to do before execution
- **Headless Mode**: Run browser automation in the background
- **Build System**: Professional Make-based build and dependency management

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Chrome browser installed
- OpenAI API key
- Make (usually pre-installed on macOS/Linux)

### One-Command Setup

```bash
# Clone and setup everything
git clone https://github.com/your-username/ai-browser-agent.git
cd ai-browser-agent
./setup.sh
```

Or manually:

```bash
# Build project (creates venv, installs dependencies)
make build

# Add your OpenAI API key to .env file
# Edit .env and add: OPENAI_API_KEY=your_openai_api_key_here
```

### Usage Examples

#### Interactive Mode

```bash
make run
```

```
Enter task: navigate to google.com
✓ Success

Enter task: take a screenshot
✓ Success
Result: {'filename': 'screenshot.png'}

Enter task: quit
```

#### Single Task Execution

```bash
# Simple task
make run-execute TASK="go to github.com"

# Complex multi-step task (automatically planned)
make run-execute TASK="navigate to google.com and search for python selenium then take a screenshot"

# Find information
make run-execute TASK="find the best hot dogs in austin tx"

# Use your existing Chrome profile (access logged-in accounts)
make run-with-profile TASK="check my Gmail inbox"
make run-with-profile TASK="post on Facebook: Hello from my AI agent!"
```

#### Interactive Mode with Your Profile

```bash
# Use your existing Chrome profile in interactive mode
make run-interactive-profile
```

```
Using your existing Chrome profile - you'll have access to logged-in accounts

Enter task: check my notifications on LinkedIn
✓ Success

Enter task: like the latest post from my friend
✓ Success
```

#### Management Commands

```bash
# View current configuration
make config

# Show all available commands
make help

# Clean up everything (venv, logs, screenshots)
make clean

# Rebuild from scratch
make clean && make build
```

## 🔐 Profile Mode - Access Your Logged-in Accounts

The agent can use your existing Chrome profile to access websites where you're already logged in:

### When to Use Profile Mode

- ✅ **Social Media**: Post to Facebook, LinkedIn, Twitter
- ✅ **Email**: Check Gmail, send emails
- ✅ **Work Tools**: Access Slack, Notion, company dashboards
- ✅ **Shopping**: Use saved payment methods, check order history
- ✅ **Personal**: Access any site where you're logged in

### How It Works

Profile mode creates a temporary copy of your Chrome profile data (bookmarks, login cookies, preferences) without interfering with your regular Chrome usage. Your original profile remains untouched.

### Commands

```bash
# List available Chrome profiles
make list-profiles

# Single task with profile (will prompt for selection if multiple profiles)
make run-with-profile TASK="check my Gmail for urgent emails"

# Use a specific profile by name
make run-with-specific-profile TASK="check my Gmail" PROFILE="Work Account"

# Interactive mode with profile
make run-interactive-profile

# CLI with specific profile
python -m src.main execute --task "..." --use-profile --profile-name "Personal"

# Environment variable
USE_EXISTING_PROFILE=true make run

# Custom profile path
python -m src.main execute --task "..." --profile-path "/path/to/profile"
```

### Security Notes

- Profile data is copied to a temporary directory and cleaned up after use
- Only essential files are copied (bookmarks, preferences, login data)
- No permanent changes are made to your original Chrome profile
- Lock files that could cause conflicts are avoided

## 📖 Documentation

- [Setup Guide](docs/SETUP.md) - Detailed installation and configuration
- [Usage Tutorial](docs/USAGE.md) - Step-by-step usage examples
- [API Reference](docs/API.md) - Complete API documentation
- [Architecture](docs/ARCHITECTURE.md) - System design and components
- [Development](docs/DEVELOPMENT.md) - Contributing and development setup
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions

## 🏗️ Project Structure

```
ai-browser-agent/
├── src/                    # Core application code
│   ├── agent/             # AI agent implementation
│   │   └── browser_agent.py
│   ├── browser/           # Browser automation
│   │   └── chrome_driver.py
│   ├── config/            # Configuration management
│   │   └── settings.py
│   ├── utils/             # Utilities and helpers
│   └── main.py           # CLI entry point
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── docs/                 # Documentation
├── screenshots/          # Generated screenshots
├── logs/                 # Application logs
└── requirements.txt      # Python dependencies
```

## 🤖 How It Works

1. **Task Input**: You provide a natural language description of what you want to do
2. **Context Analysis**: The agent analyzes the current browser state and page content
3. **AI Planning**: OpenAI GPT-4 generates an optimal action plan based on the context
4. **Action Execution**: The agent executes browser actions using Selenium WebDriver
5. **Result Tracking**: Actions and results are logged with full history tracking

### Supported Actions

- **Navigation**: `navigate`, `go to`, `visit`
- **Interaction**: `click`, `type`, `send keys`
- **Information**: `get text`, `get attribute`, `screenshot`
- **Control**: `scroll`, `wait`, `execute script`

## ⚙️ Configuration

The agent is configured through environment variables in the `.env` file:

| Variable          | Description               | Default  |
| ----------------- | ------------------------- | -------- |
| `OPENAI_API_KEY`  | OpenAI API key (required) | -        |
| `BROWSER_TYPE`    | Browser to use            | `chrome` |
| `HEADLESS_MODE`   | Run browser headlessly    | `false`  |
| `LOG_LEVEL`       | Logging level             | `INFO`   |
| `MAX_RETRIES`     | Max retry attempts        | `3`      |
| `TIMEOUT_SECONDS` | Action timeout            | `30`     |

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test types
make test-unit
make test-integration

# Run with coverage
make coverage
```

## 🛠️ Development

```bash
# Set up development environment
make dev

# Code quality checks
make quality

# Format code
make format

# Run linting
make lint
```

## 📝 Example Use Cases

- **Web Scraping**: "Navigate to news website and capture article headlines"
- **Form Automation**: "Fill out contact form with my information"
- **Testing**: "Test login functionality and take screenshots"
- **Monitoring**: "Check if website is responding and capture status"
- **Data Collection**: "Visit multiple pages and extract product information"

## 🔒 Security Considerations

- Never commit real API keys to version control
- Use environment-specific configuration files
- Review generated actions before execution in production
- Consider rate limiting for API calls
- Grant minimal browser permissions required

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Ensure all tests pass: `make test`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- [Documentation](docs/)
- [Issues](https://github.com/your-username/ai-browser-agent/issues)
- [Discussions](https://github.com/your-username/ai-browser-agent/discussions)

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) for GPT models
- [Selenium](https://selenium.dev/) for browser automation
- [Pydantic](https://pydantic.dev/) for configuration management
- [Rich](https://rich.readthedocs.io/) for beautiful CLI interfaces

---

**Made with ❤️ for intelligent browser automation**
