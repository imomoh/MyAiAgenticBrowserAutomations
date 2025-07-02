# Contributing to AI Browser Agent

Thank you for your interest in contributing to the AI Browser Agent! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Contribution Guidelines](#contribution-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Feature Requests](#feature-requests)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, visible or invisible disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

Examples of behavior that contributes to a positive environment:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

Examples of unacceptable behavior:
- The use of sexualized language or imagery and unwelcome sexual attention or advances
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate in a professional setting

### Enforcement

Project maintainers are responsible for clarifying standards of acceptable behavior and will take appropriate and fair corrective action in response to any instances of unacceptable behavior.

## Getting Started

### Prerequisites

Before contributing, ensure you have:
- Python 3.9 or higher
- Git
- Chrome browser
- OpenAI API key (for testing AI features)
- Familiarity with the project structure (see [Development Guide](docs/DEVELOPMENT.md))

### Setting Up Development Environment

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/ai-browser-agent.git
   cd ai-browser-agent
   ```
3. **Set up development environment**:
   ```bash
   make dev
   # Or manually:
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -e .
   pre-commit install
   ```
4. **Verify setup**:
   ```bash
   make test
   make quality
   ```

## Development Workflow

### Branch Strategy

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/**: Feature development branches
- **bugfix/**: Bug fix branches
- **hotfix/**: Emergency fixes for production

### Workflow Steps

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Follow code standards (see below)
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**:
   ```bash
   make test
   make quality
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   # Create PR on GitHub
   ```

## Contribution Guidelines

### Code Standards

#### Python Code Style
- **Formatting**: Use Black (line length: 88)
- **Linting**: Follow Flake8 rules
- **Type Hints**: Required for all public APIs
- **Docstrings**: Google-style for all public functions

```python
def execute_task(self, task_description: str) -> ActionResult:
    """Execute a natural language task description.
    
    Args:
        task_description: Natural language description of the task
        
    Returns:
        ActionResult containing success status and execution data
        
    Raises:
        AgentError: If the task cannot be executed
    """
```

#### Commit Message Format

Use conventional commit format:
```
type(scope): description

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes (formatting)
- refactor: Code refactoring
- test: Adding or updating tests
- chore: Maintenance tasks

Examples:
feat(agent): add support for Firefox browser
fix(browser): handle timeout errors gracefully
docs(api): update action type documentation
```

#### Testing Requirements
- **Unit tests**: Required for all new functions
- **Integration tests**: Required for new features
- **Test coverage**: Maintain >90% coverage
- **Mock external dependencies**: Use mocks for OpenAI API, browser

```python
def test_execute_task_success(self, mock_driver, mock_openai):
    """Test successful task execution."""
    # Arrange
    mock_openai.return_value = valid_response
    agent = BrowserAgent()
    
    # Act
    result = agent.execute_task("test task")
    
    # Assert
    assert result.success is True
    mock_driver.navigate_to.assert_called_once()
```

### Documentation Standards

#### Code Documentation
- **Public APIs**: Must have comprehensive docstrings
- **Complex logic**: Add inline comments
- **Type hints**: Required for all function signatures

#### User Documentation
- **New features**: Update relevant documentation files
- **Breaking changes**: Update migration guides
- **Examples**: Include practical usage examples

### Quality Checks

All contributions must pass:
```bash
make format        # Code formatting
make lint          # Linting
make type-check    # Type checking
make test          # All tests
make quality       # All quality checks
```

## Pull Request Process

### PR Checklist

Before submitting a PR, ensure:
- [ ] Code follows project standards
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated (for significant changes)
- [ ] PR description explains the changes
- [ ] Related issues are referenced

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Documentation
- [ ] Code documentation updated
- [ ] User documentation updated
- [ ] API documentation updated

## Related Issues
Fixes #(issue number)
```

### Review Process

1. **Automated checks**: CI must pass
2. **Code review**: At least one maintainer review required
3. **Testing**: Reviewer will test the changes
4. **Approval**: Maintainer approval required for merge

### Addressing Review Comments

- Address all review comments
- Push additional commits to the same branch
- Request re-review after changes
- Engage constructively with feedback

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear description of what you expected to happen.

**Environment:**
- OS: [e.g. macOS 12.0]
- Python version: [e.g. 3.11]
- Project version: [e.g. 0.1.0]
- Chrome version: [e.g. 120.0]

**Additional context**
Add any other context about the problem here.
```

### Security Issues

For security vulnerabilities:
1. **Do not create public issues**
2. **Email**: security@project-email.com
3. **Include**: Detailed description and reproduction steps
4. **Response**: We'll respond within 48 hours

## Feature Requests

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
A clear description of any alternative solutions.

**Additional context**
Add any other context or screenshots about the feature request.
```

### Feature Development Process

1. **Discussion**: Open an issue for discussion
2. **Design**: Agree on implementation approach
3. **Implementation**: Develop the feature
4. **Review**: Submit PR for review
5. **Documentation**: Update relevant docs

## Documentation

### Documentation Types

1. **User Documentation**: Setup, usage, tutorials
2. **API Documentation**: Reference for programmatic use
3. **Developer Documentation**: Architecture, contributing
4. **Code Documentation**: Inline comments and docstrings

### Documentation Guidelines

- **Clear and concise**: Easy to understand
- **Complete examples**: Include working code examples
- **Current**: Keep documentation up to date
- **Accessible**: Appropriate for target audience

### Documentation Updates

When contributing code that:
- Adds new features → Update user documentation
- Changes APIs → Update API documentation
- Modifies architecture → Update developer documentation
- Fixes bugs → Update troubleshooting documentation

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussions
- **Pull Requests**: Code review and collaboration

### Getting Help

1. **Check documentation**: Review existing docs first
2. **Search issues**: Look for similar problems
3. **Ask questions**: Use GitHub Discussions
4. **Be specific**: Provide context and details

### Helping Others

- **Answer questions**: Help other users in discussions
- **Review PRs**: Provide constructive feedback
- **Improve documentation**: Fix typos and clarify content
- **Share examples**: Contribute usage examples

## Recognition

### Contributors

We recognize contributors in:
- **README.md**: List of contributors
- **CHANGELOG.md**: Credit for specific contributions
- **GitHub**: Contributor statistics

### Types of Contributions

We value all types of contributions:
- **Code**: Features, bug fixes, improvements
- **Documentation**: Writing, editing, examples
- **Testing**: Test cases, bug reports, QA
- **Design**: User experience, interfaces
- **Community**: Helping others, discussions

## Development Guidelines

### Adding New Features

1. **Start with an issue**: Discuss the feature first
2. **Follow architecture**: Maintain existing patterns
3. **Add tests**: Comprehensive test coverage
4. **Update docs**: Include documentation updates
5. **Consider backwards compatibility**: Avoid breaking changes

### Code Review Guidelines

When reviewing PRs:
- **Be constructive**: Provide helpful feedback
- **Be specific**: Point out exact issues
- **Suggest solutions**: Don't just identify problems
- **Appreciate effort**: Recognize good work
- **Test thoroughly**: Verify functionality

### Release Process

Maintainers handle releases, but contributors can:
- **Suggest versions**: For significant changes
- **Update changelog**: Document contributions
- **Test prereleases**: Help verify release candidates

## Questions?

If you have questions about contributing:
1. Check this document and other documentation
2. Search existing GitHub issues and discussions
3. Open a new discussion for general questions
4. Open an issue for specific problems

Thank you for contributing to AI Browser Agent! 🚀