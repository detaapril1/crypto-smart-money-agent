# Contributing to Crypto Smart Money AI Agent

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read and follow our Code of Conduct:

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Report inappropriate behavior to maintainers

## Getting Started

### 1. Fork and Clone
```bash
git clone https://github.com/detaapril1/crypto-smart-money-agent.git
cd crypto-smart-money-agent
```

### 2. Create Development Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install pytest pytest-asyncio black flake8 mypy
```

### 3. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## Development Workflow

### Code Style

We follow PEP 8 with these tools:

**Format code with Black:**
```bash
black app/ tests/
```

**Check style with Flake8:**
```bash
flake8 app/ tests/
```

**Type checking with MyPy:**
```bash
mypy app/
```

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add smart money detection module
fix: resolve telegram alert formatting issue
docs: update API documentation
test: add tests for screening module
refactor: improve database connection handling
```

**Format:** `type: brief description`

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `chore`

### Testing

Write tests for new features:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_screening.py -v

# Run specific test
pytest tests/test_screening.py::test_good_token_passes -v
```

**Coverage Requirement:** Minimum 70% code coverage

### Documentation

- Update README.md for user-facing changes
- Add docstrings to functions and classes
- Update CHANGELOG.md for significant changes
- Add comments for complex logic

## Making a Pull Request

### Before Submitting

1. **Update your branch**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Run tests locally**
   ```bash
   pytest tests/ --cov=app
   ```

3. **Format and lint**
   ```bash
   black app/ tests/
   flake8 app/ tests/
   mypy app/
   ```

4. **Add tests for new features**
   - Each new feature should have corresponding tests
   - Bug fixes should include a test that reproduces the bug

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #(issue number)

## Testing
Describe how you tested this change

## Screenshots (if applicable)
Add images for UI changes

## Checklist
- [ ] Code follows PEP 8 style
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] All tests pass locally
- [ ] Commit messages are clear
```

## Project Structure Guidelines

### New Module Example

For adding a new collector (e.g., for a new data source):

1. **Create module** in `app/collectors/new_source.py`
2. **Follow existing patterns:**
   ```python
   import logging
   
   logger = logging.getLogger(__name__)
   
   class NewSourceCollector:
       async def initialize(self):
           pass
       
       async def close(self):
           pass
       
       async def fetch_data(self):
           pass
   ```

3. **Add tests** in `tests/test_new_source.py`
4. **Update imports** in `__init__.py`
5. **Integrate** with orchestrator if needed
6. **Document** in README and API docs

## Directory Structure

- **app/** - Main application code
  - **collectors/** - Data collection modules
  - **analyzers/** - Analysis engines
  - **alerts/** - Alert systems
  - **database/** - Data persistence
  - **services/** - Business logic
  - **api/** - API endpoints
  - **utils/** - Utility functions

- **tests/** - Unit and integration tests
- **docs/** - Documentation files
- **docker/** - Docker configuration
- **scripts/** - Utility scripts

## Common Tasks

### Adding a New API Integration

1. Create collector in `app/collectors/`
2. Implement `initialize()`, `close()`, and data methods
3. Add error handling and logging
4. Write unit tests
5. Update `orchestrator.py` to use it
6. Document in README

### Adding a New Alert Type

1. Create alert handler in `app/alerts/`
2. Implement `send_alert()` method
3. Format message appropriately
4. Add error handling
5. Test with mock/test credentials
6. Document in README

### Adding a New Analyzer

1. Create analyzer in `app/analyzers/`
2. Implement analysis logic
3. Return structured results
4. Add comprehensive tests
5. Integrate with orchestrator if needed

## Release Process

### Version Bumping
We follow Semantic Versioning (MAJOR.MINOR.PATCH)

1. Update version in `app/utils/config.py`
2. Update CHANGELOG.md
3. Create git tag: `git tag v1.0.0`
4. Push tag: `git push origin v1.0.0`

### Documentation for Release
- Update README.md with new features
- Update CHANGELOG.md with all changes
- Create GitHub Release with highlights

## Need Help?

- Check existing issues and discussions
- Read the documentation in `docs/`
- Ask in GitHub Discussions
- Open an issue for bugs or questions

## Resources

- [Python Style Guide (PEP 8)](https://www.python.org/dev/peps/pep-0008/)
- [Async/Await Documentation](https://docs.python.org/3/library/asyncio.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## Thank You!

Your contributions help make this project better. We appreciate your time and effort! 🎉
