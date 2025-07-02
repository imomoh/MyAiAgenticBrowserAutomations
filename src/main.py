import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from pathlib import Path

from .utils.logger import setup_logger
from .agent.browser_agent import BrowserAgent
from .utils.exceptions import AgentError

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """AI Browser Agent - Automate browser tasks with AI"""
    setup_logger()


@cli.command()
@click.option("--task", required=True, help="Task description for the AI agent")
@click.option("--headless", is_flag=True, default=False, help="Run browser in headless mode")
@click.option("--screenshot", is_flag=True, default=False, help="Take screenshot after task")
def execute(task: str, headless: bool, screenshot: bool):
    """Execute a single browser automation task"""
    
    console.print(Panel.fit(
        Text("AI Browser Agent", style="bold blue"),
        title="Starting",
        border_style="blue"
    ))
    
    try:
        with BrowserAgent() as agent:
            console.print(f"[yellow]Executing task:[/yellow] {task}")
            
            result = agent.execute_task(task)
            
            if result.success:
                console.print(f"[green]✓ Task completed successfully[/green]")
                if result.data:
                    console.print(f"[cyan]Result:[/cyan] {result.data}")
                
                if screenshot:
                    screenshot_result = agent.execute_task("take a screenshot")
                    if screenshot_result.success:
                        console.print(f"[green]✓ Screenshot saved[/green]")
            else:
                console.print(f"[red]✗ Task failed:[/red] {result.error}")
                
    except AgentError as e:
        console.print(f"[red]Agent Error:[/red] {e}")
    except Exception as e:
        console.print(f"[red]Unexpected Error:[/red] {e}")


@cli.command()
@click.option("--host", default="localhost", help="Host to bind the server")
@click.option("--port", default=8000, help="Port to bind the server")
def serve(host: str, port: int):
    """Start the agent as a web service (future implementation)"""
    console.print("[yellow]Web service mode not yet implemented[/yellow]")
    console.print("This will provide a REST API for browser automation tasks")


@cli.command() 
def interactive():
    """Start interactive mode for continuous task execution"""
    
    console.print(Panel.fit(
        Text("Interactive AI Browser Agent", style="bold green"),
        title="Starting Interactive Mode",
        border_style="green"
    ))
    
    try:
        with BrowserAgent() as agent:
            console.print("[green]Agent started successfully![/green]")
            console.print("[dim]Type 'quit' or 'exit' to stop[/dim]")
            
            while True:
                try:
                    task = console.input("\n[bold blue]Enter task:[/bold blue] ")
                    
                    if task.lower().strip() in ['quit', 'exit', 'q']:
                        break
                    
                    if not task.strip():
                        continue
                    
                    console.print(f"[yellow]Executing:[/yellow] {task}")
                    
                    result = agent.execute_task(task)
                    
                    if result.success:
                        console.print(f"[green]✓ Success[/green]")
                        if result.data:
                            console.print(f"[cyan]Result:[/cyan] {result.data}")
                    else:
                        console.print(f"[red]✗ Failed:[/red] {result.error}")
                        
                except KeyboardInterrupt:
                    console.print("\n[yellow]Task interrupted by user[/yellow]")
                    continue
                except Exception as e:
                    console.print(f"[red]Error:[/red] {e}")
            
            console.print("[green]Goodbye![/green]")
            
    except AgentError as e:
        console.print(f"[red]Agent Error:[/red] {e}")
    except Exception as e:
        console.print(f"[red]Unexpected Error:[/red] {e}")


@cli.command()
def config():
    """Show current configuration"""
    from .config.settings import settings
    
    console.print(Panel.fit("Configuration", style="bold blue"))
    
    console.print(f"[cyan]Agent Name:[/cyan] {settings.agent.agent_name}")
    console.print(f"[cyan]Max Retries:[/cyan] {settings.agent.max_retries}")
    console.print(f"[cyan]Timeout:[/cyan] {settings.agent.timeout_seconds}s")
    console.print(f"[cyan]Browser:[/cyan] {settings.browser.browser_type}")
    console.print(f"[cyan]Headless:[/cyan] {settings.browser.headless_mode}")
    console.print(f"[cyan]Window Size:[/cyan] {settings.browser.window_width}x{settings.browser.window_height}")
    console.print(f"[cyan]Log Level:[/cyan] {settings.logging.log_level}")
    console.print(f"[cyan]Log File:[/cyan] {settings.logging.log_file}")


@cli.command()
@click.option("--output", default="setup_instructions.md", help="Output file for setup instructions")
def setup_guide(output: str):
    """Generate setup instructions"""
    
    instructions = """# AI Browser Agent Setup Guide

## Prerequisites
- Python 3.9 or higher
- Chrome browser installed

## Installation

1. **Clone and navigate to the project:**
   ```bash
   cd ai-browser-agent
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\\Scripts\\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env file with your OpenAI API key
   ```

5. **Install pre-commit hooks (optional):**
   ```bash
   pre-commit install
   ```

## Usage

### Single Task Execution
```bash
python -m src.main execute --task "navigate to google.com and search for python"
```

### Interactive Mode
```bash
python -m src.main interactive
```

### Configuration
```bash
python -m src.main config
```

## Project Structure
```
ai-browser-agent/
├── src/
│   ├── agent/          # AI agent implementation
│   ├── browser/        # Browser automation
│   ├── config/         # Configuration management
│   └── utils/          # Utilities and helpers
├── tests/              # Test files
├── logs/               # Log files
├── data/               # Data storage
└── scripts/            # Utility scripts
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `BROWSER_TYPE` | Browser to use | chrome |
| `HEADLESS_MODE` | Run browser headlessly | false |
| `LOG_LEVEL` | Logging level | INFO |
| `MAX_RETRIES` | Max retry attempts | 3 |

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/ tests/
flake8 src/ tests/
mypy src/
```

### Adding New Actions
1. Add action type to `ActionType` enum in `browser_agent.py`
2. Implement action logic in `_execute_action` method
3. Update AI prompt in `_generate_action_plan` method
4. Add tests for the new action

## Troubleshooting

### Chrome Driver Issues
- Ensure Chrome browser is installed
- Check Chrome version compatibility with selenium
- Try running with `--headless` flag

### OpenAI API Issues
- Verify API key is correct in `.env` file
- Check API usage limits and billing
- Ensure network connectivity

### Permission Issues
- On macOS, you may need to allow Terminal to control System Events
- Grant accessibility permissions if needed

## Security Notes
- Never commit `.env` file with real API keys
- Use environment-specific configuration files
- Review generated actions before execution in production
- Consider rate limiting for API calls
"""
    
    Path(output).write_text(instructions)
    console.print(f"[green]Setup guide written to {output}[/green]")


def main():
    cli()


if __name__ == "__main__":
    main()