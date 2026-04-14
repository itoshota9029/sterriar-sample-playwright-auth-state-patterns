# playwright-auth-state

[![CI](https://github.com/example/playwright-auth-state/actions/workflows/ci.yml/badge.svg)](https://github.com/example/playwright-auth-state/actions/workflows/ci.yml)

A Python library for managing Playwright authentication state with automatic save, refresh, and expiration detection.

## Features

- 💾 **Save auth state** - Persist authentication state to disk after login
- 🔄 **Refresh detection** - Automatically detect when auth state has expired
- 🔐 **Reuse sessions** - Skip login by reloading saved authentication state
- 🧪 **Easy testing** - Mock-friendly design for unit tests

## Installation

```bash
pip install playwright-auth-state
playwright install  # Install browser binaries
```

## Quick Start

```python
from playwright.sync_api import sync_playwright
from src.auth_manager import AuthManager

# Initialize auth manager with a storage path
auth_manager = AuthManager(storage_path="auth_state.json")

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    
    # Try to load saved auth state
    if auth_manager.load_state(context):
        page.goto("https://example.com/dashboard")
        
        # Check if still authenticated
        if auth_manager.is_authenticated(page, indicator_selector="#user-menu"):
            print("Already logged in!")
        else:
            print("Auth expired, need to re-login")
            # Perform login...
            auth_manager.save_state(context)
    else:
        # No saved state, perform initial login
        page.goto("https://example.com/login")
        # ... login steps ...
        auth_manager.save_state(context)
    
    browser.close()
```

## Usage

### Basic Authentication Flow

```python
from src.auth_manager import AuthManager

auth = AuthManager(storage_path="./state/twitter.json")

# After successful login
auth.save_state(context)

# On subsequent runs
if auth.load_state(context):
    # State loaded successfully
    if auth.is_authenticated(page, indicator_selector=".profile-icon"):
        # Still logged in, proceed
        pass
```

### Validation Helpers

```python
from src.validators import URLValidator, ElementValidator

# Check if redirected to dashboard after login
url_validator = URLValidator(expected_pattern="/dashboard")
if url_validator.validate(page):
    print("Login successful!")

# Check if a specific element exists (e.g., user avatar)
element_validator = ElementValidator(selector=".user-avatar")
if element_validator.validate(page):
    print("User is authenticated")
```

## API Reference

### `AuthManager`

Main class for managing authentication state.

- `save_state(context)` - Save current browser context state to file
- `load_state(context)` - Load saved state into browser context
- `is_authenticated(page, indicator_selector)` - Check if session is still valid
- `clear_state()` - Remove saved authentication state file

### `URLValidator`

Validate current page URL matches expected pattern.

- `validate(page)` - Returns True if URL matches the pattern

### `ElementValidator`

Validate presence of specific DOM elements.

- `validate(page)` - Returns True if element exists on page

## Development

```bash
# Install in dev mode
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check .

# Format
ruff format .
```

## License

MIT License - see LICENSE file for details.
