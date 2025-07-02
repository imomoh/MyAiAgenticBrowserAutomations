from typing import Optional
from pydantic import BaseSettings, Field
from pathlib import Path


class AgentSettings(BaseSettings):
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    agent_name: str = Field("BrowserAgent", env="AGENT_NAME")
    agent_description: str = Field(
        "AI agent for browser automation", env="AGENT_DESCRIPTION"
    )
    max_retries: int = Field(3, env="MAX_RETRIES")
    timeout_seconds: int = Field(30, env="TIMEOUT_SECONDS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class BrowserSettings(BaseSettings):
    browser_type: str = Field("chrome", env="BROWSER_TYPE")
    headless_mode: bool = Field(False, env="HEADLESS_MODE")
    window_width: int = Field(1920, env="WINDOW_WIDTH")
    window_height: int = Field(1080, env="WINDOW_HEIGHT")
    user_data_dir: str = Field("./chrome_data", env="USER_DATA_DIR")
    allowed_domains: str = Field("*", env="ALLOWED_DOMAINS")
    blocked_domains: str = Field("", env="BLOCKED_DOMAINS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class LoggingSettings(BaseSettings):
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("logs/agent.log", env="LOG_FILE")
    log_format: str = Field("json", env="LOG_FORMAT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class Settings:
    def __init__(self):
        self.agent = AgentSettings()
        self.browser = BrowserSettings()
        self.logging = LoggingSettings()

    @classmethod
    def load(cls) -> "Settings":
        return cls()


settings = Settings.load()