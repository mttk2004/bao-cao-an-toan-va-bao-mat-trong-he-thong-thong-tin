# auracrypt2/utils/validators.py
"""
Validation utilities for AuraCrypt application data.
"""

import re
from typing import Tuple
from core.constants import AppConstants, UIMessages
from utils.helpers import validate_url, is_strong_password
from utils.app_types import EntryData, ValidationResult


class EntryValidator:
    """Validator class for password entry data."""

    @staticmethod
    def validate_service_name(service: str) -> Tuple[bool, str]:
        """
        Validate service name field.

        Args:
            service: Service name to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not service or not service.strip():
            return False, UIMessages.ERROR_SERVICE_REQUIRED

        service = service.strip()

        if len(service) > AppConstants.MAX_SERVICE_NAME_LENGTH:
            return False, f"Service name must be {AppConstants.MAX_SERVICE_NAME_LENGTH} characters or less"

        # Check for potentially dangerous characters
        if re.search(r'[\x00-\x1f\x7f-\x9f]', service):
            return False, "Service name contains invalid characters"

        return True, ""

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Validate password field.

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, UIMessages.ERROR_PASSWORD_REQUIRED

        if len(password) < AppConstants.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {AppConstants.MIN_PASSWORD_LENGTH} characters"

        # Additional security checks
        is_strong, issues = is_strong_password(password)
        if not is_strong and len(issues) > 2:
            return False, f"Password is too weak: {', '.join(issues[:2])}"

        return True, ""

    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """
        Validate username/email field.

        Args:
            username: Username to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Username is optional, so empty is valid
        if not username:
            return True, ""

        username = username.strip()

        if len(username) > 255:
            return False, "Username must be 255 characters or less"

        # Basic email validation if it looks like an email
        if "@" in username:
            email_pattern = re.compile(
                r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            )
            if not email_pattern.match(username):
                return False, "Invalid email format"

        return True, ""

    @staticmethod
    def validate_url_field(url: str) -> Tuple[bool, str]:
        """
        Validate URL field.

        Args:
            url: URL to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not url:
            return True, ""  # URL is optional

        is_valid, cleaned_url = validate_url(url)
        if not is_valid:
            return False, "Invalid URL format"

        return True, ""

    @staticmethod
    def validate_notes(notes: str) -> Tuple[bool, str]:
        """
        Validate notes field.

        Args:
            notes: Notes to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Notes are optional and can be any text
        if not notes:
            return True, ""

        if len(notes) > 2000:
            return False, "Notes must be 2000 characters or less"

        return True, ""

    @staticmethod
    def validate_entry_data(entry_data: dict) -> ValidationResult:
        """
        Validate complete entry data.

        Args:
            entry_data: Dictionary containing entry data

        Returns:
            ValidationResult with is_valid and error_message
        """
        # Validate service name
        is_valid, error = EntryValidator.validate_service_name(
            entry_data.get('service', '')
        )
        if not is_valid:
            return ValidationResult(is_valid=False, error_message=error)

        # Validate password
        is_valid, error = EntryValidator.validate_password(
            entry_data.get('password', '')
        )
        if not is_valid:
            return ValidationResult(is_valid=False, error_message=error)

        # Validate username
        is_valid, error = EntryValidator.validate_username(
            entry_data.get('username', '')
        )
        if not is_valid:
            return ValidationResult(is_valid=False, error_message=error)

        # Validate URL
        is_valid, error = EntryValidator.validate_url_field(
            entry_data.get('url', '')
        )
        if not is_valid:
            return ValidationResult(is_valid=False, error_message=error)

        # Validate notes
        is_valid, error = EntryValidator.validate_notes(
            entry_data.get('notes', '')
        )
        if not is_valid:
            return ValidationResult(is_valid=False, error_message=error)

        return ValidationResult(is_valid=True, error_message="")


class CategoryValidator:
    """Validator class for category data."""

    @staticmethod
    def validate_category_name(category_name: str) -> Tuple[bool, str]:
        """
        Validate category name.

        Args:
            category_name: Category name to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not category_name or not category_name.strip():
            return False, UIMessages.ERROR_CATEGORY_EMPTY

        category_name = category_name.strip()

        if len(category_name) > AppConstants.MAX_CATEGORY_LENGTH:
            return False, UIMessages.ERROR_CATEGORY_TOO_LONG

        # Check for reserved category name
        if category_name == AppConstants.DEFAULT_CATEGORY:
            return False, f"'{AppConstants.DEFAULT_CATEGORY}' is a reserved category name"

        # Check for valid characters (letters, numbers, spaces, hyphens, underscores)
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', category_name):
            return False, "Category name can only contain letters, numbers, spaces, hyphens, and underscores"

        return True, ""

    @staticmethod
    def validate_category_rename(
        old_name: str,
        new_name: str,
        existing_categories: list[str]
    ) -> Tuple[bool, str]:
        """
        Validate category rename operation.

        Args:
            old_name: Current category name
            new_name: New category name
            existing_categories: List of existing category names

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if old category is the default (can't rename)
        if old_name == AppConstants.DEFAULT_CATEGORY:
            return False, f"Cannot rename the '{AppConstants.DEFAULT_CATEGORY}' category"

        # Validate new name
        is_valid, error = CategoryValidator.validate_category_name(new_name)
        if not is_valid:
            return False, error

        # Normalize names for comparison
        from core.categories import CategoryManager
        normalized_old = CategoryManager.normalize_category(old_name)
        normalized_new = CategoryManager.normalize_category(new_name)

        # Check if new name is same as old name
        if normalized_new == normalized_old:
            return False, "New name is the same as current name"

        # Check if new name already exists
        if normalized_new in existing_categories:
            return False, UIMessages.ERROR_CATEGORY_EXISTS

        return True, ""


class VaultValidator:
    """Validator class for vault operations."""

    @staticmethod
    def validate_master_password(password: str, is_creation: bool = False) -> Tuple[bool, str]:
        """
        Validate master password.

        Args:
            password: Master password to validate
            is_creation: Whether this is for vault creation (stricter validation)

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Master password cannot be empty"

        if is_creation:
            # Stricter validation for new vaults
            if len(password) < 12:
                return False, "Master password should be at least 12 characters for new vaults"

            is_strong, issues = is_strong_password(password)
            if not is_strong:
                return False, f"Master password is too weak: {issues[0]}"
        else:
            # Basic validation for login
            if len(password) < AppConstants.MIN_PASSWORD_LENGTH:
                return False, f"Master password must be at least {AppConstants.MIN_PASSWORD_LENGTH} characters"

        return True, ""

    @staticmethod
    def validate_password_confirmation(password: str, confirm_password: str) -> Tuple[bool, str]:
        """
        Validate password confirmation matches.

        Args:
            password: Original password
            confirm_password: Confirmation password

        Returns:
            Tuple of (is_valid, error_message)
        """
        if password != confirm_password:
            return False, "Passwords do not match"

        return True, ""
