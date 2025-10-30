# auracrypt2/utils/app_types.py
"""
Type definitions and interfaces for AuraCrypt application.
"""

from typing import TypedDict, Optional, Literal, Protocol, Callable, Any
from datetime import datetime


class EntryData(TypedDict):
    """Type definition for password entry data."""
    id: str
    service: str
    username: str
    password: str
    url: Optional[str]
    notes: Optional[str]
    category: str
    created_at: str
    updated_at: str


class VaultData(TypedDict):
    """Type definition for vault data structure."""
    entries: list[EntryData]
    categories: list[str]
    settings: Optional[dict[str, Any]]


class CategoryData(TypedDict):
    """Type definition for category information."""
    name: str
    count: int
    color: Optional[str]


class ValidationResult(TypedDict):
    """Type definition for validation results."""
    is_valid: bool
    error_message: str


class PasswordStrengthResult(TypedDict):
    """Type definition for password strength analysis."""
    score: int
    strength: Literal["Weak", "Fair", "Good", "Strong", "Excellent"]
    feedback: list[str]
    estimated_crack_time: str


class SearchFilters(TypedDict, total=False):
    """Type definition for search filters (all optional)."""
    query: str
    category: str
    has_url: bool
    has_notes: bool
    created_after: str
    created_before: str


class UITheme(TypedDict):
    """Type definition for UI theme configuration."""
    name: str
    primary_color: str
    secondary_color: str
    success_color: str
    warning_color: str
    danger_color: str
    text_primary: str
    text_secondary: str
    background: str
    surface: str


# Protocol definitions for better type safety
class PageProtocol(Protocol):
    """Protocol for Flet page objects."""
    def update(self) -> None: ...
    def set_clipboard(self, value: str) -> None: ...
    def launch_url(self, url: str) -> None: ...
    def go(self, route: str) -> None: ...


class ViewProtocol(Protocol):
    """Protocol for view objects."""
    def update(self) -> None: ...


class CallbackProtocol(Protocol):
    """Protocol for callback functions."""
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


# Type aliases for better readability
EntryList = list[EntryData]
CategoryList = list[str]
EntryID = str
CategoryName = str
ServiceName = str

# Callback type definitions
OnSaveCallback = Callable[[EntryData], None]
OnDeleteCallback = Callable[[EntryData], None]
OnCancelCallback = Callable[[], None]
OnCategoryCallback = Callable[[CategoryName], None]
OnSearchCallback = Callable[[str], None]

# Event handler types
ClickHandler = Callable[[Any], None]
ChangeHandler = Callable[[Any], None]
SubmitHandler = Callable[[Any], None]
