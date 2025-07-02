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
@click.option("--use-profile", is_flag=True, default=False, help="Use your existing Chrome profile (access logged-in accounts)")
@click.option("--profile-path", type=str, help="Custom path to Chrome profile directory")
@click.option("--profile-name", type=str, help="Specific Chrome profile name to use")
@click.option("--list-profiles", is_flag=True, default=False, help="List available Chrome profiles and exit")
def execute(task: str, headless: bool, screenshot: bool, use_profile: bool, profile_path: str, profile_name: str, list_profiles: bool):
    """Execute a single browser automation task"""
    
    # Override settings temporarily if flags are provided
    from .config.settings import settings
    original_headless = settings.browser.headless_mode
    original_use_profile = settings.browser.use_existing_profile
    original_profile_path = settings.browser.profile_path
    
    try:
        if headless:
            settings.browser.headless_mode = True
        if use_profile:
            settings.browser.use_existing_profile = True
        if profile_path:
            settings.browser.profile_path = profile_path
        
        # Handle profile listing
        if list_profiles:
            from .browser.chrome_driver import ChromeDriver
            driver = ChromeDriver()
            profiles = driver.get_available_profiles()
            
            if not profiles:
                console.print("[red]No Chrome profiles found[/red]")
                return
            
            console.print("\n📁 Available Chrome Profiles:")
            console.print("=" * 50)
            for i, profile in enumerate(profiles, 1):
                profile_info = f"{i}. {profile}"
                if profile.is_default:
                    console.print(f"[bold green]{profile_info}[/bold green]")
                else:
                    console.print(profile_info)
            console.print("=" * 50)
            console.print("\nUse --profile-name to specify a profile, or --use-profile to be prompted for selection.")
            return
        
        console.print(Panel.fit(
            Text("AI Browser Agent", style="bold blue"),
            title="Starting",
            border_style="blue"
        ))
        
        if use_profile:
            console.print("[yellow]Using your existing Chrome profile - you'll have access to logged-in accounts[/yellow]")
            if profile_name:
                console.print(f"[cyan]Selected profile:[/cyan] {profile_name}")
        
        with BrowserAgent(profile_name=profile_name) as agent:
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
    finally:
        # Restore original settings
        settings.browser.headless_mode = original_headless
        settings.browser.use_existing_profile = original_use_profile
        settings.browser.profile_path = original_profile_path


@cli.command()
@click.option("--host", default="localhost", help="Host to bind the server")
@click.option("--port", default=8000, help="Port to bind the server")
def serve(host: str, port: int):
    """Start the agent as a web service (future implementation)"""
    console.print("[yellow]Web service mode not yet implemented[/yellow]")
    console.print("This will provide a REST API for browser automation tasks")


