# Development Guide

## Code Quality Tools

This project uses multiple tools to ensure high code quality:

### **Ruff** - Fast Python Linter & Formatter
- **Linting**: `uv run ruff check .`
- **Auto-fix**: `uv run ruff check --fix .`
- **Formatting**: `uv run ruff format .`

### **MyPy** - Static Type Checker
- **Type checking**: `uv run mypy newrelic_mcp/`
- Catches type mismatches and improves code reliability
- Currently configured in lenient mode, can be made stricter over time

### **Pylint** - Additional Code Analysis
- **Code analysis**: `uv run pylint newrelic_mcp/`
- Detects code smells, complexity issues, and potential bugs

### **Pre-commit Hooks** (Recommended)
Automatically run quality checks before each commit:

```bash
# Install pre-commit hooks (one-time setup)
uv run pre-commit install

# Run all hooks manually
uv run pre-commit run --all-files
```

## Development Workflow

### **Quick Commands**
```bash
# Format code
uv run ruff format .

# Check all linting rules
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .

# Run type checking
uv run mypy newrelic_mcp/

# Run all quality checks
uv run ruff check . && uv run mypy newrelic_mcp/ && uv run pylint newrelic_mcp/
```

### **IDE Integration**

#### **IntelliJ/PyCharm**
1. Install Ruff plugin
2. Configure MyPy as external tool
3. Enable "Format on save" with Ruff

#### **VS Code** 
1. Install Ruff extension (`charliermarsh.ruff`)
2. Install Pylance for type checking
3. Add to settings.json:
```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.linting.enabled": true,
    "ruff.enabled": true,
    "python.formatting.provider": "ruff"
}
```

## Configuration Files

- **`pyproject.toml`**: Ruff, MyPy, and Pylint configuration
- **`.pre-commit-config.yaml`**: Pre-commit hooks setup
- **Ruff settings**: Line length 120, Python 3.11+ target
- **MyPy settings**: Lenient mode initially, can be made stricter

## Code Style Standards

### **Type Hints**
- Use modern Python 3.11+ syntax: `dict[str, Any]` instead of `Dict[str, Any]`
- Prefer `str | None` over `Optional[str]`
- Add type hints to new functions and methods

### **Code Organization**
- Keep functions focused and small
- Extract common logic to avoid duplication
- Use descriptive variable names (no single letters except for loops)
- Add docstrings for public APIs

### **Error Handling**
- Use exception chaining: `raise CustomError("message") from e`
- Prefer specific exception types over generic `Exception`
- Add meaningful error messages

## Incremental Improvement

The tooling is configured to be **lenient initially** but can be made stricter over time:

1. **Phase 1** (Current): Basic linting with Ruff, lenient MyPy
2. **Phase 2**: Enable stricter MyPy settings gradually
3. **Phase 3**: Add more Pylint rules, enable additional Ruff rules
4. **Phase 4**: Consider adding tools like `bandit` for security scanning

This approach allows existing code to pass checks while encouraging better practices for new code.