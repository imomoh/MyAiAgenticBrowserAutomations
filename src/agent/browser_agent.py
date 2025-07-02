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
    def __init__(self, profile_name: Optional[str] = None, keep_browser_open: bool = False, manual_interaction: bool = False):
        self.driver = ChromeDriver()
        self.client = openai.OpenAI(api_key=settings.agent.openai_api_key)
        self.action_history: List[Dict[str, Any]] = []
        self.current_plan: Optional[List[Dict[str, Any]]] = None
        self.plan_step: int = 0
        self.profile_name = profile_name
        self.keep_browser_open = keep_browser_open
        self.manual_interaction = manual_interaction
        
        if keep_browser_open:
            self.driver.set_keep_open(True)
        if manual_interaction:
            self.driver.enable_manual_interaction(True)

    def start(self) -> None:
        try:
            self.driver.start(self.profile_name)
            logger.info("🚀 Browser agent ready")
        except Exception as e:
            logger.error(f"Failed to start browser agent: {e}")
            raise AgentError(f"Failed to start browser agent: {e}")

    def stop(self) -> None:
        try:
            self.driver.stop()
            if not self.keep_browser_open:
                logger.info("🛑 Browser agent stopped")
            else:
                logger.info("Browser agent disconnected but browser kept open")
        except Exception as e:
            logger.error(f"Error stopping browser agent: {e}")

    def is_browser_alive(self) -> bool:
        """Check if the browser is still alive and responsive."""
        return self.driver.is_browser_alive()

    def take_screenshot(self, filename: str = None) -> bool:
        """Take a screenshot using the current driver."""
        if not filename:
            import time
            filename = f"screenshot_{int(time.time())}.png"
        
        return self.driver.take_screenshot(filename)

    def sync_with_manual_changes(self) -> Dict[str, Any]:
        """Sync agent state with any manual changes made to the browser."""
        return self.driver.sync_with_manual_changes()

    def get_current_state(self) -> Dict[str, Any]:
        """Get current browser state for manual interaction awareness."""
        try:
            state = self.sync_with_manual_changes()
            if "error" not in state:
                # Update context awareness after manual changes
                context = self._get_page_context()
                state.update({"context_updated": True, "page_context": context})
            return state
        except Exception as e:
            logger.error(f"Failed to get current state: {e}")
            return {"error": str(e)}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def execute_task(self, task_description: str) -> ActionResult:
        try:
            logger.info(f"🎯 Starting task: {task_description}")
            
            # Check if this is a complex task requiring multi-step planning
            if self._is_complex_task(task_description):
                return self._execute_complex_task(task_description)
            
            # Get page context and analyze situation for better awareness
            context = self._get_page_context()
            situation_analysis = self._analyze_situation(task_description, context)
            
            # Log situational awareness
            logger.info(f"🧠 Situational awareness: {situation_analysis.get('page_type', 'unknown')} page, {situation_analysis.get('recommended_approach', 'standard')} approach")
            if situation_analysis.get('potential_obstacles'):
                logger.info(f"⚠️ Potential obstacles: {', '.join(situation_analysis['potential_obstacles'])}")
            
            # Generate action plan with enhanced context
            action = self._generate_action_plan(task_description, context, situation_analysis)
            result = self._execute_action(action)
            self._store_action_history(task_description, action, result)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Task failed: {e}")
            return self._recover_from_error(task_description, str(e))

    def _get_page_context(self) -> Dict[str, Any]:
        """Simplified page context extraction for Playwright compatibility."""
        try:
            # Basic page information
            context = {
                "current_url": self.driver.get_current_url(),
            }
            
            # Get page title safely
            try:
                context["page_title"] = self.driver.execute_script("document.title")
            except Exception as e:
                logger.warning(f"⚠️ Could not get page title")
                context["page_title"] = "Unknown"
            
            # Get viewport info safely
            try:
                context["viewport_info"] = self.driver.execute_script(
                    "({width: window.innerWidth, height: window.innerHeight})"
                )
            except Exception as e:
                logger.warning(f"⚠️ Could not get viewport info")
                context["viewport_info"] = {"width": 1920, "height": 1080}
            
            # Get basic interactive elements (simplified)
            try:
                elements_script = """
                (() => {
                    const elements = document.querySelectorAll('a, button, input, select, textarea, [role="button"], [tabindex]');
                    const interactive = [];
                    
                    for (let el of elements) {
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        
                        if (rect.width > 0 && rect.height > 0 && 
                            style.visibility !== 'hidden' && 
                            style.display !== 'none') {
                            
                            // Get element text content
                            let text = '';
                            if (el.tagName === 'INPUT') {
                                text = el.value || el.placeholder || '';
                            } else {
                                text = el.textContent || el.innerText || '';
                            }
                            
                            // Get element attributes
                            const attributes = {};
                            for (let attr of el.attributes) {
                                if (['id', 'name', 'type', 'href', 'class', 'role', 'aria-label', 'title'].includes(attr.name)) {
                                    attributes[attr.name] = attr.value;
                                }
                            }
                            
                            // Determine best selector
                            let bestSelector = '';
                            if (el.id) {
                                bestSelector = `${el.tagName.toLowerCase()}#${el.id}`;
                            } else if (el.name && el.tagName === 'INPUT') {
                                bestSelector = `input[name='${el.name}']`;
                            } else if (text.trim()) {
                                bestSelector = `${el.tagName.toLowerCase()}:has-text('${text.trim().substring(0, 30)}')`;
                            } else if (el.className) {
                                const classes = el.className.split(' ').filter(c => c.trim());
                                if (classes.length > 0) {
                                    bestSelector = `${el.tagName.toLowerCase()}.${classes[0]}`;
                                }
                            }
                            
                            interactive.push({
                                tag: el.tagName.toLowerCase(),
                                id: el.id || '',
                                name: el.name || '',
                                type: el.type || '',
                                href: el.href || '',
                                text: text.substring(0, 50).trim(),
                                attributes: attributes,
                                best_selector: bestSelector,
                                is_visible: rect.width > 0 && rect.height > 0,
                                position: { x: rect.left, y: rect.top, width: rect.width, height: rect.height }
                            });
                        }
                    }
                    
                    return interactive.slice(0, 15);
                })()
                """
                context["interactive_elements"] = self.driver.execute_script(elements_script)
                
            except Exception as e:
                logger.warning(f"⚠️ Could not get interactive elements")
                context["interactive_elements"] = []
            
            # Get basic page info
            try:
                page_info_script = """
                (() => ({
                    forms: document.forms.length,
                    links: document.links.length,
                    images: document.images.length,
                    has_login: !!(document.querySelector('input[type=\"password\"]')),
                    has_search: !!(document.querySelector('input[type=\"search\"]')),
                    page_ready: document.readyState === 'complete'
                }))()
                """
                context["page_info"] = self.driver.execute_script(page_info_script)
                
            except Exception as e:
                logger.warning(f"⚠️ Could not get page info")
                context["page_info"] = {
                    "forms": 0,
                    "links": 0,
                    "images": 0,
                    "has_login": False,
                    "has_search": False,
                    "page_ready": True
                }
            
            # Add current plan context if available
            if self.current_plan:
                context["current_plan_step"] = self.plan_step
                context["total_plan_steps"] = len(self.current_plan)
                context["plan_progress"] = f"{self.plan_step + 1}/{len(self.current_plan)}"
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to get page context: {e}")
            return {"error": str(e), "current_url": "unknown"}

    def _generate_action_plan(self, task: str, context: Dict[str, Any], situation_analysis: Dict[str, Any] = None) -> BrowserAction:
        system_prompt = """
        You are a browser automation agent with enhanced situational awareness. Given a task description, current page context, and situation analysis,
        you must return a JSON object representing the most appropriate action to take.
        
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
        
        SITUATIONAL AWARENESS GUIDELINES:
        - Use the situation analysis to understand the current page type and recommended approach
        - Consider potential obstacles and adjust your strategy accordingly
        - For login pages, prioritize username/password fields
        - For search pages, look for search input fields
        - For forms, identify required fields and submit buttons
        - For checkout pages, be extra careful with sensitive information
        - For error pages, consider navigation or refresh actions
        
        ELEMENT SELECTION GUIDELINES:
        1. Prefer ID selectors when available (most reliable): "button#create-account"
        2. Use name attributes for form inputs: "input[name='username']"
        3. Use text content for buttons/links: "button:has-text('Create Account')" or "a:has-text('Login')"
        4. Use CSS selectors for complex elements: "button.btn-primary[type='submit']"
        5. Avoid class-only selectors unless very specific
        6. For buttons, prefer: button#id, button[name='name'], button:has-text('text')
        7. For links, prefer: a#id, a[href*='keyword'], a:has-text('text')
        8. For inputs, prefer: input#id, input[name='name'], input[type='type']
        
        Always include a 'description' field explaining what the action does.
        
        Return only valid JSON.
        """
        
        user_prompt = f"""
        Task: {task}
        
        Current page context:
        - URL: {context.get('current_url', 'unknown')}
        - Title: {context.get('page_title', 'unknown')}
        - Interactive elements: {context.get('interactive_elements', [])}
        - Page info: {context.get('page_info', {})}
        {f"- Plan progress: {context.get('plan_progress', '')}" if context.get('plan_progress') else ""}
        
        Situation Analysis:
        - Page Type: {situation_analysis.get('page_type', 'unknown') if situation_analysis else 'unknown'}
        - Recommended Approach: {situation_analysis.get('recommended_approach', 'standard') if situation_analysis else 'standard'}
        - Confidence Level: {situation_analysis.get('confidence_level', 0.5) if situation_analysis else 0.5}
        - Potential Obstacles: {situation_analysis.get('potential_obstacles', []) if situation_analysis else []}
        - Success Indicators: {situation_analysis.get('success_indicators', []) if situation_analysis else []}
        - Reasoning: {situation_analysis.get('reasoning', 'No analysis available') if situation_analysis else 'No analysis available'}
        
        Task Analysis:
        - Intent: {situation_analysis.get('task_analysis', {}).get('intent', []) if situation_analysis else []}
        - Complexity: {situation_analysis.get('task_analysis', {}).get('complexity', 'medium') if situation_analysis else 'medium'}
        
        Contextual Relevance:
        - Score: {situation_analysis.get('contextual_relevance', {}).get('relevance_score', 0.5) if situation_analysis else 0.5}
        - Relevant Elements: {situation_analysis.get('contextual_relevance', {}).get('relevant_elements', []) if situation_analysis else []}
        
        Previous actions: {self.action_history[-3:] if self.action_history else []}
        
        Based on the situation analysis and current context, what is the most appropriate action to take? Consider the page type, recommended approach, and potential obstacles.
        """
        
        try:
            # Add timeout to prevent hanging
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("OpenAI API call timed out")
            
            # Set 30 second timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)
            
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
                signal.alarm(0)  # Cancel the alarm
            except TimeoutError:
                signal.alarm(0)  # Cancel the alarm
                logger.error("OpenAI API call timed out")
                raise
            
            action_json = response.choices[0].message.content.strip()
            logger.info(f"🤖 AI suggested action")
            
            # Parse the JSON response
            import json
            action_data = json.loads(action_json)
            
            return BrowserAction(**action_data)
            
        except Exception as e:
            logger.error(f"❌ Failed to plan action: {e}")
            
            # Smart fallback based on task content
            task_lower = task.lower()
            if "navigate" in task_lower or "go to" in task_lower or "visit" in task_lower:
                # Extract URL from task
                import re
                url_match = re.search(r'https?://[^\s]+', task)
                if url_match:
                    url = url_match.group(0)
                    return BrowserAction(
                        action=ActionType.NAVIGATE,
                        parameters={"url": url},
                        description=f"Navigating to {url}"
                    )
            
            # Default fallback to screenshot
            return BrowserAction(
                action=ActionType.SCREENSHOT,
                parameters={"filename": "fallback_screenshot.png"},
                description="Taking screenshot for debugging"
            )

    def _execute_action(self, action: BrowserAction) -> ActionResult:
        try:
            logger.info(f"⚡ {action.description}")
            
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
            logger.error(f"❌ Action failed: {e}")
            return ActionResult(success=False, error=str(e))

    def _get_by_method(self, by_method: str):
        """Convert string by method to Playwright selector type."""
        # Playwright uses string selectors directly, so we just return the method
        return by_method.lower()

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

    def _is_complex_task(self, task: str) -> bool:
        """Determine if task requires multi-step planning based on Anthropic principles."""
        complex_indicators = [
            "and", "then", "after", "navigate to", "search for", "fill out",
            "login", "register", "purchase", "checkout", "multiple", "several"
        ]
        task_lower = task.lower()
        return any(indicator in task_lower for indicator in complex_indicators)

    def _execute_complex_task(self, task_description: str) -> ActionResult:
        """Execute complex multi-step tasks with transparent planning."""
        try:
            # Generate comprehensive plan with situation analysis
            context = self._get_page_context()
            situation_analysis = self._analyze_situation(task_description, context)
            
            # Log situational awareness for complex tasks
            logger.info(f"🧠 Complex task situational awareness: {situation_analysis.get('page_type', 'unknown')} page, {situation_analysis.get('recommended_approach', 'standard')} approach")
            if situation_analysis.get('potential_obstacles'):
                logger.info(f"⚠️ Complex task obstacles: {', '.join(situation_analysis['potential_obstacles'])}")
            
            plan = self._generate_multi_step_plan(task_description, context, situation_analysis)
            
            logger.info(f"📋 Generated plan with {len(plan)} steps")
            for i, step in enumerate(plan, 1):
                logger.info(f"   {i}. {step['description']}")
            
            self.current_plan = plan
            self.plan_step = 0
            
            # Execute plan step by step with situational awareness
            for step_idx, step in enumerate(plan):
                self.plan_step = step_idx
                logger.info(f"📝 Step {step_idx + 1}/{len(plan)}: {step['description']}")
                
                # Get fresh context and situation analysis for each step
                step_context = self._get_page_context()
                step_situation = self._analyze_situation(f"Step {step_idx + 1}: {step['description']}", step_context)
                
                # Log step-specific situational awareness
                if step_situation.get('potential_obstacles'):
                    logger.info(f"⚠️ Step {step_idx + 1} obstacles: {', '.join(step_situation['potential_obstacles'])}")
                
                action = BrowserAction(**step)
                result = self._execute_action(action)
                
                if not result.success:
                    logger.error(f"Step {step_idx + 1} failed: {result.error}")
                    # Try to recover or continue
                    recovery_result = self._recover_from_step_failure(step, result.error)
                    if not recovery_result.success:
                        # Try user input if recovery fails
                        user_recovery = self._ask_user_for_help(step, result.error)
                        if not user_recovery.success:
                            return ActionResult(
                                success=False, 
                                error=f"Plan failed at step {step_idx + 1}: {result.error}"
                            )
                
                self._store_action_history(f"Step {step_idx + 1}", action, result)
                
                # Small delay between steps for stability
                import time
                time.sleep(0.5)
            
            return ActionResult(success=True, data={"completed_steps": len(plan)})
            
        except Exception as e:
            logger.error(f"Complex task execution failed: {e}")
            return ActionResult(success=False, error=str(e))

    def _generate_multi_step_plan(self, task: str, context: Dict[str, Any], situation_analysis: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Generate detailed multi-step plan using OpenAI."""
        system_prompt = """
        You are an expert browser automation planner with enhanced situational awareness. Break down complex tasks into detailed steps.
        Each step should be a single, specific browser action that can be executed independently.
        
        Return a JSON array where each step has:
        - action: one of [navigate, click, type, scroll, wait, screenshot, get_text, get_attribute, execute_script]
        - parameters: dict with action-specific parameters
        - description: clear explanation of what this step accomplishes
        
        SITUATIONAL PLANNING GUIDELINES:
        - Use the situation analysis to understand the current page type and recommended approach
        - Consider potential obstacles when planning steps
        - For login flows, include proper field identification and validation steps
        - For search flows, include search input and result handling
        - For form submissions, include validation and confirmation steps
        - For navigation flows, include proper wait times and error handling
        - Include wait steps where needed for page loading and stability
        
        Make steps granular and consider the current page context when planning.
        """
        
        user_prompt = f"""
        Task: {task}
        
        Current context:
        - URL: {context.get('current_url', 'unknown')}
        - Title: {context.get('page_title', 'unknown')}
        - Interactive elements: {len(context.get('interactive_elements', []))}
        
        Situation Analysis:
        - Page Type: {situation_analysis.get('page_type', 'unknown') if situation_analysis else 'unknown'}
        - Recommended Approach: {situation_analysis.get('recommended_approach', 'standard') if situation_analysis else 'standard'}
        - Potential Obstacles: {situation_analysis.get('potential_obstacles', []) if situation_analysis else []}
        - Success Indicators: {situation_analysis.get('success_indicators', []) if situation_analysis else []}
        - Confidence Level: {situation_analysis.get('confidence_level', 0.5) if situation_analysis else 0.5}
        
        Task Analysis:
        - Intent: {situation_analysis.get('task_analysis', {}).get('intent', []) if situation_analysis else []}
        - Complexity: {situation_analysis.get('task_analysis', {}).get('complexity', 'medium') if situation_analysis else 'medium'}
        
        Generate a detailed step-by-step plan to complete this task, considering the situation analysis and potential obstacles.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            import json
            plan_data = json.loads(response.choices[0].message.content.strip())
            return plan_data
            
        except Exception as e:
            logger.error(f"Failed to generate multi-step plan: {e}")
            # Fallback to simple plan
            return [{
                "action": "screenshot",
                "parameters": {"filename": "planning_fallback.png"},
                "description": "Taking screenshot for manual analysis"
            }]

    def _recover_from_error(self, task: str, error: str) -> ActionResult:
        """Implement error recovery based on Anthropic principles."""
        logger.info(f"Attempting error recovery for task: {task}")
        
        try:
            # Take screenshot for debugging
            screenshot_result = self._execute_action(BrowserAction(
                action=ActionType.SCREENSHOT,
                parameters={"filename": f"error_recovery_{int(__import__('time').time())}.png"},
                description="Error recovery screenshot"
            ))
            
            # If it's an element not found error, try to debug the element selection
            if "Element not found" in error or "Timeout" in error:
                logger.info("🔍 Debugging element selection issue...")
                debug_info = self.debug_element_selection(task)
                logger.info(f"📊 Found {len(debug_info.get('available_elements', []))} interactive elements")
                
                # Try to find a similar element based on the task description
                task_lower = task.lower()
                available_elements = debug_info.get('available_elements', [])
                
                for element in available_elements:
                    element_text = element.get('text', '').lower()
                    element_tag = element.get('tag', '').lower()
                    
                    # Check if this element might be what we're looking for
                    if any(keyword in element_text for keyword in task_lower.split()):
                        selectors = element.get('selectors', [])
                        if selectors:
                            best_selector = selectors[0]  # Use the first (best) selector
                            logger.info(f"🔄 Trying alternative element: {best_selector}")
                            
                            try:
                                # Try to click this alternative element
                                if element_tag in ['button', 'a'] or element.get('is_clickable'):
                                    self.driver.click_element('css', best_selector)
                                    logger.info(f"✅ Successfully clicked alternative element: {best_selector}")
                                    return ActionResult(success=True, data={"recovered_with": best_selector})
                            except Exception as alt_error:
                                logger.warning(f"Alternative element click failed: {alt_error}")
                                continue
            
            # Simple recovery strategies
            recovery_actions = [
                # Wait and retry
                {"action": "wait", "parameters": {"seconds": 2}, "description": "Wait for page to stabilize"},
                # Refresh page if navigation error
                {"action": "execute_script", "parameters": {"script": "location.reload();"}, "description": "Refresh page"}
            ]
            
            for recovery_action in recovery_actions:
                try:
                    action = BrowserAction(**recovery_action)
                    result = self._execute_action(action)
                    if result.success:
                        logger.info(f"Recovery action succeeded: {recovery_action['description']}")
                        break
                except Exception as recovery_error:
                    logger.warning(f"Recovery action failed: {recovery_error}")
                    continue
            
            return ActionResult(
                success=False, 
                error=f"Original error: {error}. Recovery attempted.",
                screenshot_path=screenshot_result.screenshot_path if screenshot_result.success else None
            )
            
        except Exception as recovery_exception:
            logger.error(f"Error recovery failed: {recovery_exception}")
            return ActionResult(success=False, error=f"Original: {error}, Recovery: {recovery_exception}")

    def _recover_from_step_failure(self, step: Dict[str, Any], error: str) -> ActionResult:
        """Recover from individual step failures in multi-step plans."""
        logger.info(f"Attempting step recovery: {step['description']}")
        
        try:
            # Wait and retry the same step once
            import time
            time.sleep(1)
            
            action = BrowserAction(**step)
            return self._execute_action(action)
            
        except Exception as e:
            logger.error(f"Step recovery failed: {e}")
            return ActionResult(success=False, error=str(e))

    def get_current_plan_status(self) -> Dict[str, Any]:
        """Get current plan execution status for transparency."""
        if not self.current_plan:
            return {"has_plan": False}
        
        return {
            "has_plan": True,
            "total_steps": len(self.current_plan),
            "current_step": self.plan_step + 1,
            "progress_percentage": round((self.plan_step + 1) / len(self.current_plan) * 100, 1),
            "current_step_description": self.current_plan[self.plan_step]["description"] if self.plan_step < len(self.current_plan) else "Plan completed",
            "remaining_steps": len(self.current_plan) - self.plan_step - 1
        }

    def evaluate_task_completion(self, original_task: str) -> Dict[str, Any]:
        """Evaluate if the original task was successfully completed."""
        try:
            context = self._get_page_context()
            
            evaluation_prompt = f"""
            Original task: {original_task}
            
            Current page state:
            - URL: {context.get('current_url')}
            - Title: {context.get('page_title')}
            - Page info: {context.get('page_info', {})}
            
            Action history: {self.action_history[-5:] if self.action_history else []}
            
            Based on the current page state and action history, evaluate:
            1. Was the original task completed successfully? (true/false)
            2. What evidence supports this conclusion?
            3. What additional steps might be needed?
            
            Respond in JSON format:
            {{"completed": true/false, "evidence": "description", "next_steps": ["step1", "step2"]}}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": evaluation_prompt}],
                temperature=0.1,
                max_tokens=300
            )
            
            import json
            evaluation = json.loads(response.choices[0].message.content.strip())
            return evaluation
            
        except Exception as e:
            logger.error(f"Task evaluation failed: {e}")
            return {"completed": False, "evidence": "Evaluation failed", "next_steps": []}

    def _ask_user_for_help(self, failed_step: Dict[str, Any], error: str) -> ActionResult:
        """Ask user for help when agent gets blocked."""
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.text import Text
            
            console = Console()
            
            # Take a screenshot to show current state
            screenshot_result = self.take_screenshot("blocked_state.png")
            
            console.print(Panel.fit(
                Text("🚫 Agent Blocked - Need Your Help", style="bold red"),
                border_style="red"
            ))
            
            console.print(f"[yellow]Failed step:[/yellow] {failed_step.get('description', 'Unknown step')}")
            console.print(f"[yellow]Error:[/yellow] {error}")
            console.print(f"[yellow]Current URL:[/yellow] {self.driver.get_current_url()}")
            
            if screenshot_result:
                console.print(f"[cyan]Screenshot saved:[/cyan] screenshots/blocked_state.png")
            
            console.print("\n[bold blue]What would you like me to do?[/bold blue]")
            console.print("[dim]Options:[/dim]")
            console.print("[dim]  1. 'skip' - Skip this step and continue[/dim]")
            console.print("[dim]  2. 'retry' - Retry the same step[/dim]") 
            console.print("[dim]  3. 'abort' - Stop the task[/dim]")
            console.print("[dim]  4. Type a new instruction to try instead[/dim]")
            
            user_input = console.input("\n[bold green]Your choice:[/bold green] ").strip().lower()
            
            if user_input == 'skip':
                logger.info("User chose to skip failed step")
                return ActionResult(success=True, data="User skipped step")
            elif user_input == 'retry':
                logger.info("User chose to retry failed step")
                # Retry the same action
                action = BrowserAction(**failed_step)
                return self._execute_action(action)
            elif user_input == 'abort':  
                logger.info("User chose to abort task")
                return ActionResult(success=False, error="User aborted task")
            else:
                # User provided new instruction
                logger.info(f"User provided new instruction: {user_input}")
                console.print(f"[green]Trying:[/green] {user_input}")
                
                # Execute the user's instruction as a new task
                return self.execute_task(user_input)
                
        except Exception as e:
            logger.error(f"Error asking user for help: {e}")
            return ActionResult(success=False, error=f"User input failed: {e}")

    def debug_element_selection(self, task_description: str) -> Dict[str, Any]:
        """Debug element selection issues by providing detailed information about available elements."""
        try:
            context = self._get_page_context()
            
            # Get detailed element information
            debug_script = """
            const elements = document.querySelectorAll('*');
            const interactive = [];
            
            for (let el of elements) {
                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);
                
                // Only include elements that are potentially interactive
                if (el.tagName.match(/^(A|BUTTON|INPUT|SELECT|TEXTAREA)$/i) || 
                    el.getAttribute('role') === 'button' || 
                    el.getAttribute('tabindex') || 
                    el.onclick || 
                    el.addEventListener) {
                    
                    if (rect.width > 0 && rect.height > 0 && 
                        style.visibility !== 'hidden' && 
                        style.display !== 'none') {
                        
                        // Get all relevant attributes
                        const attributes = {};
                        for (let attr of el.attributes) {
                            attributes[attr.name] = attr.value;
                        }
                        
                        // Get element text
                        let text = '';
                        if (el.tagName === 'INPUT') {
                            text = el.value || el.placeholder || '';
                        } else {
                            text = el.textContent || el.innerText || '';
                        }
                        
                        // Generate possible selectors
                        const selectors = [];
                        if (el.id) selectors.push(`${el.tagName.toLowerCase()}#${el.id}`);
                        if (el.name) selectors.push(`${el.tagName.toLowerCase()}[name='${el.name}']`);
                        if (text.trim()) selectors.push(`${el.tagName.toLowerCase()}:has-text('${text.trim().substring(0, 20)}')`);
                        if (el.className) {
                            const classes = el.className.split(' ').filter(c => c.trim());
                            if (classes.length > 0) {
                                selectors.push(`${el.tagName.toLowerCase()}.${classes[0]}`);
                            }
                        }
                        
                        interactive.push({
                            tag: el.tagName.toLowerCase(),
                            text: text.substring(0, 100).trim(),
                            attributes: attributes,
                            selectors: selectors,
                            position: { x: rect.left, y: rect.top, width: rect.width, height: rect.height },
                            is_clickable: !!(el.onclick || el.getAttribute('onclick') || el.getAttribute('role') === 'button')
                        });
                    }
                }
            }
            
            return interactive.slice(0, 20);
            """
            
            elements = self.driver.execute_script(debug_script)
            
            # Take a screenshot for visual reference
            screenshot_filename = f"debug_elements_{int(time.time())}.png"
            self.take_screenshot(screenshot_filename)
            
            return {
                "task": task_description,
                "current_url": context.get("current_url"),
                "page_title": context.get("page_title"),
                "available_elements": elements,
                "screenshot": screenshot_filename,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Failed to debug element selection: {e}")
            return {"error": str(e)}

    def list_available_elements(self) -> Dict[str, Any]:
        """List all available interactive elements on the current page for manual reference."""
        try:
            context = self._get_page_context()
            interactive_elements = context.get('interactive_elements', [])
            
            # Format elements for easy reading
            formatted_elements = []
            for i, elem in enumerate(interactive_elements, 1):
                formatted_elem = {
                    "index": i,
                    "tag": elem.get('tag', ''),
                    "text": elem.get('text', ''),
                    "id": elem.get('id', ''),
                    "name": elem.get('name', ''),
                    "type": elem.get('type', ''),
                    "best_selector": elem.get('best_selector', ''),
                    "position": elem.get('position', {}),
                    "attributes": elem.get('attributes', {})
                }
                formatted_elements.append(formatted_elem)
            
            return {
                "current_url": context.get("current_url"),
                "page_title": context.get("page_title"),
                "total_elements": len(formatted_elements),
                "elements": formatted_elements
            }
            
        except Exception as e:
            logger.error(f"Failed to list available elements: {e}")
            return {"error": str(e)}

    def _analyze_situation(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the current page situation and user request to provide better contextual awareness.
        This helps the agent understand what's currently happening and what the user wants to achieve.
        """
        try:
            logger.info("🔍 Analyzing current situation...")
            
            # Enhanced page analysis
            analysis = {
                "task_analysis": self._analyze_task_intent(task),
                "page_analysis": self._analyze_page_state(context),
                "contextual_relevance": self._analyze_contextual_relevance(task, context),
                "recommended_approach": None,
                "potential_obstacles": [],
                "success_indicators": []
            }
            
            # Generate AI-powered situation analysis
            ai_analysis = self._generate_ai_situation_analysis(task, context, analysis)
            analysis.update(ai_analysis)
            
            logger.info(f"📊 Situation analysis complete - Page type: {analysis.get('page_type', 'unknown')}")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze situation: {e}")
            return {
                "task_analysis": {"intent": "unknown", "complexity": "medium"},
                "page_analysis": {"type": "unknown", "state": "unknown"},
                "contextual_relevance": {"relevance_score": 0.5},
                "recommended_approach": "standard",
                "potential_obstacles": [],
                "success_indicators": []
            }

    def _analyze_task_intent(self, task: str) -> Dict[str, Any]:
        """Analyze the user's task to understand intent and complexity."""
        task_lower = task.lower()
        
        # Intent classification
        intents = {
            "navigation": any(word in task_lower for word in ["go to", "navigate", "visit", "open", "browse"]),
            "interaction": any(word in task_lower for word in ["click", "press", "tap", "select", "choose"]),
            "input": any(word in task_lower for word in ["type", "enter", "fill", "write", "input"]),
            "search": any(word in task_lower for word in ["search", "find", "look for", "locate"]),
            "extraction": any(word in task_lower for word in ["get", "extract", "read", "copy", "save"]),
            "verification": any(word in task_lower for word in ["check", "verify", "confirm", "test"]),
            "multi_step": any(word in task_lower for word in ["and", "then", "after", "next", "finally"])
        }
        
        # Complexity assessment
        complexity = "simple"
        if intents["multi_step"] or len(task.split()) > 10:
            complexity = "complex"
        elif len(task.split()) > 5:
            complexity = "medium"
        
        return {
            "intent": [k for k, v in intents.items() if v],
            "complexity": complexity,
            "word_count": len(task.split()),
            "has_url": "http" in task_lower,
            "has_specific_element": any(word in task_lower for word in ["button", "link", "form", "input", "field"])
        }

    def _analyze_page_state(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the current page state and type."""
        page_info = context.get("page_info", {})
        interactive_elements = context.get("interactive_elements", [])
        current_url = context.get("current_url", "")
        page_title = context.get("page_title", "")
        
        # Page type classification
        page_type = "general"
        if page_info.get("has_login"):
            page_type = "login"
        elif page_info.get("has_search"):
            page_type = "search"
        elif "form" in page_title.lower() or page_info.get("forms", 0) > 0:
            page_type = "form"
        elif any("checkout" in elem.get("text", "").lower() for elem in interactive_elements):
            page_type = "checkout"
        elif any("cart" in elem.get("text", "").lower() for elem in interactive_elements):
            page_type = "shopping"
        
        # Page state assessment
        state = "ready"
        if not page_info.get("page_ready", True):
            state = "loading"
        elif len(interactive_elements) == 0:
            state = "empty"
        
        # Interactive element analysis
        element_types = {}
        for elem in interactive_elements:
            elem_type = elem.get("tag", "unknown")
            element_types[elem_type] = element_types.get(elem_type, 0) + 1
        
        return {
            "type": page_type,
            "state": state,
            "interactive_elements_count": len(interactive_elements),
            "element_types": element_types,
            "has_forms": page_info.get("forms", 0) > 0,
            "has_links": page_info.get("links", 0) > 0,
            "has_images": page_info.get("images", 0) > 0,
            "url_domain": self._extract_domain(current_url)
        }

    def _analyze_contextual_relevance(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how relevant the current page context is to the user's task."""
        task_lower = task.lower()
        interactive_elements = context.get("interactive_elements", [])
        page_title = context.get("page_title", "").lower()
        
        # Calculate relevance score based on element matching
        relevant_elements = []
        for elem in interactive_elements:
            elem_text = elem.get("text", "").lower()
            elem_tag = elem.get("tag", "").lower()
            
            # Check if element text matches task keywords
            task_words = set(task_lower.split())
            elem_words = set(elem_text.split())
            if task_words & elem_words:  # Intersection
                relevant_elements.append(elem)
        
        relevance_score = min(1.0, len(relevant_elements) / max(1, len(interactive_elements)))
        
        return {
            "relevance_score": relevance_score,
            "relevant_elements_count": len(relevant_elements),
            "relevant_elements": relevant_elements[:5],  # Top 5 most relevant
            "page_title_relevance": any(word in page_title for word in task_lower.split() if len(word) > 3)
        }

    def _generate_ai_situation_analysis(self, task: str, context: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to generate intelligent situation analysis and recommendations."""
        try:
            system_prompt = """
            You are an expert browser automation analyst. Analyze the current situation and provide intelligent recommendations.
            
            Return a JSON object with:
            - page_type: "login", "search", "form", "checkout", "shopping", "general", "error"
            - recommended_approach: "direct", "exploratory", "cautious", "aggressive"
            - potential_obstacles: array of potential issues
            - success_indicators: array of what would indicate success
            - confidence_level: 0.0 to 1.0
            - reasoning: brief explanation of the analysis
            """
            
            user_prompt = f"""
            Task: {task}
            
            Page Context:
            - URL: {context.get('current_url', 'unknown')}
            - Title: {context.get('page_title', 'unknown')}
            - Page Type: {analysis['page_analysis']['type']}
            - Interactive Elements: {len(context.get('interactive_elements', []))}
            - Element Types: {analysis['page_analysis']['element_types']}
            
            Task Analysis:
            - Intent: {analysis['task_analysis']['intent']}
            - Complexity: {analysis['task_analysis']['complexity']}
            
            Contextual Relevance:
            - Score: {analysis['contextual_relevance']['relevance_score']}
            - Relevant Elements: {len(analysis['contextual_relevance']['relevant_elements'])}
            
            Previous Actions: {self.action_history[-2:] if self.action_history else []}
            
            Provide intelligent analysis and recommendations for this situation.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=400
            )
            
            import json
            ai_analysis = json.loads(response.choices[0].message.content.strip())
            return ai_analysis
            
        except Exception as e:
            logger.warning(f"AI situation analysis failed: {e}")
            return {
                "page_type": analysis['page_analysis']['type'],
                "recommended_approach": "standard",
                "potential_obstacles": [],
                "success_indicators": [],
                "confidence_level": 0.5,
                "reasoning": "Analysis failed, using fallback"
            }

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL for context analysis."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return "unknown"

    def get_current_situation_analysis(self, task: str = None) -> Dict[str, Any]:
        """
        Get the current situational analysis for the given task or current page.
        Useful for debugging and monitoring the agent's awareness.
        """
        try:
            context = self._get_page_context()
            if task:
                return self._analyze_situation(task, context)
            else:
                # Analyze current page without specific task
                return {
                    "page_analysis": self._analyze_page_state(context),
                    "contextual_relevance": {"relevance_score": 0.5, "relevant_elements": []},
                    "recommended_approach": "standard",
                    "potential_obstacles": [],
                    "success_indicators": []
                }
        except Exception as e:
            logger.error(f"Failed to get current situation analysis: {e}")
            return {"error": str(e)}