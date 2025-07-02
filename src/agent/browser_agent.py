from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel
import openai
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from ..browser.chrome_driver import ChromeDriver
from ..config.settings import settings
from ..utils.exceptions import AgentError, BrowserError


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


class BrowserAction(BaseModel):
    action: ActionType
    parameters: Dict[str, Any]
    description: str


class ActionResult(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    screenshot_path: Optional[str] = None


class BrowserAgent:
    def __init__(self):
        self.driver = ChromeDriver()
        self.client = openai.OpenAI(api_key=settings.agent.openai_api_key)
        self.action_history: List[Dict[str, Any]] = []

    def start(self) -> None:
        try:
            self.driver.start()
            logger.info("Browser agent started successfully")
        except Exception as e:
            logger.error(f"Failed to start browser agent: {e}")
            raise AgentError(f"Failed to start browser agent: {e}")

    def stop(self) -> None:
        try:
            self.driver.stop()
            logger.info("Browser agent stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping browser agent: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def execute_task(self, task_description: str) -> ActionResult:
        try:
            logger.info(f"Executing task: {task_description}")
            
            # Get current page context
            context = self._get_page_context()
            
            # Generate action plan using AI
            action = self._generate_action_plan(task_description, context)
            
            # Execute the action
            result = self._execute_action(action)
            
            # Store in history
            self._store_action_history(task_description, action, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute task '{task_description}': {e}")
            return ActionResult(success=False, error=str(e))

    def _get_page_context(self) -> Dict[str, Any]:
        try:
            context = {
                "current_url": self.driver.get_current_url(),
                "page_title": self.driver.execute_script("return document.title;"),
                "viewport_info": self.driver.execute_script(
                    "return {width: window.innerWidth, height: window.innerHeight};"
                ),
            }
            
            # Get visible elements (basic implementation)
            try:
                visible_elements = self.driver.execute_script("""
                    const elements = document.querySelectorAll('*');
                    const visible = [];
                    for (let el of elements) {
                        const rect = el.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0 && 
                            rect.top >= 0 && rect.left >= 0 &&
                            rect.bottom <= window.innerHeight && 
                            rect.right <= window.innerWidth) {
                            visible.push({
                                tag: el.tagName,
                                id: el.id,
                                class: el.className,
                                text: el.textContent?.substring(0, 100),
                                type: el.type,
                                href: el.href
                            });
                        }
                    }
                    return visible.slice(0, 20);
                """)
                context["visible_elements"] = visible_elements
            except Exception as e:
                logger.warning(f"Could not get visible elements: {e}")
                context["visible_elements"] = []
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to get page context: {e}")
            return {"error": str(e)}

    def _generate_action_plan(self, task: str, context: Dict[str, Any]) -> BrowserAction:
        system_prompt = """
        You are a browser automation agent. Given a task description and current page context,
        you must return a JSON object representing the action to take.
        
        Available actions:
        - navigate: {"action": "navigate", "parameters": {"url": "https://example.com"}}
        - click: {"action": "click", "parameters": {"selector": "button#submit", "by": "css"}}
        - type: {"action": "type", "parameters": {"selector": "input[name='username']", "text": "mytext", "by": "css"}}
        - scroll: {"action": "scroll", "parameters": {"direction": "down", "amount": 300}}
        - wait: {"action": "wait", "parameters": {"seconds": 2}}
        - screenshot: {"action": "screenshot", "parameters": {"filename": "screenshot.png"}}
        - get_text: {"action": "get_text", "parameters": {"selector": "h1", "by": "css"}}
        - get_attribute: {"action": "get_attribute", "parameters": {"selector": "a", "attribute": "href", "by": "css"}}
        - execute_script: {"action": "execute_script", "parameters": {"script": "window.scrollTo(0, 0);"}}
        
        For 'by' parameter, use: 'css', 'xpath', 'id', 'name', 'tag', 'class', 'link_text', 'partial_link_text'
        
        Always include a 'description' field explaining what the action does.
        
        Return only valid JSON.
        """
        
        user_prompt = f"""
        Task: {task}
        
        Current page context:
        - URL: {context.get('current_url', 'unknown')}
        - Title: {context.get('page_title', 'unknown')}
        - Visible elements: {context.get('visible_elements', [])}
        
        Previous actions: {self.action_history[-3:] if self.action_history else []}
        
        What action should I take to complete this task?
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            action_json = response.choices[0].message.content.strip()
            logger.info(f"AI suggested action: {action_json}")
            
            # Parse the JSON response
            import json
            action_data = json.loads(action_json)
            
            return BrowserAction(**action_data)
            
        except Exception as e:
            logger.error(f"Failed to generate action plan: {e}")
            # Fallback to screenshot action
            return BrowserAction(
                action=ActionType.SCREENSHOT,
                parameters={"filename": "fallback_screenshot.png"},
                description="Taking screenshot for debugging"
            )

    def _execute_action(self, action: BrowserAction) -> ActionResult:
        try:
            logger.info(f"Executing action: {action.action} - {action.description}")
            
            if action.action == ActionType.NAVIGATE:
                url = action.parameters.get("url")
                self.driver.navigate_to(url)
                return ActionResult(success=True, data={"url": url})
            
            elif action.action == ActionType.CLICK:
                selector = action.parameters.get("selector")
                by_method = action.parameters.get("by", "css")
                by = self._get_by_method(by_method)
                self.driver.click_element(by, selector)
                return ActionResult(success=True, data={"clicked": selector})
            
            elif action.action == ActionType.TYPE:
                selector = action.parameters.get("selector")
                text = action.parameters.get("text")
                by_method = action.parameters.get("by", "css")
                by = self._get_by_method(by_method)
                self.driver.send_keys(by, selector, text)
                return ActionResult(success=True, data={"typed": text, "into": selector})
            
            elif action.action == ActionType.SCREENSHOT:
                filename = action.parameters.get("filename", "screenshot.png")
                success = self.driver.take_screenshot(filename)
                return ActionResult(
                    success=success, 
                    data={"filename": filename}, 
                    screenshot_path=filename if success else None
                )
            
            elif action.action == ActionType.GET_TEXT:
                selector = action.parameters.get("selector")
                by_method = action.parameters.get("by", "css")
                by = self._get_by_method(by_method)
                text = self.driver.get_text(by, selector)
                return ActionResult(success=True, data={"text": text})
            
            elif action.action == ActionType.GET_ATTRIBUTE:
                selector = action.parameters.get("selector")
                attribute = action.parameters.get("attribute")
                by_method = action.parameters.get("by", "css")
                by = self._get_by_method(by_method)
                value = self.driver.get_attribute(by, selector, attribute)
                return ActionResult(success=True, data={"attribute": attribute, "value": value})
            
            elif action.action == ActionType.EXECUTE_SCRIPT:
                script = action.parameters.get("script")
                result = self.driver.execute_script(script)
                return ActionResult(success=True, data={"result": result})
            
            elif action.action == ActionType.WAIT:
                seconds = action.parameters.get("seconds", 1)
                import time
                time.sleep(seconds)
                return ActionResult(success=True, data={"waited": seconds})
            
            elif action.action == ActionType.SCROLL:
                direction = action.parameters.get("direction", "down")
                amount = action.parameters.get("amount", 300)
                script = f"window.scrollBy(0, {amount if direction == 'down' else -amount});"
                self.driver.execute_script(script)
                return ActionResult(success=True, data={"scrolled": direction, "amount": amount})
            
            else:
                raise BrowserError(f"Unknown action type: {action.action}")
                
        except Exception as e:
            logger.error(f"Failed to execute action {action.action}: {e}")
            return ActionResult(success=False, error=str(e))

    def _get_by_method(self, by_method: str):
        from selenium.webdriver.common.by import By
        by_mapping = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "name": By.NAME,
            "tag": By.TAG_NAME,
            "class": By.CLASS_NAME,
            "link_text": By.LINK_TEXT,
            "partial_link_text": By.PARTIAL_LINK_TEXT,
        }
        return by_mapping.get(by_method.lower(), By.CSS_SELECTOR)

    def _store_action_history(
        self, 
        task: str, 
        action: BrowserAction, 
        result: ActionResult
    ) -> None:
        self.action_history.append({
            "task": task,
            "action": action.dict(),
            "result": result.dict(),
            "timestamp": __import__("datetime").datetime.now().isoformat()
        })
        
        # Keep only last 10 actions
        if len(self.action_history) > 10:
            self.action_history = self.action_history[-10:]

    def get_action_history(self) -> List[Dict[str, Any]]:
        return self.action_history.copy()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()