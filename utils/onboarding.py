# auracrypt2/utils/onboarding.py
"""
Onboarding tour system for new users.
Provides step-by-step guidance through AuraCrypt features.
"""

import flet as ft
from typing import List, Dict, Callable, Optional
from core.constants import AppConstants, UIMessages


class OnboardingStep:
    """Represents a single step in the onboarding tour."""

    def __init__(
        self,
        title: str,
        message: str,
        target_element: Optional[str] = None,
        action: Optional[str] = None,
        highlight_color: str = AppConstants.PRIMARY_COLOR
    ):
        self.title = title
        self.message = message
        self.target_element = target_element
        self.action = action
        self.highlight_color = highlight_color


class OnboardingManager:
    """Manages the onboarding experience for new users."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.current_step = 0
        self.is_active = False
        self.overlay_container: Optional[ft.Container] = None
        self.steps: List[OnboardingStep] = []
        self.on_complete: Optional[Callable] = None
        self.on_skip: Optional[Callable] = None

        self._initialize_steps()

    def _initialize_steps(self):
        """Initialize the onboarding steps."""
        self.steps = [
            OnboardingStep(
                title="Welcome to AuraCrypt! 🔐",
                message="AuraCrypt is your secure password manager. Let's take a quick tour to get you started!",
                action="next"
            ),
            OnboardingStep(
                title="Your Vault is Secure 🛡️",
                message="Your passwords are encrypted with AES-256-GCM encryption. Only you have the key to decrypt them with your master password.",
                action="next"
            ),
            OnboardingStep(
                title="Add Your First Entry 📝",
                message="Click the 'Add New' button to create your first password entry. You can store website logins, app passwords, and more!",
                target_element="add_button",
                action="highlight"
            ),
            OnboardingStep(
                title="Organize with Categories 📁",
                message="Keep your passwords organized by using categories like 'Work', 'Personal', 'Finance', etc. Click on categories to filter your entries.",
                target_element="categories_section",
                action="highlight"
            ),
            OnboardingStep(
                title="Search Your Passwords 🔍",
                message="Use the search bar to quickly find any password entry by service name, username, or URL.",
                target_element="search_bar",
                action="highlight"
            ),
            OnboardingStep(
                title="Quick Actions ⚡",
                message="Once you select an entry, you can edit it, copy the password to your clipboard, or delete it using the action buttons.",
                target_element="action_buttons",
                action="highlight"
            ),
            OnboardingStep(
                title="Stay Secure 🔒",
                message="Your vault automatically locks after 15 minutes of inactivity. You can also lock it manually using the 'Lock Vault' button.",
                target_element="lock_button",
                action="highlight"
            ),
            OnboardingStep(
                title="You're All Set! 🎉",
                message="That's it! You're ready to use AuraCrypt. Remember to use a strong master password and never share it with anyone.",
                action="complete"
            )
        ]

    def start_tour(self, on_complete: Optional[Callable] = None, on_skip: Optional[Callable] = None):
        """
        Start the onboarding tour.

        Args:
            on_complete: Callback when tour is completed
            on_skip: Callback when tour is skipped
        """
        self.on_complete = on_complete
        self.on_skip = on_skip
        self.current_step = 0
        self.is_active = True
        self._show_current_step()

    def next_step(self):
        """Move to the next step in the tour."""
        if not self.is_active:
            return

        self.current_step += 1
        if self.current_step >= len(self.steps):
            self._complete_tour()
        else:
            self._show_current_step()

    def previous_step(self):
        """Move to the previous step in the tour."""
        if not self.is_active or self.current_step <= 0:
            return

        self.current_step -= 1
        self._show_current_step()

    def skip_tour(self):
        """Skip the entire tour."""
        if not self.is_active:
            return

        self._hide_overlay()
        self.is_active = False

        if self.on_skip:
            self.on_skip()

    def _show_current_step(self):
        """Show the current step of the tour."""
        if not self.is_active or self.current_step >= len(self.steps):
            return

        step = self.steps[self.current_step]
        self._show_step_overlay(step)

    def _show_step_overlay(self, step: OnboardingStep):
        """
        Show the overlay for a specific step.

        Args:
            step: The onboarding step to show
        """
        # Remove existing overlay
        self._hide_overlay()

        # Create progress indicator
        progress = (self.current_step + 1) / len(self.steps)
        progress_bar = ft.ProgressBar(
            value=progress,
            bgcolor=ft.Colors.with_opacity(0.2, AppConstants.PRIMARY_COLOR),
            color=AppConstants.PRIMARY_COLOR,
            height=4
        )

        # Create step counter
        step_counter = ft.Text(
            f"Step {self.current_step + 1} of {len(self.steps)}",
            size=12,
            color=AppConstants.TEXT_SECONDARY,
            weight=ft.FontWeight.W_500
        )

        # Create action buttons
        action_buttons = []

        if self.current_step > 0:
            action_buttons.append(
                ft.TextButton(
                    "Previous",
                    on_click=lambda e: self.previous_step(),
                    style=ft.ButtonStyle(
                        color=AppConstants.TEXT_SECONDARY
                    )
                )
            )

        action_buttons.append(
            ft.TextButton(
                "Skip Tour",
                on_click=lambda e: self.skip_tour(),
                style=ft.ButtonStyle(
                    color=AppConstants.TEXT_SECONDARY
                )
            )
        )

        if step.action == "complete":
            action_buttons.append(
                ft.ElevatedButton(
                    "Get Started!",
                    on_click=lambda e: self._complete_tour(),
                    style=ft.ButtonStyle(
                        bgcolor=AppConstants.PRIMARY_COLOR,
                        color=AppConstants.WHITE_COLOR
                    )
                )
            )
        else:
            action_buttons.append(
                ft.ElevatedButton(
                    "Next",
                    on_click=lambda e: self.next_step(),
                    style=ft.ButtonStyle(
                        bgcolor=AppConstants.PRIMARY_COLOR,
                        color=AppConstants.WHITE_COLOR
                    )
                )
            )

        # Create content card
        content_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    step_counter,
                    progress_bar,
                    ft.Divider(height=1, color=AppConstants.TEXT_SECONDARY),
                    ft.Text(
                        step.title,
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=AppConstants.TEXT_PRIMARY
                    ),
                    ft.Text(
                        step.message,
                        size=14,
                        color=AppConstants.TEXT_SECONDARY
                    ),
                    ft.Row(
                        action_buttons,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    )
                ],
                spacing=16),
                padding=24,
                width=400
            ),
            elevation=8
        )

        # Create overlay container
        self.overlay_container = ft.Container(
            content=ft.Stack([
                # Semi-transparent background
                ft.Container(
                    bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLACK),
                    expand=True,
                    on_click=lambda e: None  # Prevent clicks through overlay
                ),
                # Content card positioned in center
                ft.Container(
                    content=content_card,
                    alignment=ft.alignment.center,
                    expand=True
                )
            ]),
            expand=True
        )

        # Add overlay to page
        self.page.overlay.append(self.overlay_container)
        self.page.update()

    def _hide_overlay(self):
        """Hide the current overlay."""
        if self.overlay_container and self.overlay_container in self.page.overlay:
            self.page.overlay.remove(self.overlay_container)
            self.overlay_container = None
            self.page.update()

    def _complete_tour(self):
        """Complete the onboarding tour."""
        self._hide_overlay()
        self.is_active = False

        if self.on_complete:
            self.on_complete()

    def create_tooltip(self, element: ft.Control, message: str, show_delay: int = 1000) -> ft.Tooltip:
        """
        Create a tooltip for an element.

        Args:
            element: The UI element to attach tooltip to
            message: Tooltip message
            show_delay: Delay before showing tooltip (ms)

        Returns:
            Tooltip control
        """
        return ft.Tooltip(
            message=message,
            wait_duration=show_delay,
            text_style=ft.TextStyle(
                size=12,
                color=AppConstants.WHITE_COLOR
            ),
            bgcolor=AppConstants.TEXT_PRIMARY,
            border_radius=8,
            padding=8
        )


class FirstTimeSetup:
    """Handles first-time setup experience."""

    def __init__(self, page: ft.Page):
        self.page = page

    def should_show_onboarding(self) -> bool:
        """
        Check if onboarding should be shown.
        This could check for a settings file or user preference.

        Returns:
            True if onboarding should be shown
        """
        # For now, we'll show onboarding when vault is first created
        # In a real app, you might store this in settings
        return True

    def mark_onboarding_complete(self):
        """Mark onboarding as completed so it doesn't show again."""
        # In a real app, you would save this to settings
        pass

    def show_welcome_dialog(self, on_start_tour: Callable, on_skip: Callable):
        """
        Show initial welcome dialog.

        Args:
            on_start_tour: Callback to start the tour
            on_skip: Callback to skip the tour
        """
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Welcome to AuraCrypt! 🎉"),
            content=ft.Column([
                ft.Text(
                    "Welcome to your new secure password manager!",
                    size=16,
                    weight=ft.FontWeight.W_500
                ),
                ft.Text(
                    "Would you like to take a quick tour to learn about the main features?",
                    size=14,
                    color=AppConstants.TEXT_SECONDARY
                ),
                ft.Text(
                    "The tour takes about 2 minutes and will help you get started.",
                    size=12,
                    color=AppConstants.TEXT_SECONDARY
                )
            ],
            spacing=12,
            height=120),
            actions=[
                ft.TextButton(
                    "Skip for now",
                    on_click=lambda e: self._close_welcome_dialog(dialog, on_skip)
                ),
                ft.ElevatedButton(
                    "Start Tour",
                    on_click=lambda e: self._close_welcome_dialog(dialog, on_start_tour),
                    style=ft.ButtonStyle(
                        bgcolor=AppConstants.PRIMARY_COLOR,
                        color=AppConstants.WHITE_COLOR
                    )
                )
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _close_welcome_dialog(self, dialog: ft.AlertDialog, callback: Callable):
        """Close the welcome dialog and call the callback."""
        dialog.open = False
        self.page.update()
        callback()
