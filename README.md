# AI Browser Agent

[![CI](https://github.com/your-username/ai-browser-agent/workflows/CI/badge.svg)](https://github.com/your-username/ai-browser-agent/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent AI-powered browser automation agent that understands natural language commands and performs web automation tasks using OpenAI's GPT models and Selenium WebDriver.

## 🌟 Features

- **Natural Language Control**: Describe what you want to do in plain English
- **Intelligent Action Planning**: AI analyzes the current page context and plans optimal actions
- **Browser Automation**: Full Chrome browser control with Selenium WebDriver
- **Screenshot Capture**: Automatic screenshot generation for visual verification
- **Action History**: Track all performed actions with detailed logging
- **CLI Interface**: Professional command-line interface with rich formatting
- **Retry Logic**: Robust error handling with configurable retry mechanisms
- **Headless Mode**: Run browser automation in the background
- **Comprehensive Testing**: 94%+ test coverage with unit and integration tests

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Chrome browser installed
- OpenAI API key

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/ai-browser-agent.git
   cd ai-browser-agent
   ```

2. **Set up virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

### Usage Examples

#### Interactive Mode
```bash
python -m src.main interactive
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
# Navigate to a website
python -m src.main execute --task "go to github.com"

# Take a screenshot in headless mode
python -m src.main execute --task "take a screenshot" --headless

# Complex multi-step task
python -m src.main execute --task "navigate to google.com and search for python selenium"
```

#### Configuration Management
```bash
# View current configuration
python -m src.main config

# Show available commands
python -m src.main --help
```

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

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `BROWSER_TYPE` | Browser to use | `chrome` |
| `HEADLESS_MODE` | Run browser headlessly | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `MAX_RETRIES` | Max retry attempts | `3` |
| `TIMEOUT_SECONDS` | Action timeout | `30` |

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