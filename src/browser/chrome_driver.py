from typing import Optional, List, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger
from pathlib import Path

from ..config.settings import settings


class ChromeDriver:
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None

    def start(self) -> None:
        try:
            chrome_options = self._get_chrome_options()
            service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, settings.agent.timeout_seconds)
            
            self.driver.set_window_size(
                settings.browser.window_width, 
                settings.browser.window_height
            )
            
            logger.info("Chrome driver started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Chrome driver: {e}")
            raise

    def stop(self) -> None:
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Chrome driver stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping Chrome driver: {e}")
            finally:
                self.driver = None
                self.wait = None

    def navigate_to(self, url: str) -> None:
        if not self.driver:
            raise RuntimeError("Driver not started")
        
        try:
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            raise

    def find_element(self, by: By, value: str, timeout: Optional[int] = None) -> Any:
        if not self.driver or not self.wait:
            raise RuntimeError("Driver not started")
        
        try:
            wait_time = timeout or settings.agent.timeout_seconds
            wait = WebDriverWait(self.driver, wait_time)
            element = wait.until(EC.presence_of_element_located((by, value)))
            return element
        except Exception as e:
            logger.error(f"Failed to find element {by}={value}: {e}")
            raise

    def find_elements(self, by: By, value: str) -> List[Any]:
        if not self.driver:
            raise RuntimeError("Driver not started")
        
        try:
            elements = self.driver.find_elements(by, value)
            return elements
        except Exception as e:
            logger.error(f"Failed to find elements {by}={value}: {e}")
            raise

    def click_element(self, by: By, value: str, timeout: Optional[int] = None) -> None:
        element = self.find_element(by, value, timeout)
        try:
            element.click()
            logger.info(f"Clicked element {by}={value}")
        except Exception as e:
            logger.error(f"Failed to click element {by}={value}: {e}")
            raise

    def send_keys(self, by: By, value: str, text: str, timeout: Optional[int] = None) -> None:
        element = self.find_element(by, value, timeout)
        try:
            element.clear()
            element.send_keys(text)
            logger.info(f"Sent keys to element {by}={value}")
        except Exception as e:
            logger.error(f"Failed to send keys to element {by}={value}: {e}")
            raise

    def get_text(self, by: By, value: str, timeout: Optional[int] = None) -> str:
        element = self.find_element(by, value, timeout)
        try:
            text = element.text
            logger.info(f"Got text from element {by}={value}: {text[:50]}...")
            return text
        except Exception as e:
            logger.error(f"Failed to get text from element {by}={value}: {e}")
            raise

    def get_attribute(self, by: By, value: str, attribute: str, timeout: Optional[int] = None) -> str:
        element = self.find_element(by, value, timeout)
        try:
            attr_value = element.get_attribute(attribute)
            logger.info(f"Got attribute '{attribute}' from element {by}={value}: {attr_value}")
            return attr_value or ""
        except Exception as e:
            logger.error(f"Failed to get attribute '{attribute}' from element {by}={value}: {e}")
            raise

    def execute_script(self, script: str) -> Any:
        if not self.driver:
            raise RuntimeError("Driver not started")
        
        try:
            result = self.driver.execute_script(script)
            logger.info(f"Executed script: {script[:50]}...")
            return result
        except Exception as e:
            logger.error(f"Failed to execute script: {e}")
            raise

    def take_screenshot(self, filename: str) -> bool:
        if not self.driver:
            raise RuntimeError("Driver not started")
        
        try:
            screenshot_path = Path("screenshots") / filename
            screenshot_path.parent.mkdir(exist_ok=True)
            
            success = self.driver.save_screenshot(str(screenshot_path))
            if success:
                logger.info(f"Screenshot saved: {screenshot_path}")
            return success
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return False

    def get_page_source(self) -> str:
        if not self.driver:
            raise RuntimeError("Driver not started")
        
        try:
            source = self.driver.page_source
            logger.info(f"Got page source ({len(source)} characters)")
            return source
        except Exception as e:
            logger.error(f"Failed to get page source: {e}")
            raise

    def get_current_url(self) -> str:
        if not self.driver:
            raise RuntimeError("Driver not started")
        
        try:
            url = self.driver.current_url
            logger.info(f"Current URL: {url}")
            return url
        except Exception as e:
            logger.error(f"Failed to get current URL: {e}")
            raise

    def _get_chrome_options(self) -> Options:
        chrome_options = Options()
        
        if settings.browser.headless_mode:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        if settings.browser.user_data_dir:
            user_data_path = Path(settings.browser.user_data_dir)
            user_data_path.mkdir(exist_ok=True)
            chrome_options.add_argument(f"--user-data-dir={user_data_path}")
        
        return chrome_options

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()