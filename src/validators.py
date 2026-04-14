"""Validators for checking authentication status."""

import re
from typing import Any


class URLValidator:
    """Validate page URL matches expected pattern."""

    def __init__(self, expected_pattern: str, use_regex: bool = False) -> None:
        """Initialize URL validator.

        Args:
            expected_pattern: URL pattern to match (substring or regex)
            use_regex: If True, treat pattern as regex; otherwise as substring
        """
        self.expected_pattern = expected_pattern
        self.use_regex = use_regex
        if use_regex:
            self.regex = re.compile(expected_pattern)

    def validate(self, page: Any) -> bool:
        """Validate current page URL.

        Args:
            page: Playwright Page instance

        Returns:
            True if URL matches the expected pattern, False otherwise
        """
        current_url = page.url
        if self.use_regex:
            return bool(self.regex.search(current_url))
        return self.expected_pattern in current_url


class ElementValidator:
    """Validate presence of DOM elements on page."""

    def __init__(self, selector: str, timeout: int = 5000) -> None:
        """Initialize element validator.

        Args:
            selector: CSS selector for element to check
            timeout: Maximum time to wait for element in milliseconds
        """
        self.selector = selector
        self.timeout = timeout

    def validate(self, page: Any) -> bool:
        """Check if element exists on page.

        Args:
            page: Playwright Page instance

        Returns:
            True if element exists and is visible, False otherwise
        """
        try:
            element = page.wait_for_selector(self.selector, timeout=self.timeout, state="visible")
            return element is not None
        except Exception:
            return False


class CombinedValidator:
    """Combine multiple validators with AND logic."""

    def __init__(self, *validators: URLValidator | ElementValidator) -> None:
        """Initialize combined validator.

        Args:
            *validators: Variable number of validator instances
        """
        self.validators = validators

    def validate(self, page: Any) -> bool:
        """Check if all validators pass.

        Args:
            page: Playwright Page instance

        Returns:
            True if all validators pass, False otherwise
        """
        return all(validator.validate(page) for validator in self.validators)
