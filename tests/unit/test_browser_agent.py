import pytest
from unittest.mock import Mock, patch, MagicMock
from src.agent.browser_agent import BrowserAgent, ActionType, BrowserAction, ActionResult
from src.utils.exceptions import AgentError


@pytest.fixture
def mock_driver():
    with patch('src.agent.browser_agent.ChromeDriver') as mock:
        driver = Mock()
        mock.return_value = driver
        yield driver


@pytest.fixture  
def mock_openai():
    with patch('src.agent.browser_agent.openai.OpenAI') as mock:
        client = Mock()
        mock.return_value = client
        yield client


@pytest.fixture
def browser_agent(mock_driver, mock_openai):
    agent = BrowserAgent()
    return agent


class TestBrowserAgent:
    def test_init(self, browser_agent):
        assert browser_agent.driver is not None  
        assert browser_agent.client is not None
        assert browser_agent.action_history == []

    def test_start_success(self, browser_agent, mock_driver):
        browser_agent.start()
        mock_driver.start.assert_called_once()

    def test_start_failure(self, browser_agent, mock_driver):
        mock_driver.start.side_effect = Exception("Driver failed")
        
        with pytest.raises(AgentError):
            browser_agent.start() 

    def test_stop(self, browser_agent, mock_driver):
        browser_agent.stop()
        mock_driver.stop.assert_called_once()

    def test_get_page_context_success(self, browser_agent, mock_driver):
        mock_driver.get_current_url.return_value = "https://example.com"
        mock_driver.execute_script.side_effect = [
            "Example Title",
            {"width": 1920, "height": 1080},
            []
        ]
        
        context = browser_agent._get_page_context()
        
        assert context["current_url"] == "https://example.com"
        assert context["page_title"] == "Example Title"
        assert "viewport_info" in context
        assert "visible_elements" in context

    def test_execute_action_navigate(self, browser_agent, mock_driver):
        action = BrowserAction(
            action=ActionType.NAVIGATE,
            parameters={"url": "https://example.com"},
            description="Navigate to example.com"
        )
        
        result = browser_agent._execute_action(action)
        
        assert result.success is True
        assert result.data == {"url": "https://example.com"}
        mock_driver.navigate_to.assert_called_once_with("https://example.com")

    def test_execute_action_click(self, browser_agent, mock_driver):
        action = BrowserAction(
            action=ActionType.CLICK,
            parameters={"selector": "button#submit", "by": "css"},
            description="Click submit button"
        )
        
        with patch.object(browser_agent, '_get_by_method') as mock_by:
            mock_by.return_value = "css_selector"
            
            result = browser_agent._execute_action(action)
            
            assert result.success is True
            assert result.data == {"clicked": "button#submit"}
            mock_driver.click_element.assert_called_once_with("css_selector", "button#submit")

    def test_execute_action_type(self, browser_agent, mock_driver):
        action = BrowserAction(
            action=ActionType.TYPE,
            parameters={"selector": "input[name='username']", "text": "testuser", "by": "css"},
            description="Type username"
        )
        
        with patch.object(browser_agent, '_get_by_method') as mock_by:
            mock_by.return_value = "css_selector"
            
            result = browser_agent._execute_action(action)
            
            assert result.success is True
            assert result.data == {"typed": "testuser", "into": "input[name='username']"}
            mock_driver.send_keys.assert_called_once_with("css_selector", "input[name='username']", "testuser")

    def test_execute_action_screenshot(self, browser_agent, mock_driver):
        action = BrowserAction(
            action=ActionType.SCREENSHOT,
            parameters={"filename": "test.png"},
            description="Take screenshot"
        )
        
        mock_driver.take_screenshot.return_value = True
        
        result = browser_agent._execute_action(action)
        
        assert result.success is True
        assert result.data == {"filename": "test.png"}
        assert result.screenshot_path == "test.png"
        mock_driver.take_screenshot.assert_called_once_with("test.png")

    def test_execute_action_failure(self, browser_agent, mock_driver):
        action = BrowserAction(
            action=ActionType.NAVIGATE,
            parameters={"url": "https://example.com"},
            description="Navigate to example.com"
        )
        
        mock_driver.navigate_to.side_effect = Exception("Navigation failed")
        
        result = browser_agent._execute_action(action)
        
        assert result.success is False
        assert "Navigation failed" in result.error

    def test_get_by_method(self, browser_agent):
        from selenium.webdriver.common.by import By
        
        assert browser_agent._get_by_method("css") == By.CSS_SELECTOR
        assert browser_agent._get_by_method("xpath") == By.XPATH
        assert browser_agent._get_by_method("id") == By.ID
        assert browser_agent._get_by_method("name") == By.NAME
        assert browser_agent._get_by_method("invalid") == By.CSS_SELECTOR  # default

    def test_store_action_history(self, browser_agent):
        task = "Test task"
        action = BrowserAction(
            action=ActionType.NAVIGATE,
            parameters={"url": "https://example.com"},
            description="Test action"
        )
        result = ActionResult(success=True, data={"test": "data"})
        
        browser_agent._store_action_history(task, action, result)
        
        assert len(browser_agent.action_history) == 1
        history_item = browser_agent.action_history[0]
        assert history_item["task"] == task
        assert history_item["action"] == action.dict()
        assert history_item["result"] == result.dict()
        assert "timestamp" in history_item

    def test_action_history_limit(self, browser_agent):
        # Add more than 10 actions
        for i in range(15):
            task = f"Task {i}"
            action = BrowserAction(
                action=ActionType.NAVIGATE,
                parameters={"url": f"https://example{i}.com"},
                description=f"Action {i}"
            )
            result = ActionResult(success=True)
            browser_agent._store_action_history(task, action, result)
        
        # Should only keep last 10
        assert len(browser_agent.action_history) == 10
        assert browser_agent.action_history[0]["task"] == "Task 5"
        assert browser_agent.action_history[-1]["task"] == "Task 14"

    def test_context_manager(self, mock_driver):
        with patch('src.agent.browser_agent.openai.OpenAI'):
            with BrowserAgent() as agent:
                assert agent is not None
        mock_driver.start.assert_called_once()
        mock_driver.stop.assert_called_once()