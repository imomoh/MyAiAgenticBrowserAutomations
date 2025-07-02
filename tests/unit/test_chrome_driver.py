import pytest
from unittest.mock import Mock, patch, MagicMock
from selenium.webdriver.common.by import By
from src.browser.chrome_driver import ChromeDriver


@pytest.fixture
def mock_webdriver():
    with patch('src.browser.chrome_driver.webdriver.Chrome') as mock:
        driver = Mock()
        mock.return_value = driver
        yield driver


@pytest.fixture
def mock_service():
    with patch('src.browser.chrome_driver.Service') as mock:
        yield mock


@pytest.fixture
def mock_chrome_driver_manager():
    with patch('src.browser.chrome_driver.ChromeDriverManager') as mock:
        manager = Mock()
        manager.install.return_value = "/path/to/chromedriver"
        mock.return_value = manager
        yield manager


@pytest.fixture
def chrome_driver():
    return ChromeDriver()


class TestChromeDriver:
    def test_init(self, chrome_driver):
        assert chrome_driver.driver is None
        assert chrome_driver.wait is None

    def test_start_success(self, chrome_driver, mock_webdriver, mock_service, mock_chrome_driver_manager):
        with patch('src.browser.chrome_driver.WebDriverWait') as mock_wait:
            chrome_driver.start()
            
            assert chrome_driver.driver == mock_webdriver
            mock_webdriver.set_window_size.assert_called_once()
            assert chrome_driver.wait is not None

    def test_start_failure(self, chrome_driver, mock_chrome_driver_manager):
        with patch('src.browser.chrome_driver.webdriver.Chrome') as mock_chrome:
            mock_chrome.side_effect = Exception("Driver failed to start")
            
            with pytest.raises(Exception):
                chrome_driver.start()

    def test_stop_success(self, chrome_driver):
        mock_driver = Mock()
        chrome_driver.driver = mock_driver
        
        chrome_driver.stop()
        
        mock_driver.quit.assert_called_once()
        assert chrome_driver.driver is None
        assert chrome_driver.wait is None

    def test_stop_with_error(self, chrome_driver):
        mock_driver = Mock()
        mock_driver.quit.side_effect = Exception("Quit failed")
        chrome_driver.driver = mock_driver
        
        chrome_driver.stop()  # Should not raise exception
        
        assert chrome_driver.driver is None
        assert chrome_driver.wait is None

    def test_navigate_to_success(self, chrome_driver):
        mock_driver = Mock()
        chrome_driver.driver = mock_driver
        url = "https://example.com"
        
        chrome_driver.navigate_to(url)
        
        mock_driver.get.assert_called_once_with(url)

    def test_navigate_to_no_driver(self, chrome_driver):
        with pytest.raises(RuntimeError, match="Driver not started"):
            chrome_driver.navigate_to("https://example.com")

    def test_find_element_success(self, chrome_driver):
        mock_driver = Mock()
        mock_wait = Mock()
        mock_element = Mock()
        
        chrome_driver.driver = mock_driver
        chrome_driver.wait = mock_wait
        mock_wait.until.return_value = mock_element
        
        result = chrome_driver.find_element(By.ID, "test-id")
        
        assert result == mock_element
        mock_wait.until.assert_called_once()

    def test_find_element_no_driver(self, chrome_driver):
        with pytest.raises(RuntimeError, match="Driver not started"):
            chrome_driver.find_element(By.ID, "test-id")

    def test_click_element_success(self, chrome_driver):
        mock_element = Mock()
        
        with patch.object(chrome_driver, 'find_element', return_value=mock_element):
            chrome_driver.click_element(By.ID, "test-id")
            
            mock_element.click.assert_called_once()

    def test_send_keys_success(self, chrome_driver):
        mock_element = Mock()
        
        with patch.object(chrome_driver, 'find_element', return_value=mock_element):
            chrome_driver.send_keys(By.ID, "test-id", "test text")
            
            mock_element.clear.assert_called_once()
            mock_element.send_keys.assert_called_once_with("test text")

    def test_get_text_success(self, chrome_driver):
        mock_element = Mock()
        mock_element.text = "Element text"
        
        with patch.object(chrome_driver, 'find_element', return_value=mock_element):
            text = chrome_driver.get_text(By.ID, "test-id")
            
            assert text == "Element text"

    def test_get_attribute_success(self, chrome_driver):
        mock_element = Mock()
        mock_element.get_attribute.return_value = "attribute value"
        
        with patch.object(chrome_driver, 'find_element', return_value=mock_element):
            value = chrome_driver.get_attribute(By.ID, "test-id", "href")
            
            assert value == "attribute value"
            mock_element.get_attribute.assert_called_once_with("href")

    def test_get_attribute_none_result(self, chrome_driver):
        mock_element = Mock()
        mock_element.get_attribute.return_value = None
        
        with patch.object(chrome_driver, 'find_element', return_value=mock_element):
            value = chrome_driver.get_attribute(By.ID, "test-id", "href")
            
            assert value == ""

    def test_execute_script_success(self, chrome_driver):
        mock_driver = Mock()
        chrome_driver.driver = mock_driver
        mock_driver.execute_script.return_value = "script result"
        
        result = chrome_driver.execute_script("return 'test';")
        
        assert result == "script result"
        mock_driver.execute_script.assert_called_once_with("return 'test';")

    def test_execute_script_no_driver(self, chrome_driver):
        with pytest.raises(RuntimeError, match="Driver not started"):
            chrome_driver.execute_script("return 'test';")

    @patch('src.browser.chrome_driver.Path')
    def test_take_screenshot_success(self, mock_path, chrome_driver):
        mock_driver = Mock()
        chrome_driver.driver = mock_driver
        mock_driver.save_screenshot.return_value = True
        
        mock_screenshot_path = Mock()
        mock_screenshot_path.parent.mkdir = Mock()
        mock_path.return_value = mock_screenshot_path
        
        result = chrome_driver.take_screenshot("test.png")
        
        assert result is True
        mock_driver.save_screenshot.assert_called_once()
        mock_screenshot_path.parent.mkdir.assert_called_once_with(exist_ok=True)

    def test_take_screenshot_no_driver(self, chrome_driver):
        with pytest.raises(RuntimeError, match="Driver not started"):
            chrome_driver.take_screenshot("test.png")

    def test_get_page_source_success(self, chrome_driver):
        mock_driver = Mock()
        chrome_driver.driver = mock_driver
        mock_driver.page_source = "<html>test</html>"
        
        source = chrome_driver.get_page_source()
        
        assert source == "<html>test</html>"

    def test_get_page_source_no_driver(self, chrome_driver):
        with pytest.raises(RuntimeError, match="Driver not started"):
            chrome_driver.get_page_source()

    def test_get_current_url_success(self, chrome_driver):
        mock_driver = Mock()
        chrome_driver.driver = mock_driver
        mock_driver.current_url = "https://example.com"
        
        url = chrome_driver.get_current_url()
        
        assert url == "https://example.com"

    def test_get_current_url_no_driver(self, chrome_driver):
        with pytest.raises(RuntimeError, match="Driver not started"):
            chrome_driver.get_current_url()

    @patch('src.browser.chrome_driver.Path')
    def test_get_chrome_options(self, mock_path, chrome_driver):
        mock_path.return_value.mkdir = Mock()
        
        options = chrome_driver._get_chrome_options()
        
        assert options is not None
        # Check that some expected arguments are present
        arguments = options.arguments
        assert "--no-sandbox" in arguments
        assert "--disable-dev-shm-usage" in arguments

    def test_context_manager(self, mock_webdriver, mock_service, mock_chrome_driver_manager):
        with patch('src.browser.chrome_driver.WebDriverWait'):
            with ChromeDriver() as driver:
                assert driver.driver is not None
        
        # Driver should be stopped after context exit
        mock_webdriver.quit.assert_called_once()