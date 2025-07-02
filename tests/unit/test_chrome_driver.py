import pytest
from unittest.mock import Mock, patch, MagicMock
from src.browser.chrome_driver import ChromeDriver


@pytest.fixture
def mock_playwright():
    with patch('src.browser.chrome_driver.sync_playwright') as mock:
        playwright_instance = Mock()
        browser = Mock()
        context = Mock()
        page = Mock()
        
        # Set up the chain
        playwright_instance.chromium.launch.return_value = browser
        browser.new_context.return_value = context
        context.new_page.return_value = page
        
        mock.return_value.start.return_value = playwright_instance
        yield {
            'playwright': playwright_instance,
            'browser': browser,
            'context': context,
            'page': page
        }


@pytest.fixture
def chrome_driver():
    return ChromeDriver()


class TestChromeDriver:
    def test_init(self, chrome_driver):
        assert chrome_driver.playwright is None
        assert chrome_driver.browser is None
        assert chrome_driver.context is None
        assert chrome_driver.page is None

    def test_start_success(self, chrome_driver, mock_playwright):
        chrome_driver.start()
        
        assert chrome_driver.playwright is not None
        assert chrome_driver.browser == mock_playwright['browser']
        assert chrome_driver.context == mock_playwright['context']
        assert chrome_driver.page == mock_playwright['page']

    def test_start_failure(self, chrome_driver):
        with patch('src.browser.chrome_driver.sync_playwright') as mock_playwright:
            mock_playwright.return_value.start.side_effect = Exception("Playwright failed to start")
            
            with pytest.raises(Exception):
                chrome_driver.start()

    def test_stop_success(self, chrome_driver):
        # Set up mock objects
        mock_playwright = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        chrome_driver.playwright = mock_playwright
        chrome_driver.browser = mock_browser
        chrome_driver.context = mock_context
        chrome_driver.page = mock_page
        
        chrome_driver.stop()
        
        mock_page.close.assert_called_once()
        mock_context.close.assert_called_once()
        mock_browser.close.assert_called_once()
        mock_playwright.stop.assert_called_once()
        
        assert chrome_driver.page is None
        assert chrome_driver.context is None
        assert chrome_driver.browser is None
        assert chrome_driver.playwright is None

    def test_stop_with_error(self, chrome_driver):
        mock_playwright = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        mock_page = Mock()
        mock_page.close.side_effect = Exception("Close failed")
        
        chrome_driver.playwright = mock_playwright
        chrome_driver.browser = mock_browser
        chrome_driver.context = mock_context
        chrome_driver.page = mock_page
        
        chrome_driver.stop()  # Should not raise exception
        
        assert chrome_driver.page is None
        assert chrome_driver.context is None
        assert chrome_driver.browser is None
        assert chrome_driver.playwright is None

    def test_navigate_to_success(self, chrome_driver):
        mock_page = Mock()
        chrome_driver.page = mock_page
        url = "https://example.com"
        
        chrome_driver.navigate_to(url)
        
        mock_page.goto.assert_called_once_with(url)

    def test_navigate_to_no_page(self, chrome_driver):
        with pytest.raises(RuntimeError, match="Page not started"):
            chrome_driver.navigate_to("https://example.com")

    def test_find_element_success(self, chrome_driver):
        mock_page = Mock()
        mock_element = Mock()
        chrome_driver.page = mock_page
        mock_page.wait_for_selector.return_value = mock_element
        
        result = chrome_driver.find_element("id", "test-id")
        
        assert result == mock_element
        mock_page.wait_for_selector.assert_called_once_with("#test-id", timeout=30000)

    def test_find_element_no_page(self, chrome_driver):
        with pytest.raises(RuntimeError, match="Page not started"):
            chrome_driver.find_element("id", "test-id")

    def test_click_element_success(self, chrome_driver):
        mock_element = Mock()
        
        with patch.object(chrome_driver, 'find_element', return_value=mock_element):
            chrome_driver.click_element("id", "test-id")
            
            mock_element.click.assert_called_once()

    def test_send_keys_success(self, chrome_driver):
        mock_element = Mock()
        
        with patch.object(chrome_driver, 'find_element', return_value=mock_element):
            chrome_driver.send_keys("id", "test-id", "test text")
            
            mock_element.fill.assert_called_once_with("test text")

    def test_get_text_success(self, chrome_driver):
        mock_element = Mock()
        mock_element.text_content.return_value = "Element text"
        
        with patch.object(chrome_driver, 'find_element', return_value=mock_element):
            text = chrome_driver.get_text("id", "test-id")
            
            assert text == "Element text"

    def test_get_attribute_success(self, chrome_driver):
        mock_element = Mock()
        mock_element.get_attribute.return_value = "attribute value"
        
        with patch.object(chrome_driver, 'find_element', return_value=mock_element):
            value = chrome_driver.get_attribute("id", "test-id", "href")
            
            assert value == "attribute value"
            mock_element.get_attribute.assert_called_once_with("href")

    def test_get_attribute_none_result(self, chrome_driver):
        mock_element = Mock()
        mock_element.get_attribute.return_value = None
        
        with patch.object(chrome_driver, 'find_element', return_value=mock_element):
            value = chrome_driver.get_attribute("id", "test-id", "href")
            
            assert value == ""

    def test_execute_script_success(self, chrome_driver):
        mock_page = Mock()
        chrome_driver.page = mock_page
        mock_page.evaluate.return_value = "script result"
        
        result = chrome_driver.execute_script("return 'test';")
        
        assert result == "script result"
        mock_page.evaluate.assert_called_once_with("return 'test';")

    def test_execute_script_no_page(self, chrome_driver):
        with pytest.raises(RuntimeError, match="Page not started"):
            chrome_driver.execute_script("return 'test';")

    @patch('src.browser.chrome_driver.Path')
    def test_take_screenshot_success(self, mock_path, chrome_driver):
        mock_page = Mock()
        chrome_driver.page = mock_page
        
        # Mock the Path constructor and division operation
        mock_screenshots_dir = Mock()
        mock_screenshots_dir.parent.mkdir = Mock()
        mock_screenshots_dir.__str__ = Mock(return_value="/fake/path/screenshots/test.png")
        
        # Mock the Path division operation
        mock_path.return_value.__truediv__ = Mock(return_value=mock_screenshots_dir)
        
        result = chrome_driver.take_screenshot("test.png")
        
        assert result is True
        mock_page.screenshot.assert_called_once_with(path="/fake/path/screenshots/test.png")
        mock_screenshots_dir.parent.mkdir.assert_called_once_with(exist_ok=True)

    def test_take_screenshot_no_page(self, chrome_driver):
        with pytest.raises(RuntimeError, match="Page not started"):
            chrome_driver.take_screenshot("test.png")

    def test_get_page_source_success(self, chrome_driver):
        mock_page = Mock()
        chrome_driver.page = mock_page
        mock_page.content.return_value = "<html>test</html>"
        
        source = chrome_driver.get_page_source()
        
        assert source == "<html>test</html>"

    def test_get_page_source_no_page(self, chrome_driver):
        with pytest.raises(RuntimeError, match="Page not started"):
            chrome_driver.get_page_source()

    def test_get_current_url_success(self, chrome_driver):
        mock_page = Mock()
        chrome_driver.page = mock_page
        mock_page.url = "https://example.com"
        
        url = chrome_driver.get_current_url()
        
        assert url == "https://example.com"

    def test_get_current_url_no_page(self, chrome_driver):
        with pytest.raises(RuntimeError, match="Page not started"):
            chrome_driver.get_current_url()

    def test_convert_selenium_selector(self, chrome_driver):
        """Test selector conversion from Selenium to Playwright format."""
        assert chrome_driver._convert_selenium_selector("id", "test") == "#test"
        assert chrome_driver._convert_selenium_selector("name", "test") == "[name='test']"
        assert chrome_driver._convert_selenium_selector("class_name", "test") == ".test"
        assert chrome_driver._convert_selenium_selector("tag_name", "div") == "div"
        assert chrome_driver._convert_selenium_selector("link_text", "test") == "text=test"
        assert chrome_driver._convert_selenium_selector("partial_link_text", "test") == "text=test"
        assert chrome_driver._convert_selenium_selector("css", ".test") == ".test"
        assert chrome_driver._convert_selenium_selector("xpath", "//div") == "//div"
        assert chrome_driver._convert_selenium_selector("unknown", "test") == "test"

    def test_context_manager(self, mock_playwright):
        with ChromeDriver() as driver:
            assert driver.playwright is not None