@cli.command() 
@click.option("--use-profile", is_flag=True, default=False, help="Use your existing Chrome profile (access logged-in accounts)")
@click.option("--profile-path", type=str, help="Custom path to Chrome profile directory")
@click.option("--profile-name", type=str, help="Specific Chrome profile name to use")
@click.option("--list-profiles", is_flag=True, default=False, help="List available Chrome profiles and exit")
@click.option("--clean-profile", is_flag=True, default=False, help="Use a clean profile to avoid verification prompts")
def interactive(use_profile: bool, profile_path: str, profile_name: str, list_profiles: bool, clean_profile: bool):
    """Start interactive mode for continuous task execution"""
    
    # Override settings temporarily if flags are provided
    from .config.settings import settings
    original_use_profile = settings.browser.use_existing_profile
    original_profile_path = settings.browser.profile_path
    
    try:
        if clean_profile:
            # Use clean profile to avoid verification prompts
            settings.browser.use_existing_profile = False
            console.print("[yellow]Using clean profile to avoid verification prompts[/yellow]")
        elif use_profile:
            settings.browser.use_existing_profile = True
        if profile_path:
            settings.browser.profile_path = profile_path
        
        # Handle profile listing
        if list_profiles:
            from .browser.chrome_driver import ChromeDriver
            driver = ChromeDriver()
            profiles = driver.get_available_profiles()
            
            if not profiles:
                console.print("[red]No Chrome profiles found[/red]")
                return
            
            console.print("\n📁 Available Chrome Profiles:")
            console.print("=" * 50)
            for i, profile in enumerate(profiles, 1):
                profile_info = f"{i}. {profile}"
                if profile.is_default:
                    console.print(f"[bold green]{profile_info}[/bold green]")
                else:
                    console.print(profile_info)
            console.print("=" * 50)
            console.print("\nUse --profile-name to specify a profile, or --use-profile to be prompted for selection.")
            return
            
        console.print(Panel.fit(
            Text("Interactive AI Browser Agent", style="bold green"),
            title="Starting Interactive Mode",
            border_style="green"
        ))
        
        if use_profile:
            console.print("[yellow]Using your existing Chrome profile - you'll have access to logged-in accounts[/yellow]")
            if profile_name:
                console.print(f"[cyan]Selected profile:[/cyan] {profile_name}")
        
        # Create agent but start it manually to maintain persistent connection
        agent = BrowserAgent(profile_name=profile_name)
        
        try:
            agent.start()
            console.print("[green]Agent started successfully![/green]")
            console.print("[yellow]Chrome window opened - keep it open for continuous interaction[/yellow]")
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
            
        finally:
            # Clean up: stop the agent properly
            try:
                agent.stop()
            except Exception as e:
                console.print(f"[yellow]Warning: Error stopping agent: {e}[/yellow]")
            
    except AgentError as e:
        console.print(f"[red]Agent Error:[/red] {e}")
    except Exception as e:
        console.print(f"[red]Unexpected Error:[/red] {e}")
    finally:
        # Restore original settings
        settings.browser.use_existing_profile = original_use_profile
        settings.browser.profile_path = original_profile_path


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
@click.option("--use-profile", is_flag=True, default=True, help="Use your existing Chrome profile (default: True)")
@click.option("--profile-path", type=str, help="Custom path to Chrome profile directory")
@click.option("--profile-name", type=str, help="Specific Chrome profile name to use")
@click.option("--list-profiles", is_flag=True, default=False, help="List available Chrome profiles and exit")
def run_interactive_profile(use_profile: bool, profile_path: str, profile_name: str, list_profiles: bool):
    """Run interactive mode with persistent Chrome profile connection"""
    
    # Override settings temporarily if flags are provided
    from .config.settings import settings
    original_use_profile = settings.browser.use_existing_profile
    original_profile_path = settings.browser.profile_path
    
    try:
        if use_profile:
            settings.browser.use_existing_profile = True
        if profile_path:
            settings.browser.profile_path = profile_path
        
        # Handle profile listing
        if list_profiles:
            from .browser.chrome_driver import ChromeDriver
            driver = ChromeDriver()
            profiles = driver.get_available_profiles()
            
            if not profiles:
                console.print("[red]No Chrome profiles found[/red]")
                return
            
            console.print("\n📁 Available Chrome Profiles:")
            console.print("=" * 50)
            for i, profile in enumerate(profiles, 1):
                profile_info = f"{i}. {profile}"
                if profile.is_default:
                    console.print(f"[bold green]{profile_info}[/bold green]")
                else:
                    console.print(profile_info)
            console.print("=" * 50)
            console.print("\nUse --profile-name to specify a profile, or --use-profile to be prompted for selection.")
            return
            
        console.print(Panel.fit(
            Text("Interactive AI Browser Agent with Persistent Profile", style="bold green"),
            title="Starting Interactive Profile Mode",
            border_style="green"
        ))
        
        console.print("[yellow]Using your existing Chrome profile with persistent connection[/yellow]")
        if profile_name:
            console.print(f"[cyan]Selected profile:[/cyan] {profile_name}")
        
        # Create agent with manual interaction and persistent connection enabled
        agent = BrowserAgent(profile_name=profile_name, keep_browser_open=True, manual_interaction=True)
        
        try:
            agent.start()
            current_url = agent.driver.get_current_url()
            console.print("[green]Agent started successfully![/green]")
            console.print(f"[cyan]Current page:[/cyan] {current_url}")
            console.print("[yellow]🎉 Mixed manual/automated mode enabled![/yellow]")
            console.print("[green]✅ You can now interact with the Chrome window manually[/green]")
            console.print("[green]✅ The agent will work with your manual changes[/green]")
            console.print("")
            console.print("[bold blue]Available commands:[/bold blue]")
            console.print("[dim]  • 'quit' or 'exit' - Stop the agent[/dim]")
            console.print("[dim]  • 'url' - Show current page URL[/dim]")
            console.print("[dim]  • 'screenshot' - Take a screenshot[/dim]")
            console.print("[dim]  • 'sync' - Sync with manual changes[/dim]")
            console.print("[dim]  • Any other text - Execute as automation task[/dim]")
            
            while True:
                try:
                    task = console.input("\n[bold blue]Enter task:[/bold blue] ")
                    
                    if task.lower().strip() in ['quit', 'exit', 'q']:
                        break
                    
                    if not task.strip():
                        continue
                    
                    # Handle special commands
                    if task.lower().strip() == 'url':
                        current_url = agent.driver.get_current_url()
                        console.print(f"[cyan]Current URL:[/cyan] {current_url}")
                        continue
                    elif task.lower().strip() == 'screenshot':
                        result = agent.execute_task("take a screenshot")
                        if result.success:
                            console.print(f"[green]✓ Screenshot saved[/green]")
                        else:
                            console.print(f"[red]✗ Screenshot failed:[/red] {result.error}")
                        continue
                    elif task.lower().strip() == 'sync':
                        console.print("[yellow]Syncing with manual changes...[/yellow]")
                        state = agent.get_current_state()
                        if "error" not in state:
                            console.print(f"[green]✓ Synced![/green]")
                            console.print(f"[cyan]Current URL:[/cyan] {state.get('url', 'unknown')}")
                            console.print(f"[cyan]Page Title:[/cyan] {state.get('title', 'unknown')}")
                            console.print(f"[cyan]Page Ready:[/cyan] {state.get('ready_state', 'unknown')}")
                            console.print(f"[cyan]Windows Open:[/cyan] {state.get('window_handles', 'unknown')}")
                        else:
                            console.print(f"[red]✗ Sync failed:[/red] {state.get('error', 'unknown')}")
                        continue
                    
                    console.print(f"[yellow]Executing:[/yellow] {task}")
                    
                    # Auto-sync before each automated task in manual interaction mode
                    agent.sync_with_manual_changes()
                    
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
            
            console.print("[green]Goodbye! Chrome window will remain open.[/green]")
            
        finally:
            # Don't close Chrome - leave it open for user to continue
            console.print("[yellow]Chrome window left open for you to continue manually[/yellow]")
            
    except AgentError as e:
        console.print(f"[red]Agent Error:[/red] {e}")
    except Exception as e:
        console.print(f"[red]Unexpected Error:[/red] {e}")
    finally:
        # Restore original settings
        settings.browser.use_existing_profile = original_use_profile
        settings.browser.profile_path = original_profile_path


