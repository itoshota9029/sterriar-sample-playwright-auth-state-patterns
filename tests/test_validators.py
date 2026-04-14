"""Tests for validator classes."""

from unittest.mock import Mock

from src.validators import CombinedValidator, ElementValidator, URLValidator


class TestURLValidator:
    """Test suite for URLValidator."""

    def test_validate_substring_match(self):
        """Test URL validation with substring matching."""
        validator = URLValidator("/dashboard")
        mock_page = Mock()
        mock_page.url = "https://app.example.com/dashboard/overview"

        result = validator.validate(mock_page)

        assert result is True

    def test_validate_substring_no_match(self):
        """Test URL validation fails when substring doesn't match."""
        validator = URLValidator("/admin")
        mock_page = Mock()
        mock_page.url = "https://app.example.com/user/profile"

        result = validator.validate(mock_page)

        assert result is False

    def test_validate_regex_match(self):
        """Test URL validation with regex pattern."""
        validator = URLValidator(r"/user/\d+", use_regex=True)
        mock_page = Mock()
        mock_page.url = "https://example.com/user/12345/profile"

        result = validator.validate(mock_page)

        assert result is True

    def test_validate_regex_no_match(self):
        """Test URL validation fails when regex doesn't match."""
        validator = URLValidator(r"^https://secure\.example\.com", use_regex=True)
        mock_page = Mock()
        mock_page.url = "https://example.com/login"

        result = validator.validate(mock_page)

        assert result is False

    def test_validate_with_query_params(self):
        """Test URL validation handles query parameters correctly."""
        validator = URLValidator("/search")
        mock_page = Mock()
        mock_page.url = "https://example.com/search?q=playwright&lang=en"

        result = validator.validate(mock_page)

        assert result is True


class TestElementValidator:
    """Test suite for ElementValidator."""

    def test_validate_element_exists(self):
        """Test validation passes when element is found."""
        validator = ElementValidator(".user-profile")
        mock_page = Mock()
        mock_element = Mock()
        mock_page.wait_for_selector.return_value = mock_element

        result = validator.validate(mock_page)

        assert result is True
        mock_page.wait_for_selector.assert_called_once_with(
            ".user-profile", timeout=5000, state="visible"
        )

    def test_validate_element_not_found(self):
        """Test validation fails when element is not found."""
        validator = ElementValidator("#login-button")
        mock_page = Mock()
        mock_page.wait_for_selector.side_effect = Exception("Timeout waiting for selector")

        result = validator.validate(mock_page)

        assert result is False

    def test_validate_with_custom_timeout(self):
        """Test element validation respects custom timeout."""
        validator = ElementValidator(".navbar", timeout=15000)
        mock_page = Mock()
        mock_page.wait_for_selector.return_value = Mock()

        validator.validate(mock_page)

        mock_page.wait_for_selector.assert_called_once_with(
            ".navbar", timeout=15000, state="visible"
        )

    def test_validate_handles_various_exceptions(self):
        """Test validation handles different types of exceptions gracefully."""
        validator = ElementValidator("#user-menu")
        mock_page = Mock()

        # Test with different exception types
        for exception in [TimeoutError("timeout"), RuntimeError("error"), ValueError("invalid")]:
            mock_page.wait_for_selector.side_effect = exception
            result = validator.validate(mock_page)
            assert result is False


class TestCombinedValidator:
    """Test suite for CombinedValidator."""

    def test_validate_all_pass(self):
        """Test combined validation passes when all validators pass."""
        url_validator = URLValidator("/dashboard")
        element_validator = ElementValidator(".user-avatar")

        combined = CombinedValidator(url_validator, element_validator)

        mock_page = Mock()
        mock_page.url = "https://app.example.com/dashboard"
        mock_page.wait_for_selector.return_value = Mock()

        result = combined.validate(mock_page)

        assert result is True

    def test_validate_one_fails(self):
        """Test combined validation fails if any validator fails."""
        url_validator = URLValidator("/admin")
        element_validator = ElementValidator(".admin-panel")

        combined = CombinedValidator(url_validator, element_validator)

        mock_page = Mock()
        mock_page.url = "https://app.example.com/dashboard"  # Wrong URL
        mock_page.wait_for_selector.return_value = Mock()  # Element exists

        result = combined.validate(mock_page)

        assert result is False

    def test_validate_multiple_validators(self):
        """Test combined validation with multiple validators."""
        validators = [
            URLValidator("/secure"),
            ElementValidator("#header"),
            ElementValidator(".footer"),
            URLValidator("https", use_regex=False),
        ]

        combined = CombinedValidator(*validators)

        mock_page = Mock()
        mock_page.url = "https://example.com/secure/dashboard"
        mock_page.wait_for_selector.return_value = Mock()

        result = combined.validate(mock_page)

        assert result is True

    def test_validate_empty_validators(self):
        """Test combined validation with no validators returns True."""
        combined = CombinedValidator()
        mock_page = Mock()

        result = combined.validate(mock_page)

        assert result is True
