from typing import Optional, List, Dict, Any
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from loguru import logger
from pathlib import Path
import json
import platform
import time

from ..config.settings import settings


class ChromeProfile:
    """Represents a Chrome profile with its metadata."""
    
    def __init__(self, name: str, path: Path, email: Optional[str] = None, is_default: bool = False):
        self.name = name
        self.path = path
        self.email = email
        self.is_default = is_default
    
    def __str__(self):
        email_info = f" ({self.email})" if self.email else ""
        default_info = " [Default]" if self.is_default else ""
        return f"{self.name}{email_info}{default_info}"
    
    def __repr__(self):
        return f"ChromeProfile(name='{self.name}', email='{self.email}', is_default={self.is_default})"


class ChromeDriver:
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.selected_profile: Optional[ChromeProfile] = None
        self.keep_browser_open: bool = False
        self.manual_interaction_mode: bool = False

    def start(self, profile_name: Optional[str] = None) -> None:
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Handle profile selection if using existing profiles
                if settings.browser.use_existing_profile and not self.selected_profile:
                    self.select_profile(profile_name)
                
                print("🚀 Starting browser...")  # User-friendly message
                logger.info(f"🔄 Starting browser (attempt {attempt + 1}/{max_retries})")
                
                self.playwright = sync_playwright().start()
                
                # Prepare persistent context args
                context_args = self._get_context_args()
                user_data_dir = context_args.pop("user_data_dir", None)
                
                if user_data_dir:
                    self.context = self.playwright.chromium.launch_persistent_context(
                        user_data_dir=user_data_dir,
                        executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                        headless=settings.browser.headless_mode,
                        args=self._get_browser_args(),
                        **context_args
                    )
                else:
                    # fallback to non-persistent context for automation
                    self.browser = self.playwright.chromium.launch(
                        executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                        headless=settings.browser.headless_mode,
                        args=self._get_browser_args()
                    )
                    # Remove keys not supported by new_context
                    context_args.pop('args', None)
                    context_args.pop('user_data_dir', None)
                    self.context = self.browser.new_context(**context_args)
                
                # Use the first page if it exists, otherwise create a new one
                if self.context.pages:
                    self.page = self.context.pages[0]
                else:
                    self.page = self.context.new_page()
                
                # Wait a moment for the browser to fully initialize
                time.sleep(2)
                
                # Try to get the current URL to verify the browser is responsive
                try:
                    self.page.url
                except Exception as url_error:
                    logger.warning(f"⚠️ Browser started but may not be fully responsive")
                    # Continue anyway, as this might be a temporary issue
                
                if self.selected_profile:
                    logger.info(f"✅ Browser started with profile: {self.selected_profile.name}")
                else:
                    logger.info("🚀 Browser started successfully")
                
                return  # Success, exit the retry loop
                
            except Exception as e:
                last_error = e
                logger.warning(f"⚠️ Browser start attempt {attempt + 1} failed")
                
                # Clean up any partial instances
                self._cleanup()
                
                # Wait before retrying
                if attempt < max_retries - 1:
                    time.sleep(2)
        
        # All retries failed
                    logger.error(f"❌ Failed to start browser after {max_retries} attempts")
        
        # Check if the error is due to profile being in use
        if "ProcessSingleton" in str(last_error) and "profile is already in use" in str(last_error):
            error_msg = f"""
❌ Chrome Profile Conflict Detected

Your Chrome profile is currently in use by another Chrome instance. 
To resolve this:

1. Close ALL Chrome windows completely:
   • Press Cmd+Q while Chrome is active, OR
   • Right-click Chrome in dock → "Quit"
   • Make sure Chrome is completely closed

2. Then run the command again.

Alternatively, you can run without --use-profile to use a clean browser session:
   python -m src.main execute --task "your task here"
"""
            raise RuntimeError(error_msg)
        
        raise last_error

    def stop(self) -> None:
        if not self.keep_browser_open:
            self._cleanup()
            logger.info("🛑 Browser stopped successfully")
        else:
            logger.info("Playwright browser kept open as requested")

    def _cleanup(self) -> None:
        """Clean up Playwright resources."""
        try:
            if self.page:
                self.page.close()
        except Exception as e:
            logger.error(f"Error closing page: {e}")
        finally:
            self.page = None
            
        try:
            if self.context:
                self.context.close()
        except Exception as e:
            logger.error(f"Error closing context: {e}")
        finally:
            self.context = None
            
        try:
            if self.browser:
                self.browser.close()
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
        finally:
            self.browser = None
            
        try:
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            logger.error(f"Error stopping playwright: {e}")
        finally:
            self.playwright = None

    def set_keep_open(self, keep_open: bool = True) -> None:
        """Set whether to keep the browser open when stopping the driver."""
        self.keep_browser_open = keep_open
        if keep_open:
            logger.info("Browser will be kept open when agent stops")

    def enable_manual_interaction(self, enable: bool = True) -> None:
        """Enable/disable manual interaction mode for mixed control."""
        self.manual_interaction_mode = enable
        if enable:
            logger.info("Manual interaction mode enabled - you can interact with the browser window")
        else:
            logger.info("Manual interaction mode disabled")

    def sync_with_manual_changes(self) -> Dict[str, Any]:
        """Sync agent state with any manual changes made to the browser."""
        if not self.page:
            return {"error": "Page not started"}
        
        try:
            # Get current page state
            current_state = {
                "url": self.page.url,
                "title": self.page.title(),
                "ready_state": self.page.evaluate("document.readyState"),
                "window_handles": len(self.context.pages),
                "active_element": self.page.evaluate("document.activeElement.tagName") or "unknown"
            }
            logger.info(f"Synced with manual changes - Current URL: {current_state['url']}")
            return current_state
        except Exception as e:
            logger.warning(f"Failed to sync with manual changes: {e}")
            return {"error": str(e)}

    def is_browser_alive(self) -> bool:
        """Check if the browser is still alive and responsive."""
        try:
            if not self.page:
                return False
            # Try to get the current URL to test responsiveness
            self.page.url
            return True
        except Exception:
            return False

    def ensure_window_focus(self) -> bool:
        """Ensure the browser window is focused."""
        try:
            if self.page:
                # Bring page to front
                self.page.bring_to_front()
                return True
        except Exception as e:
            logger.warning(f"Failed to focus window: {e}")
        return False

    def navigate_to(self, url: str) -> None:
        if not self.page:
            raise RuntimeError("Page not started")
        
        try:
            logger.info(f"🚀 Navigating to: {url}")
            self.page.goto(url)
        except Exception as e:
            logger.error(f"❌ Failed to navigate to page: {e}")
            raise

    def find_element(self, by: str, value: str, timeout: Optional[int] = None) -> Any:
        if not self.page:
            raise RuntimeError("Page not started")
        
        wait_time = timeout or settings.agent.timeout_seconds * 1000  # Convert to milliseconds
        selector = self._convert_selenium_selector(by, value)
        
        logger.info(f"🔍 Looking for element: {by}={value} (selector: {selector})")
        
        # Strategy 1: Try to find element immediately (no wait)
        try:
            element = self.page.query_selector(selector)
            if element:
                logger.info(f"✅ Element found immediately")
                return element
        except Exception as e:
            logger.debug(f"Immediate search failed: {e}")
        
        # Strategy 2: Wait for element to be present (but not necessarily visible)
        try:
            logger.info(f"⏳ Waiting for element to be present...")
            element = self.page.wait_for_selector(selector, timeout=wait_time, state="attached")
            if element:
                logger.info(f"✅ Element found (attached to DOM)")
                return element
        except Exception as e:
            logger.warning(f"⚠️ Element not found in DOM: {e}")
        
        # Strategy 3: Try alternative selectors if the original failed
        alternative_selectors = self._generate_alternative_selectors(by, value)
        for alt_selector in alternative_selectors:
            try:
                logger.info(f"🔄 Trying alternative selector: {alt_selector}")
                element = self.page.query_selector(alt_selector)
                if element:
                    logger.info(f"✅ Element found with alternative selector")
                    return element
            except Exception as e:
                logger.debug(f"Alternative selector failed: {e}")
        
        # Strategy 4: Try to find by text content if it's a button/link
        if by in ["link_text", "partial_link_text"] or "button" in value.lower() or "link" in value.lower():
            try:
                text_selector = f"text={value}"
                logger.info(f"🔄 Trying text-based selector: {text_selector}")
                element = self.page.query_selector(text_selector)
                if element:
                    logger.info(f"✅ Element found by text")
                    return element
            except Exception as e:
                logger.debug(f"Text-based selector failed: {e}")
        
        # Strategy 5: Try to find any interactive element with similar text
        try:
            logger.info(f"🔄 Searching for interactive elements with similar text...")
            elements = self.page.query_selector_all("button, a, input, [role='button'], [tabindex]")
            for elem in elements:
                try:
                    text = elem.text_content() or elem.get_attribute("value") or elem.get_attribute("placeholder") or ""
                    if value.lower() in text.lower() or text.lower() in value.lower():
                        logger.info(f"✅ Found element with similar text: '{text}'")
                        return elem
                except Exception:
                    continue
        except Exception as e:
            logger.debug(f"Interactive element search failed: {e}")
        
        # If all strategies fail, raise a detailed error
        error_msg = f"Element not found after trying multiple strategies: {by}={value}"
        logger.error(f"❌ {error_msg}")
        
        # Take a screenshot for debugging
        try:
            debug_filename = f"element_not_found_{int(time.time())}.png"
            self.take_screenshot(debug_filename)
            logger.info(f"📸 Debug screenshot saved: {debug_filename}")
        except Exception as e:
            logger.warning(f"Could not take debug screenshot: {e}")
        
        raise Exception(error_msg)

    def _generate_alternative_selectors(self, by: str, value: str) -> List[str]:
        """Generate alternative selectors for better element finding."""
        alternatives = []
        
        if by == "id":
            # Try without # prefix
            alternatives.append(value)
            # Try with different casing
            alternatives.append(value.lower())
            alternatives.append(value.upper())
        elif by == "css":
            # Try without any prefix
            if value.startswith("#"):
                alternatives.append(value[1:])
            elif value.startswith("."):
                alternatives.append(value[1:])
            # Try with different casing
            alternatives.append(value.lower())
            alternatives.append(value.upper())
        elif by == "name":
            # Try as ID
            alternatives.append(f"#{value}")
            # Try as class
            alternatives.append(f".{value}")
        elif by == "class_name":
            # Try as ID
            alternatives.append(f"#{value}")
            # Try without dot prefix
            alternatives.append(value)
        
        # Add common variations
        if "button" in value.lower():
            alternatives.extend([
                f"button:has-text('{value}')",
                f"[role='button']:has-text('{value}')",
                f"input[type='button'][value='{value}']",
                f"input[type='submit'][value='{value}']"
            ])
        
        if "link" in value.lower() or by in ["link_text", "partial_link_text"]:
            alternatives.extend([
                f"a:has-text('{value}')",
                f"a[href*='{value}']"
            ])
        
        return alternatives

    def find_elements(self, by: str, value: str) -> List[Any]:
        if not self.page:
            raise RuntimeError("Page not started")
        
        try:
            selector = self._convert_selenium_selector(by, value)
            elements = self.page.query_selector_all(selector)
            return elements
        except Exception as e:
            logger.error(f"❌ Elements not found: {e}")
            raise

    def click_element(self, by: str, value: str, timeout: Optional[int] = None) -> None:
        element = self.find_element(by, value, timeout)
        
        logger.info(f"🖱️ Attempting to click element: {by}={value}")
        
        # Strategy 1: Try direct click
        try:
            element.click()
            logger.info(f"✅ Clicked on element successfully")
            return
        except Exception as e:
            logger.warning(f"⚠️ Direct click failed: {e}")
        
        # Strategy 2: Try to scroll element into view and click
        try:
            logger.info(f"🔄 Scrolling element into view...")
            element.scroll_into_view_if_needed()
            time.sleep(0.5)  # Brief pause for scroll animation
            element.click()
            logger.info(f"✅ Clicked on element after scrolling into view")
            return
        except Exception as e:
            logger.warning(f"⚠️ Click after scroll failed: {e}")
        
        # Strategy 3: Try to wait for element to be visible and clickable
        try:
            logger.info(f"⏳ Waiting for element to be visible and clickable...")
            wait_time = timeout or settings.agent.timeout_seconds * 1000
            element = self.page.wait_for_selector(
                self._convert_selenium_selector(by, value), 
                timeout=wait_time, 
                state="visible"
            )
            if element:
                element.click()
                logger.info(f"✅ Clicked on element after waiting for visibility")
                return
        except Exception as e:
            logger.warning(f"⚠️ Click after visibility wait failed: {e}")
        
        # Strategy 4: Try JavaScript click
        try:
            logger.info(f"🔄 Trying JavaScript click...")
            self.page.evaluate("(element) => element.click()", element)
            logger.info(f"✅ Clicked on element using JavaScript")
            return
        except Exception as e:
            logger.warning(f"⚠️ JavaScript click failed: {e}")
        
        # Strategy 5: Try to focus and press Enter
        try:
            logger.info(f"🔄 Trying focus and Enter key...")
            element.focus()
            time.sleep(0.2)
            element.press("Enter")
            logger.info(f"✅ Activated element using Enter key")
            return
        except Exception as e:
            logger.warning(f"⚠️ Focus and Enter failed: {e}")
        
        # Strategy 6: Try to check if element is actually clickable
        try:
            logger.info(f"🔍 Checking element properties...")
            
            # Check if element is visible
            is_visible = element.is_visible()
            logger.info(f"Element visible: {is_visible}")
            
            # Check if element is enabled
            is_enabled = element.is_enabled()
            logger.info(f"Element enabled: {is_enabled}")
            
            # Get element bounds
            bounding_box = element.bounding_box()
            if bounding_box:
                logger.info(f"Element bounds: {bounding_box}")
            
            # Check if element is covered by other elements
            is_covered = self.page.evaluate("""
                (element) => {
                    const rect = element.getBoundingClientRect();
                    const centerX = rect.left + rect.width / 2;
                    const centerY = rect.top + rect.height / 2;
                    const elementAtPoint = document.elementFromPoint(centerX, centerY);
                    return elementAtPoint !== element && !element.contains(elementAtPoint);
                }
            """, element)
            
            if is_covered:
                logger.warning(f"⚠️ Element appears to be covered by another element")
            
            # Try one more time with force click
            element.click(force=True)
            logger.info(f"✅ Clicked on element with force=True")
            return
            
        except Exception as e:
            logger.error(f"❌ All click strategies failed: {e}")
            
            # Take a screenshot for debugging
            try:
                debug_filename = f"click_failed_{int(time.time())}.png"
                self.take_screenshot(debug_filename)
                logger.info(f"📸 Debug screenshot saved: {debug_filename}")
            except Exception as screenshot_error:
                logger.warning(f"Could not take debug screenshot: {screenshot_error}")
            
            raise Exception(f"Failed to click element {by}={value} after trying multiple strategies: {e}")

    def send_keys(self, by: str, value: str, text: str, timeout: Optional[int] = None) -> None:
        element = self.find_element(by, value, timeout)
        try:
            element.fill(text)
            logger.info(f"📝 Typed text into field")
        except Exception as e:
            logger.error(f"❌ Failed to type text: {e}")
            raise

    def get_text(self, by: str, value: str, timeout: Optional[int] = None) -> str:
        element = self.find_element(by, value, timeout)
        try:
            text = element.text_content()
            logger.info(f"📖 Retrieved text from page")
            return text or ""
        except Exception as e:
            logger.error(f"❌ Failed to get text: {e}")
            raise

    def get_attribute(self, by: str, value: str, attribute: str, timeout: Optional[int] = None) -> str:
        element = self.find_element(by, value, timeout)
        try:
            attr_value = element.get_attribute(attribute)
            logger.info(f"Got attribute '{attribute}' from element {by}={value}: {attr_value}")
            return attr_value or ""
        except Exception as e:
            logger.error(f"Failed to get attribute '{attribute}' from element {by}={value}: {e}")
            raise

    def execute_script(self, script: str) -> Any:
        if not self.page:
            raise RuntimeError("Page not started")
        
        try:
            result = self.page.evaluate(script)
            logger.info(f"🔧 Executed JavaScript")
            return result
        except Exception as e:
            logger.error(f"❌ Failed to execute script: {e}")
            raise

    def take_screenshot(self, filename: str) -> bool:
        if not self.page:
            raise RuntimeError("Page not started")
        
        try:
            screenshot_path = Path("screenshots") / filename
            screenshot_path.parent.mkdir(exist_ok=True)
            
            self.page.screenshot(path=str(screenshot_path))
            logger.info(f"📸 Screenshot saved")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to take screenshot: {e}")
            return False

    def get_page_source(self) -> str:
        if not self.page:
            raise RuntimeError("Page not started")
        
        try:
            source = self.page.content()
            logger.info(f"📄 Retrieved page content")
            return source
        except Exception as e:
            logger.error(f"❌ Failed to get page content: {e}")
            raise

    def get_current_url(self) -> str:
        if not self.page:
            raise RuntimeError("Page not started")
        
        try:
            url = self.page.url
            logger.info(f"🌐 Current page: {url}")
            return url
        except Exception as e:
            logger.error(f"❌ Failed to get current URL: {e}")
            raise

    def _convert_selenium_selector(self, by: str, value: str) -> str:
        """Convert Selenium selector to Playwright selector."""
        if by == "id":
            return f"#{value}"
        elif by == "name":
            return f"[name='{value}']"
        elif by == "class_name":
            return f".{value}"
        elif by == "tag_name":
            return value
        elif by == "link_text":
            return f"text={value}"
        elif by == "partial_link_text":
            return f"text={value}"
        elif by == "css":
            return value
        elif by == "xpath":
            return value
        else:
            # Default to CSS selector
            return value

    def _get_browser_args(self) -> List[str]:
        """Get browser launch arguments."""
        args = []
        
        if self.manual_interaction_mode:
            # Minimal automation detection for better manual interaction
            args.extend([
                "--disable-blink-features=AutomationControlled",
                "--disable-features=VizDisplayCompositor"
            ])
        else:
            # Standard automation mode
            args.extend([
                "--disable-blink-features=AutomationControlled",
                "--disable-features=VizDisplayCompositor"
            ])
        
        # Basic flags to minimize prompts
        args.extend([
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-sync",
            "--disable-profile-picker",
            "--disable-features=ProfilePicker",
            "--disable-features=ChromeWhatsNewUI",
            "--disable-features=ChromeRefresh2023",
            "--disable-features=ChromeWebUIDarkMode"
        ])
        
        return args

    def _get_context_args(self) -> Dict[str, Any]:
        """Get context creation arguments."""
        context_args = {}
        
        if settings.browser.use_existing_profile and self.selected_profile:
            # Use specific profile directory to avoid verification prompts
            profile_path = self.selected_profile.path
            if profile_path.exists():
                context_args["user_data_dir"] = str(profile_path.parent)
                context_args["args"] = [f"--profile-directory={profile_path.name}"]
                logger.info(f"Using Chrome profile: {self.selected_profile.name} at {profile_path}")
            else:
                logger.warning(f"⚠️ Profile path does not exist")
        
        # Set viewport size
        context_args["viewport"] = {"width": 1920, "height": 1080}
        
        # Set user agent
        context_args["user_agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        # Add flags to minimize verification prompts
        if "args" not in context_args:
            context_args["args"] = []
        
        context_args["args"].extend([
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-sync",
            "--disable-profile-picker",
            "--disable-features=ProfilePicker",
            "--disable-features=ChromeWhatsNewUI",
            "--disable-features=ChromeRefresh2023",
            "--disable-features=ChromeWebUIDarkMode",
            "--disable-blink-features=AutomationControlled",
            "--disable-features=VizDisplayCompositor"
        ])
        
        return context_args

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def get_available_profiles(self) -> List[ChromeProfile]:
        """Get available Chrome profiles from the user data directory."""
        profiles = []
        
        try:
            chrome_data_dir = self._get_chrome_data_directory()
            if not chrome_data_dir:
                return profiles
            
            # Look for profile directories
            for item in chrome_data_dir.iterdir():
                if item.is_dir() and item.name.startswith("Profile "):
                    profile_name = item.name
                    profile_path = item
                    
                    # Try to get email from preferences
                    email = self._get_email_from_preferences(profile_path)
                    
                    # Check if this is the default profile
                    is_default = profile_name == "Default"
                    
                    profile = ChromeProfile(
                        name=profile_name,
                        path=profile_path,
                        email=email,
                        is_default=is_default
                    )
                    profiles.append(profile)
            
            # Sort profiles: Default first, then others alphabetically
            profiles.sort(key=lambda p: (not p.is_default, p.name))
            
            logger.info(f"📁 Found {len(profiles)} Chrome profiles")
            return profiles
            
        except Exception as e:
            logger.error(f"Failed to get available profiles: {e}")
            return profiles

    def _get_email_from_preferences(self, profile_path: Path) -> Optional[str]:
        """Extract email from Chrome profile preferences."""
        try:
            preferences_file = profile_path / "Preferences"
            if not preferences_file.exists():
                return None
            
            with open(preferences_file, 'r', encoding='utf-8') as f:
                prefs = json.load(f)
            
            # Try to get email from various locations in preferences
            email = None
            
            # Check account_id_migration_state
            if "account_id_migration_state" in prefs:
                account_state = prefs["account_id_migration_state"]
                if "account_id" in account_state:
                    email = account_state["account_id"]
            
            # Check signin
            if not email and "signin" in prefs:
                signin = prefs["signin"]
                if "last_used_account" in signin:
                    last_account = signin["last_used_account"]
                    if "email" in last_account:
                        email = last_account["email"]
            
            return email
            
        except Exception as e:
            logger.debug(f"Failed to extract email from preferences: {e}")
            return None

    def _get_chrome_data_directory(self) -> Optional[Path]:
        """Get the Chrome user data directory path."""
        if platform.system() == "Darwin":  # macOS
            return Path.home() / "Library/Application Support/Google/Chrome"
        elif platform.system() == "Windows":
            return Path.home() / "AppData/Local/Google/Chrome/User Data"
        elif platform.system() == "Linux":
            return Path.home() / ".config/google-chrome"
        else:
            logger.warning(f"Unsupported platform: {platform.system()}")
            return None

    def select_profile(self, profile_name: Optional[str] = None) -> ChromeProfile:
        """Select a Chrome profile to use."""
        profiles = self.get_available_profiles()
        
        if not profiles:
            raise RuntimeError("No Chrome profiles found")
        
        if profile_name:
            # Find profile by name
            for profile in profiles:
                if profile.name == profile_name:
                    self.selected_profile = profile
                    logger.info(f"👤 Using profile: {profile}")
                    return profile
            
            raise ValueError(f"Profile '{profile_name}' not found")
        else:
            # Prompt user to select profile
            self.selected_profile = self._prompt_profile_selection(profiles)
            return self.selected_profile

    def _prompt_profile_selection(self, profiles: List[ChromeProfile]) -> ChromeProfile:
        """Prompt user to select a profile."""
        print("\n📁 Available Chrome Profiles:")
        print("=" * 50)
        for i, profile in enumerate(profiles, 1):
            profile_info = f"{i}. {profile}"
            if profile.is_default:
                print(f"✓ {profile_info}")
            else:
                print(f"  {profile_info}")
        print("=" * 50)
        
        while True:
            try:
                choice = input(f"\nSelect profile (1-{len(profiles)}) or press Enter for default: ").strip()
                
                if not choice:
                    # Return default profile
                    for profile in profiles:
                        if profile.is_default:
                            return profile
                    # If no default, return first profile
                    return profiles[0]
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(profiles):
                    selected_profile = profiles[choice_num - 1]
                    print(f"Selected: {selected_profile}")
                    return selected_profile
                else:
                    print(f"Please enter a number between 1 and {len(profiles)}")
                    
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\nProfile selection cancelled")
                # Return default profile
                for profile in profiles:
                    if profile.is_default:
                        return profile
                return profiles[0]