@cli.command()
def list_profiles():
    """List available Chrome profiles"""
    from .browser.chrome_driver import ChromeDriver
    
    console.print(Panel.fit("Chrome Profiles", style="bold blue"))
    
    try:
        driver = ChromeDriver()
        profiles = driver.get_available_profiles()
        
        if not profiles:
            console.print("[red]No Chrome profiles found[/red]")
            console.print("\nMake sure Chrome is installed and you have at least one profile set up.")
            return
        
        console.print(f"\n📁 Found {len(profiles)} Chrome profile(s):")
        console.print("=" * 60)
        
        for i, profile in enumerate(profiles, 1):
            profile_info = f"{i}. {profile}"
            if profile.is_default:
                console.print(f"[bold green]{profile_info}[/bold green]")
            else:
                console.print(profile_info)
        
        console.print("=" * 60)
        console.print("\n[dim]Usage:[/dim]")
        console.print("  • Use --use-profile to be prompted for selection")
        console.print("  • Use --profile-name 'Profile Name' to specify directly")
        console.print("  • Use --profile-path '/path/to/profile' for custom location")
        
    except Exception as e:
        console.print(f"[red]Error listing profiles:[/red] {e}")


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


@cli.command()
@click.option("--url", required=True, help="URL to navigate to")
@click.option("--screenshot", is_flag=True, default=False, help="Take screenshot after navigation")
@click.option("--use-profile", is_flag=True, default=False, help="Use your existing Chrome profile")
def direct(url: str, screenshot: bool, use_profile: bool):
    """Execute direct browser actions without AI (for testing)"""
    
    # Override settings temporarily if flags are provided
    from .config.settings import settings
    original_use_profile = settings.browser.use_existing_profile
    
    try:
        if use_profile:
            settings.browser.use_existing_profile = True
        
        console.print(Panel.fit(
            Text("Direct Browser Control", style="bold green"),
            title="Starting",
            border_style="green"
        ))
        
        if use_profile:
            console.print("[yellow]Using your existing Chrome profile[/yellow]")
        
        from .browser.chrome_driver import ChromeDriver
        
        with ChromeDriver() as driver:
            console.print(f"[yellow]Navigating to:[/yellow] {url}")
            
            # Navigate directly
            driver.navigate_to(url)
            
            # Get current URL to confirm
            current_url = driver.get_current_url()
            console.print(f"[green]✓ Successfully navigated to:[/green] {current_url}")
            
            # Take screenshot if requested
            if screenshot:
                filename = f"direct_{int(__import__('time').time())}.png"
                success = driver.take_screenshot(filename)
                if success:
                    console.print(f"[green]✓ Screenshot saved:[/green] {filename}")
                else:
                    console.print("[red]✗ Failed to take screenshot[/red]")
            
            # Get page title
            try:
                title = driver.execute_script("return document.title;")
                console.print(f"[cyan]Page title:[/cyan] {title}")
            except Exception as e:
                console.print(f"[yellow]Could not get page title:[/yellow] {e}")
                
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
    finally:
        # Restore original settings
        settings.browser.use_existing_profile = original_use_profile


def main():
    cli()


if __name__ == "__main__":
    main()