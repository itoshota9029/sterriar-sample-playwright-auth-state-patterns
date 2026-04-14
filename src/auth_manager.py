"""Authentication state manager for Playwright."""

import json
from pathlib import Path
from typing import Any


class AuthManager:
    """Manage Playwright authentication state with save/load/validation."""

    def __init__(self, storage_path: str | Path) -> None:
        """Initialize auth manager.

        Args:
            storage_path: Path to save authentication state JSON file
        """
        self.storage_path = Path(storage_path)

    def save_state(self, context: Any) -> None:
        """Save authentication state from browser context to file.

        Args:
            context: Playwright BrowserContext instance
        """
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        context.storage_state(path=str(self.storage_path))

    def load_state(self, context: Any) -> bool:
        """Load authentication state from file into browser context.

        Args:
            context: Playwright BrowserContext instance

        Returns:
            True if state was loaded successfully, False otherwise
        """
        if not self.storage_path.exists():
            return False

        try:
            with open(self.storage_path) as f:
                state = json.load(f)
            context.add_cookies(state.get("cookies", []))
            # Note: In real Playwright, you'd use context created with storage_state parameter
            # This simplified version demonstrates the concept
            return True
        except (json.JSONDecodeError, OSError):
            return False

    def is_authenticated(self, page: Any, indicator_selector: str, timeout: int = 5000) -> bool:
        """Check if the current session is still authenticated.

        Args:
            page: Playwright Page instance
            indicator_selector: CSS selector for element that indicates authenticated state
            timeout: Maximum time to wait for indicator in milliseconds

        Returns:
            True if authenticated indicator is present, False otherwise
        """
        try:
            element = page.wait_for_selector(indicator_selector, timeout=timeout, state="visible")
            return element is not None
        except Exception:
            return False

    def clear_state(self) -> bool:
        """Remove saved authentication state file.

        Returns:
            True if file was deleted, False if it didn't exist
        """
        if self.storage_path.exists():
            self.storage_path.unlink()
            return True
        return False

    def state_exists(self) -> bool:
        """Check if authentication state file exists.

        Returns:
            True if state file exists, False otherwise
        """
        return self.storage_path.exists()
