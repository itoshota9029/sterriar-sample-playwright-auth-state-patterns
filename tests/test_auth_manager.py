"""Tests for AuthManager class."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock

from src.auth_manager import AuthManager


class TestAuthManager:
    """Test suite for AuthManager."""

    def test_save_state_creates_directory(self):
        """Test that save_state creates parent directories if they don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "nested" / "dir" / "auth.json"
            auth_manager = AuthManager(storage_path)

            mock_context = Mock()
            mock_context.storage_state = Mock()

            auth_manager.save_state(mock_context)

            assert storage_path.parent.exists()
            mock_context.storage_state.assert_called_once_with(path=str(storage_path))

    def test_save_state_calls_context_method(self):
        """Test that save_state properly calls context.storage_state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "auth.json"
            auth_manager = AuthManager(storage_path)

            mock_context = Mock()
            auth_manager.save_state(mock_context)

            mock_context.storage_state.assert_called_once_with(path=str(storage_path))

    def test_load_state_returns_false_when_file_missing(self):
        """Test that load_state returns False when storage file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "nonexistent.json"
            auth_manager = AuthManager(storage_path)

            mock_context = Mock()
            result = auth_manager.load_state(mock_context)

            assert result is False
            mock_context.add_cookies.assert_not_called()

    def test_load_state_loads_cookies_successfully(self):
        """Test that load_state successfully loads cookies from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "auth.json"
            auth_data = {
                "cookies": [
                    {"name": "session", "value": "abc123", "domain": ".example.com"},
                    {"name": "user_id", "value": "42", "domain": ".example.com"},
                ],
                "origins": [],
            }
            storage_path.write_text(json.dumps(auth_data))

            auth_manager = AuthManager(storage_path)
            mock_context = Mock()

            result = auth_manager.load_state(mock_context)

            assert result is True
            mock_context.add_cookies.assert_called_once_with(auth_data["cookies"])

    def test_load_state_handles_invalid_json(self):
        """Test that load_state handles corrupted JSON gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "bad.json"
            storage_path.write_text("invalid json {{{")

            auth_manager = AuthManager(storage_path)
            mock_context = Mock()

            result = auth_manager.load_state(mock_context)

            assert result is False

    def test_is_authenticated_returns_true_when_element_found(self):
        """Test is_authenticated returns True when indicator element is present."""
        auth_manager = AuthManager("auth.json")
        mock_page = Mock()
        mock_element = MagicMock()
        mock_page.wait_for_selector.return_value = mock_element

        result = auth_manager.is_authenticated(mock_page, "#user-avatar")

        assert result is True
        mock_page.wait_for_selector.assert_called_once_with(
            "#user-avatar", timeout=5000, state="visible"
        )

    def test_is_authenticated_returns_false_when_element_not_found(self):
        """Test is_authenticated returns False when indicator element is missing."""
        auth_manager = AuthManager("auth.json")
        mock_page = Mock()
        mock_page.wait_for_selector.side_effect = Exception("Timeout")

        result = auth_manager.is_authenticated(mock_page, ".profile-icon")

        assert result is False

    def test_is_authenticated_with_custom_timeout(self):
        """Test is_authenticated respects custom timeout parameter."""
        auth_manager = AuthManager("auth.json")
        mock_page = Mock()
        mock_page.wait_for_selector.return_value = MagicMock()

        auth_manager.is_authenticated(mock_page, ".user-menu", timeout=10000)

        mock_page.wait_for_selector.assert_called_once_with(
            ".user-menu", timeout=10000, state="visible"
        )

    def test_clear_state_removes_existing_file(self):
        """Test that clear_state removes the auth state file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "auth.json"
            storage_path.write_text('{"cookies": []}')

            auth_manager = AuthManager(storage_path)
            result = auth_manager.clear_state()

            assert result is True
            assert not storage_path.exists()

    def test_clear_state_returns_false_when_file_missing(self):
        """Test that clear_state returns False when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "nonexistent.json"
            auth_manager = AuthManager(storage_path)

            result = auth_manager.clear_state()

            assert result is False

    def test_state_exists_returns_true_when_file_present(self):
        """Test state_exists returns True when file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "auth.json"
            storage_path.write_text('{"cookies": []}')

            auth_manager = AuthManager(storage_path)

            assert auth_manager.state_exists() is True

    def test_state_exists_returns_false_when_file_missing(self):
        """Test state_exists returns False when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "missing.json"
            auth_manager = AuthManager(storage_path)

            assert auth_manager.state_exists() is False
