class AgentError(Exception):
    pass


class BrowserError(AgentError):
    pass


class ConfigurationError(AgentError):
    pass


class AIServiceError(AgentError):
    pass