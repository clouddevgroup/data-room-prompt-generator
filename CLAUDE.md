# CLAUDE.md - Insights Generator Project Guidelines

## Build & Run Commands
- Run application: `python app.py` (basic) or `python app_with_anthropic.py` (with API)
- Install dependencies: `pip install -r requirements.txt`
- Lint Python files: `flake8 --max-line-length=100 *.py`
- Format Python files: `black *.py`
- Debug mode: Both `app.py` and `app_with_anthropic.py` run with `debug=True`

## Code Style Guidelines

### Python
- Imports: stdlib → third-party → local (with blank lines between groups)
- Functions: snake_case, descriptive names, docstrings explaining purpose
- Variables: snake_case, meaningful names
- Type hints encouraged for function parameters and returns
- Error handling: Use specific exceptions with try/except blocks
- Log errors when using app_with_anthropic.py

### JavaScript
- Use const/let over var
- Variables/functions: camelCase
- DOM element IDs: kebab-case
- Prefer descriptive names for elements and functions

### Project Structure
- Flask templates in `/templates`
- Static files in browser-accessible locations
- Store environment variables in `.env` file (excluded from git)
- Keep API keys secure and never commit them

### Anthropic API
- Set `ANTHROPIC_API_KEY` in `.env` file if using Claude API
- API calls use claude-3-sonnet-20240229 model by default