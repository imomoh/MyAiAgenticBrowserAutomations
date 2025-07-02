import pytest
from unittest.mock import patch
from src.agent.browser_agent import BrowserAgent


@pytest.mark.integration
class TestFullWorkflow:
    """Integration tests that test the full workflow with mocked external dependencies"""
    
    @patch('src.agent.browser_agent.openai.OpenAI')
    @patch('src.browser.chrome_driver.ChromeDriverManager')  
    @patch('src.browser.chrome_driver.webdriver.Chrome')
    def test_agent_lifecycle(self, mock_chrome, mock_driver_manager, mock_openai):
        """Test agent start, task execution, and stop"""
        
        # Setup mocks
        mock_driver = mock_chrome.return_value
        mock_driver.current_url = "https://example.com"
        mock_driver.execute_script.side_effect = [
            "Example Page",  # page title
            {"width": 1920, "height": 1080},  # viewport
            []  # visible elements
        ]
        
        mock_client = mock_openai.return_value
        mock_response = type('MockResponse', (), {
            'choices': [type('MockChoice', (), {
                'message': type('MockMessage', (), {
                    'content': '{"action": "screenshot", "parameters": {"filename": "test.png"}, "description": "Take a screenshot"}'
                })()
            })()]
        })()
        mock_client.chat.completions.create.return_value = mock_response
        
        mock_driver_manager.return_value.install.return_value = "/fake/path"
        mock_driver.save_screenshot.return_value = True
        
        # Test the workflow
        with BrowserAgent() as agent:
            result = agent.execute_task("take a screenshot")
            
            assert result.success
            assert result.data is not None
            assert len(agent.get_action_history()) == 1
        
        # Verify driver was started and stopped
        mock_chrome.assert_called_once()
        mock_driver.quit.assert_called_once()
    
    @patch('src.agent.browser_agent.openai.OpenAI')
    @patch('src.browser.chrome_driver.ChromeDriverManager')
    @patch('src.browser.chrome_driver.webdriver.Chrome')  
    def test_navigation_workflow(self, mock_chrome, mock_driver_manager, mock_openai):
        """Test navigation task workflow"""
        
        # Setup mocks
        mock_driver = mock_chrome.return_value
        mock_driver.current_url = "https://google.com"
        mock_driver.execute_script.side_effect = [
            "Google",
            {"width": 1920, "height": 1080},
            []
        ]
        
        mock_client = mock_openai.return_value
        mock_response = type('MockResponse', (), {
            'choices': [type('MockChoice', (), {
                'message': type('MockMessage', (), {
                    'content': '{"action": "navigate", "parameters": {"url": "https://google.com"}, "description": "Navigate to Google"}'
                })()
            })()]
        })()
        mock_client.chat.completions.create.return_value = mock_response
        
        mock_driver_manager.return_value.install.return_value = "/fake/path"
        
        with BrowserAgent() as agent:
            result = agent.execute_task("go to google.com")
            
            assert result.success
            mock_driver.get.assert_called_with("https://google.com")
    
    @patch('src.agent.browser_agent.openai.OpenAI')
    @patch('src.browser.chrome_driver.ChromeDriverManager')
    @patch('src.browser.chrome_driver.webdriver.Chrome')
    def test_error_handling_workflow(self, mock_chrome, mock_driver_manager, mock_openai):
        """Test error handling in workflow"""
        
        # Setup mocks to simulate failure
        mock_driver = mock_chrome.return_value
        mock_driver.get.side_effect = Exception("Navigation failed")
        mock_driver.current_url = "https://example.com"
        mock_driver.execute_script.side_effect = [
            "Example",
            {"width": 1920, "height": 1080},
            []
        ]
        
        mock_client = mock_openai.return_value
        mock_response = type('MockResponse', (), {
            'choices': [type('MockChoice', (), {
                'message': type('MockMessage', (), {
                    'content': '{"action": "navigate", "parameters": {"url": "https://invalid.com"}, "description": "Navigate to invalid site"}'
                })()
            })()]
        })()
        mock_client.chat.completions.create.return_value = mock_response
        
        mock_driver_manager.return_value.install.return_value = "/fake/path"
        
        with BrowserAgent() as agent:
            result = agent.execute_task("navigate to invalid site")
            
            assert not result.success
            assert "Navigation failed" in result.error
    
    @patch('src.agent.browser_agent.openai.OpenAI')
    @patch('src.browser.chrome_driver.ChromeDriverManager')
    @patch('src.browser.chrome_driver.webdriver.Chrome')
    def test_multiple_actions_workflow(self, mock_chrome, mock_driver_manager, mock_openai):
        """Test multiple sequential actions"""
        
        mock_driver = mock_chrome.return_value
        mock_driver.current_url = "https://example.com"
        mock_driver.execute_script.side_effect = [
            "Example",
            {"width": 1920, "height": 1080},
            [],
            "Example",
            {"width": 1920, "height": 1080},
            []
        ]
        
        mock_client = mock_openai.return_value
        mock_responses = [
            type('MockResponse', (), {
                'choices': [type('MockChoice', (), {
                    'message': type('MockMessage', (), {
                        'content': '{"action": "navigate", "parameters": {"url": "https://example.com"}, "description": "Navigate to example"}'
                    })()
                })()]
            })(),
            type('MockResponse', (), {
                'choices': [type('MockChoice', (), {
                    'message': type('MockMessage', (), {
                        'content': '{"action": "screenshot", "parameters": {"filename": "after_nav.png"}, "description": "Take screenshot after navigation"}'
                    })()
                })()]
            })()
        ]
        mock_client.chat.completions.create.side_effect = mock_responses
        
        mock_driver_manager.return_value.install.return_value = "/fake/path"
        mock_driver.save_screenshot.return_value = True
        
        with BrowserAgent() as agent:
            # Execute multiple tasks
            result1 = agent.execute_task("navigate to example.com")
            result2 = agent.execute_task("take a screenshot")
            
            assert result1.success
            assert result2.success
            assert len(agent.get_action_history()) == 2