# auracrypt2/core/constants.py
"""
Constants used throughout the AuraCrypt application.
This file centralizes all configuration values and magic numbers.
"""

class AppConstants:
    """Application-wide constants."""

    # Application Information
    APP_TITLE = "AuraCrypt"
    APP_VERSION = "2.0.0"

    # UI Color Constants
    PRIMARY_COLOR = "#6366f1"      # Indigo-500
    SECONDARY_COLOR = "#ec4899"    # Pink-500
    SUCCESS_COLOR = "#22c55e"      # Green-500
    WARNING_COLOR = "#f59e0b"      # Amber-500
    DANGER_COLOR = "#ef4444"       # Red-500
    ERROR_COLOR = "#ef4444"        # Same as danger for consistency
    TEXT_PRIMARY = "#1f2937"       # Gray-800
    TEXT_SECONDARY = "#6b7280"     # Gray-500
    BACKGROUND_LIGHT = "#f8fafc"   # Slate-50
    WHITE_COLOR = "#ffffff"        # White
    ACCENT_COLOR = "#fde047"       # Yellow-300

    # Security Constants
    AUTO_LOCK_TIMEOUT = 15 * 60    # 15 minutes in seconds
    AUTO_LOCK_CHECK_INTERVAL = 30  # Check every 30 seconds
    MIN_PASSWORD_LENGTH = 8        # Minimum required password length
    MAX_CATEGORY_LENGTH = 50       # Maximum category name length
    MAX_SERVICE_NAME_LENGTH = 100  # Maximum service name length
    PASSWORD_GENERATOR_DEFAULT_LENGTH = 16
    CLIPBOARD_CLEAR_DELAY = 30     # Clear clipboard after 30 seconds

    # Crypto Constants
    SALT_SIZE = 16                 # Size of salt in bytes
    KEY_SIZE = 32                  # AES-256 key size
    PBKDF2_ITERATIONS = 480_000    # PBKDF2 iterations (OWASP 2023)
    AES_NONCE_SIZE = 12            # AES-GCM nonce size

    # File Constants
    VAULT_FILE = "vault.dat"
    CORRUPTED_VAULT_FILE = f"{VAULT_FILE}.corrupted"
    BACKUP_DIR = "backups"

    # UI Layout Constants
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 700
    BORDER_RADIUS = 12
    CARD_BORDER_RADIUS = 16
    BUTTON_HEIGHT = 44
    SMALL_BUTTON_HEIGHT = 36
    TEXT_FIELD_HEIGHT = 56

    # Search and Pagination
    SEARCH_DEBOUNCE_DELAY = 0.3    # Delay before executing search
    MAX_RECENT_ENTRIES = 5         # Number of recent entries to remember
    ENTRIES_PER_PAGE = 20          # For lazy loading

    # Notification Durations (milliseconds)
    SNACK_DURATION = 3000          # 3 seconds
    COPY_FEEDBACK_DURATION = 2000  # 2 seconds
    UNDO_DURATION = 6000           # 6 seconds

    # Default Categories
    DEFAULT_CATEGORIES = [
        "Personal",
        "Work",
        "Social",
        "Finance",
        "Shopping",
        "Entertainment"
    ]
    DEFAULT_CATEGORY = "Uncategorized"

class UIMessages:
    """User interface messages and text constants."""

    # Error Messages
    ERROR_VAULT_NOT_FOUND = "Vault file not found."
    ERROR_WRONG_PASSWORD = "Decryption failed. Master password may be incorrect or data is corrupt."
    ERROR_SERVICE_REQUIRED = "Service name is required"
    ERROR_PASSWORD_REQUIRED = "Password is required"
    ERROR_CATEGORY_EMPTY = "Category name cannot be empty"
    ERROR_CATEGORY_EXISTS = "Category already exists"
    ERROR_CATEGORY_TOO_LONG = f"Category name must be {AppConstants.MAX_CATEGORY_LENGTH} characters or less"

    # Success Messages
    ENTRY_ADDED_SUCCESS = "added successfully"
    ENTRY_UPDATED_SUCCESS = "updated successfully"
    ENTRY_DELETED = "deleted"
    ENTRY_RESTORED = "restored"
    SUCCESS_CATEGORY_ADDED = "Category added successfully"
    SUCCESS_CATEGORY_RENAMED = "Category renamed successfully"
    SUCCESS_CATEGORY_DELETED = "Category deleted"
    VAULT_CREATED_SUCCESS = "Vault created successfully! You can now log in."
    PASSWORD_COPIED = "Password copied for"

    # Error Messages
    ERROR_CREATING_VAULT = "Error creating vault"
    ERROR_SAVING_VAULT = "Failed to save vault"
    UNKNOWN_SERVICE = "Unknown"

    # UI Buttons and Actions
    UNDO_BUTTON = "UNDO"

    # UI Labels
    LABEL_SERVICE_NAME = "Service Name"
    LABEL_USERNAME = "Username/Email"
    LABEL_PASSWORD = "Password"
    LABEL_URL = "URL (optional)"
    LABEL_NOTES = "Notes (optional)"
    LABEL_CATEGORY = "Category"
    LABEL_MASTER_PASSWORD = "Master Password"
    LABEL_CONFIRM_PASSWORD = "Confirm Master Password"

    # Tooltips
    TOOLTIP_ADD_ENTRY = "Add new password entry"
    TOOLTIP_EDIT_ENTRY = "Edit selected entry"
    TOOLTIP_DELETE_ENTRY = "Delete selected entry"
    TOOLTIP_COPY_PASSWORD = "Copy password to clipboard"
    TOOLTIP_LOCK_VAULT = "Lock and secure vault"
    TOOLTIP_MANAGE_CATEGORIES = "Manage Categories"
    TOOLTIP_GENERATE_PASSWORD = "Generate a secure password"
    TOOLTIP_SHOW_PASSWORD = "Show password"
    TOOLTIP_HIDE_PASSWORD = "Hide password"
