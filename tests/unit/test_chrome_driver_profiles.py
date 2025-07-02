import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json
from src.browser.chrome_driver import ChromeDriver, ChromeProfile


class TestChromeProfile:
    def test_chrome_profile_creation(self):
        profile = ChromeProfile(
            name="Test Profile",
            path=Path("/test/path"),
            email="test@example.com",
            is_default=True
        )
        
        assert profile.name == "Test Profile"
        assert profile.path == Path("/test/path")
        assert profile.email == "test@example.com"
        assert profile.is_default is True
    
    def test_chrome_profile_str_representation(self):
        profile = ChromeProfile(
            name="Test Profile",
            path=Path("/test/path"),
            email="test@example.com",
            is_default=True
        )
        
        expected = "Test Profile (test@example.com) [Default]"
        assert str(profile) == expected
    
    def test_chrome_profile_str_no_email(self):
        profile = ChromeProfile(
            name="Test Profile",
            path=Path("/test/path"),
            email=None,
            is_default=False
        )
        
        expected = "Test Profile"
        assert str(profile) == expected


class TestChromeDriverProfiles:
    @pytest.fixture
    def mock_chrome_data_dir(self, tmp_path):
        """Create a mock Chrome data directory structure."""
        # Create the full path structure for macOS
        home_dir = tmp_path / "Users" / "test"
        home_dir.mkdir(parents=True)
        
        chrome_data = home_dir / "Library" / "Application Support" / "Google" / "Chrome"
        chrome_data.mkdir(parents=True)
        
        # Create Local State file
        local_state = {
            "profile": {
                "info_cache": {
                    "Default": {
                        "email": "default@example.com",
                        "name": "Default"
                    },
                    "Profile 1": {
                        "email": "work@example.com",
                        "name": "Work Account"
                    },
                    "Profile 2": {
                        "email": "personal@example.com",
                        "name": "Personal"
                    }
                }
            }
        }
        
        with open(chrome_data / "Local State", 'w') as f:
            json.dump(local_state, f)
        
        # Create profile directories
        (chrome_data / "Default").mkdir()
        (chrome_data / "Profile 1").mkdir()
        (chrome_data / "Profile 2").mkdir()
        
        # Create some non-profile directories
        (chrome_data / "Crashpad").mkdir()
        (chrome_data / "GPUCache").mkdir()
        
        return chrome_data
    
    @patch('src.browser.chrome_driver.settings')
    def test_get_available_profiles(self, mock_settings, mock_chrome_data_dir):
        """Test getting available Chrome profiles."""
        mock_settings.browser.profile_path = None
        
        driver = ChromeDriver()
        
        # Mock the _get_chrome_data_directory method directly
        with patch.object(driver, '_get_chrome_data_directory', return_value=mock_chrome_data_dir):
            profiles = driver.get_available_profiles()
        
        assert len(profiles) == 3
        
        # Check that profiles are sorted correctly (Default first)
        assert profiles[0].name == "Default"
        assert profiles[0].is_default is True
        assert profiles[0].email == "default@example.com"
        
        assert profiles[1].name == "Profile 1"
        assert profiles[1].is_default is False
        assert profiles[1].email == "work@example.com"
        
        assert profiles[2].name == "Profile 2"
        assert profiles[2].is_default is False
        assert profiles[2].email == "personal@example.com"
    
    @patch('src.browser.chrome_driver.settings')
    def test_get_available_profiles_no_local_state(self, mock_settings, tmp_path):
        """Test getting profiles when Local State doesn't exist."""
        mock_settings.browser.profile_path = None
        
        # Create Chrome data dir without Local State
        chrome_data = tmp_path / "Chrome"
        chrome_data.mkdir()
        (chrome_data / "Default").mkdir()
        
        driver = ChromeDriver()
        
        # Mock the _get_chrome_data_directory method directly
        with patch.object(driver, '_get_chrome_data_directory', return_value=chrome_data):
            profiles = driver.get_available_profiles()
        
        # Should still find the Default profile
        assert len(profiles) == 1
        assert profiles[0].name == "Default"
        assert profiles[0].is_default is True
        assert profiles[0].email is None
    
    @patch('src.browser.chrome_driver.settings')
    def test_get_chrome_data_directory_custom_path(self, mock_settings):
        """Test getting Chrome data directory with custom profile path."""
        custom_path = "/custom/chrome/path"
        mock_settings.browser.profile_path = custom_path
        
        driver = ChromeDriver()
        result = driver._get_chrome_data_directory()
        
        assert result == Path(custom_path)
    
    @patch('src.browser.chrome_driver.settings')
    def test_get_chrome_data_directory_platform_specific(self, mock_settings):
        """Test getting Chrome data directory for different platforms."""
        mock_settings.browser.profile_path = None
        
        driver = ChromeDriver()
        
        # Test macOS
        with patch('src.browser.chrome_driver.platform.system', return_value="Darwin"):
            with patch('src.browser.chrome_driver.Path.home', return_value=Path("/Users/test")):
                result = driver._get_chrome_data_directory()
                expected = Path("/Users/test/Library/Application Support/Google/Chrome")
                assert result == expected
        
        # Test Windows
        with patch('src.browser.chrome_driver.platform.system', return_value="Windows"):
            with patch('src.browser.chrome_driver.Path.home', return_value=Path("C:\\Users\\test")):
                result = driver._get_chrome_data_directory()
                expected = Path("C:\\Users\\test/AppData/Local/Google/Chrome/User Data")
                assert result == expected
        
        # Test Linux
        with patch('src.browser.chrome_driver.platform.system', return_value="Linux"):
            with patch('src.browser.chrome_driver.Path.home', return_value=Path("/home/test")):
                result = driver._get_chrome_data_directory()
                expected = Path("/home/test/.config/google-chrome")
                assert result == expected
    
    def test_get_email_from_preferences(self, tmp_path):
        """Test extracting email from Preferences file."""
        driver = ChromeDriver()
        
        # Create a mock Preferences file
        prefs_path = tmp_path / "Preferences"
        prefs_data = {
            "account_tracker_service": {
                "last_known_gaia_id": "test@example.com"
            }
        }
        
        with open(prefs_path, 'w') as f:
            json.dump(prefs_data, f)
        
        email = driver._get_email_from_preferences(tmp_path)
        assert email == "test@example.com"
    
    def test_get_email_from_preferences_no_file(self, tmp_path):
        """Test extracting email when Preferences file doesn't exist."""
        driver = ChromeDriver()
        
        email = driver._get_email_from_preferences(tmp_path)
        assert email is None
    
    @patch('builtins.input', return_value="1")
    def test_select_profile_single_profile(self, mock_input, mock_chrome_data_dir):
        """Test profile selection when only one profile is available."""
        with patch('src.browser.chrome_driver.settings') as mock_settings:
            mock_settings.browser.profile_path = None
            
            # Get the home directory from the mock chrome data dir
            home_dir = mock_chrome_data_dir.parent.parent.parent
            
            with patch('src.browser.chrome_driver.platform.system', return_value="Darwin"):
                with patch('src.browser.chrome_driver.Path.home', return_value=home_dir):
                    driver = ChromeDriver()
                    
                    # Mock to return only one profile
                    with patch.object(driver, 'get_available_profiles') as mock_get_profiles:
                        single_profile = ChromeProfile("Default", Path("/test"), "test@example.com", True)
                        mock_get_profiles.return_value = [single_profile]
                        
                        selected = driver.select_profile()
                        
                        assert selected == single_profile
                        assert driver.selected_profile == single_profile
                        # Should not prompt for input
                        mock_input.assert_not_called()
    
    @patch('builtins.input', return_value="2")
    def test_select_profile_multiple_profiles(self, mock_input, mock_chrome_data_dir):
        """Test profile selection when multiple profiles are available."""
        with patch('src.browser.chrome_driver.settings') as mock_settings:
            mock_settings.browser.profile_path = None
            
            # Get the home directory from the mock chrome data dir
            home_dir = mock_chrome_data_dir.parent.parent.parent
            
            with patch('src.browser.chrome_driver.platform.system', return_value="Darwin"):
                with patch('src.browser.chrome_driver.Path.home', return_value=home_dir):
                    driver = ChromeDriver()
                    
                    # Mock to return multiple profiles
                    with patch.object(driver, 'get_available_profiles') as mock_get_profiles:
                        profile1 = ChromeProfile("Default", Path("/test1"), "default@example.com", True)
                        profile2 = ChromeProfile("Work", Path("/test2"), "work@example.com", False)
                        mock_get_profiles.return_value = [profile1, profile2]
                        
                        selected = driver.select_profile()
                        
                        assert selected == profile2  # User selected option 2
                        assert driver.selected_profile == profile2
                        mock_input.assert_called_once()
    
    def test_select_profile_by_name(self, mock_chrome_data_dir):
        """Test profile selection by specific name."""
        with patch('src.browser.chrome_driver.settings') as mock_settings:
            mock_settings.browser.profile_path = None
            
            # Get the home directory from the mock chrome data dir
            home_dir = mock_chrome_data_dir.parent.parent.parent
            
            with patch('src.browser.chrome_driver.platform.system', return_value="Darwin"):
                with patch('src.browser.chrome_driver.Path.home', return_value=home_dir):
                    driver = ChromeDriver()
                    
                    # Mock to return multiple profiles
                    with patch.object(driver, 'get_available_profiles') as mock_get_profiles:
                        profile1 = ChromeProfile("Default", Path("/test1"), "default@example.com", True)
                        profile2 = ChromeProfile("Work", Path("/test2"), "work@example.com", False)
                        mock_get_profiles.return_value = [profile1, profile2]
                        
                        selected = driver.select_profile("Work")
                        
                        assert selected == profile2
                        assert driver.selected_profile == profile2
    
    def test_select_profile_by_name_not_found(self, mock_chrome_data_dir):
        """Test profile selection with non-existent profile name."""
        with patch('src.browser.chrome_driver.settings') as mock_settings:
            mock_settings.browser.profile_path = None
            
            # Get the home directory from the mock chrome data dir
            home_dir = mock_chrome_data_dir.parent.parent.parent
            
            with patch('src.browser.chrome_driver.platform.system', return_value="Darwin"):
                with patch('src.browser.chrome_driver.Path.home', return_value=home_dir):
                    driver = ChromeDriver()
                    
                    # Mock to return multiple profiles
                    with patch.object(driver, 'get_available_profiles') as mock_get_profiles:
                        profile1 = ChromeProfile("Default", Path("/test1"), "default@example.com", True)
                        profile2 = ChromeProfile("Work", Path("/test2"), "work@example.com", False)
                        mock_get_profiles.return_value = [profile1, profile2]
                        
                        with pytest.raises(ValueError, match="Profile 'NonExistent' not found"):
                            driver.select_profile("NonExistent")
    
    def test_select_profile_no_profiles(self):
        """Test profile selection when no profiles are available."""
        driver = ChromeDriver()
        
        with patch.object(driver, 'get_available_profiles', return_value=[]):
            with pytest.raises(RuntimeError, match="No Chrome profiles found"):
                driver.select_profile() 