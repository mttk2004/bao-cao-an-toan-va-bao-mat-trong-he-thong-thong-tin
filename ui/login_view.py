import flet as ft
import re

class LoginView(ft.View):
    def __init__(self, page, on_login, on_create_vault):
        super().__init__(route="/login")
        self.page = page
        self.on_login = on_login
        self.on_create_vault = on_create_vault

        # --- Modern Color Scheme ---
        self.primary_color = "#6366f1"  # Indigo
        self.secondary_color = "#ec4899"  # Pink
        self.surface_color = ft.Colors.with_opacity(0.1, "white")
        self.text_primary = "#1f2937"
        self.text_secondary = "#6b7280"

        # --- UI Controls ---
        self.app_logo = ft.Icon(
            ft.Icons.SECURITY,
            size=48,
            color=self.primary_color
        )

        self.app_title = ft.Text(
            "AuraCrypt",
            size=36,
            weight=ft.FontWeight.BOLD,
            color=self.primary_color,
            text_align=ft.TextAlign.CENTER
        )

        self.subtitle = ft.Text(
            "Secure Password Manager",
            size=16,
            color=self.text_secondary,
            text_align=ft.TextAlign.CENTER
        )

        self.title = ft.Text(
            "Unlock Vault",
            size=24,
            weight=ft.FontWeight.W_600,
            color=self.text_primary,
            text_align=ft.TextAlign.CENTER
        )

        self.password_field = ft.TextField(
            label="Master Password",
            password=True,
            can_reveal_password=True,
            on_submit=self._handle_submit,
            on_change=self._validate_fields,
            border_radius=12,
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.05, "black"),
            border_color=ft.Colors.with_opacity(0.2, "grey"),
            focused_border_color=self.primary_color,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            height=60,
            text_size=16,
            label_style=ft.TextStyle(color=self.text_secondary),
            cursor_color=self.primary_color
        )

        self.confirm_password_field = ft.TextField(
            label="Confirm Master Password",
            password=True,
            can_reveal_password=True,
            visible=False, # Hidden by default, shown in create mode
            on_submit=self._handle_submit,
            on_change=self._validate_fields,
            border_radius=12,
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.05, "black"),
            border_color=ft.Colors.with_opacity(0.2, "grey"),
            focused_border_color=self.primary_color,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            height=60,
            text_size=16,
            label_style=ft.TextStyle(color=self.text_secondary),
            cursor_color=self.primary_color
        )

        self.strength_indicator = ft.ProgressBar(
            value=0,
            width=300,
            height=8,
            border_radius=4,
            bgcolor=ft.Colors.with_opacity(0.1, "grey")
        )
        self.strength_text = ft.Text(
            "",
            size=14,
            weight=ft.FontWeight.W_500
        )

        self.login_button = ft.Container(
            content=ft.ElevatedButton(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.LOCK_OPEN, size=20),
                        ft.Text("Unlock Vault", size=16, weight=ft.FontWeight.W_600)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8
                ),
                on_click=self._handle_login,
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=self.primary_color,
                    elevation={"": 2, "hovered": 4, "pressed": 1},
                    animation_duration=200,
                    shape=ft.RoundedRectangleBorder(radius=12),
                    padding=ft.Padding(20, 16, 20, 16)
                ),
                expand=True,
                height=56
            ),
            visible=False,
            margin=ft.Margin(0, 10, 0, 0)
        )

        self.create_button = ft.Container(
            content=ft.ElevatedButton(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, size=20),
                        ft.Text("Create New Vault", size=16, weight=ft.FontWeight.W_600)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8
                ),
                on_click=self._handle_create_vault,
                disabled=True,
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=self.secondary_color,
                    elevation={"": 2, "hovered": 4, "pressed": 1},
                    animation_duration=200,
                    shape=ft.RoundedRectangleBorder(radius=12),
                    padding=ft.Padding(20, 16, 20, 16)
                ),
                expand=True,
                height=56
            ),
            visible=False,
            margin=ft.Margin(0, 10, 0, 0)
        )

        # --- Loading Indicator ---
        self.loading_indicator = ft.ProgressRing(
            visible=False,
            color=self.primary_color,
            width=40,
            height=40
        )
        self.loading_text = ft.Text(
            "Please wait...",
            size=14,
            color=self.text_secondary,
            visible=False
        )
        self.loading_overlay = ft.Container(
            content=ft.Column(
                [
                    self.loading_indicator,
                    self.loading_text
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16
            ),
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(0.8, "white"),
            visible=False,
            border_radius=12
        )

        self.strength_container = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.SECURITY, size=16, color=self.text_secondary),
                            self.strength_text
                        ],
                        spacing=8,
                        alignment=ft.MainAxisAlignment.START
                    ),
                    self.strength_indicator
                ],
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
            visible=False,
            padding=ft.Padding(0, 10, 0, 0)
        )

        # --- Header Section ---
        self.header_section = ft.Column(
            [
                self.app_logo,
                self.app_title,
                self.subtitle,
                ft.Container(height=20),  # Spacer
                self.title
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8
        )

        # --- Form Section ---
        self.form_section = ft.Column(
            [
                self.password_field,
                self.confirm_password_field,
                self.strength_container,
                self.login_button,
                self.create_button
            ],
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # --- Main Content Card ---
        self.main_card = ft.Container(
            content=ft.Column(
                [
                    self.header_section,
                    ft.Container(height=20),  # Spacer
                    self.form_section
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0
            ),
            width=450,
            padding=ft.Padding(40, 40, 40, 40),
            bgcolor=ft.Colors.with_opacity(0.95, "white"),
            border_radius=20,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=25,
                color=ft.Colors.with_opacity(0.1, "black"),
                offset=ft.Offset(0, 8)
            ),
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, "grey"))
        )

        # --- Background with Gradient ---
        self.background = ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[
                    "#667eea",  # Light blue
                    "#764ba2",  # Purple
                    "#f093fb",  # Light pink
                    "#f5576c"   # Pink-red
                ]
            )
        )

        # Use a surrounding Container to perfectly center the main_card on the page
        self.view_content = ft.Container(
            content=self.main_card,
            alignment=ft.alignment.center,
            expand=True,
            padding=ft.Padding(20, 20, 20, 20)
        )

        self.controls = [
            ft.Stack(
                [
                    self.background,
                    self.view_content,
                    self.loading_overlay,
                ],
                expand=True
            )
        ]

    def set_mode(self, vault_exists: bool):
        """Set the view mode based on whether a vault exists."""
        is_create_mode = not vault_exists

        # Update title with animation-like effect
        if vault_exists:
            self.title.value = "Welcome Back"
            self.subtitle.value = "Enter your master password to unlock"
        else:
            self.title.value = "Create Your Vault"
            self.subtitle.value = "Set up a secure master password"

        self.login_button.visible = vault_exists
        self.create_button.visible = is_create_mode

        self.confirm_password_field.visible = is_create_mode
        self.strength_container.visible = is_create_mode

        # Reset fields when mode changes
        self.password_field.value = ""
        self.confirm_password_field.value = ""
        self.password_field.error_text = None
        self.confirm_password_field.error_text = None

        # Reset strength indicator
        if is_create_mode:
            self.strength_indicator.value = 0
            self.strength_text.value = ""

        self._validate_fields() # Update button states
        if self.page:
            self.page.update()

    def _handle_submit(self, e):
        """Handle enter key press."""
        if self.login_button.visible and not self.login_button.content.disabled:
            self._handle_login(e)
        elif self.create_button.visible and not self.create_button.content.disabled:
            self._handle_create_vault(e)

    def _show_loading(self, show: bool, message: str = "Please wait..."):
        """Shows or hides the loading indicator and disables/enables the main content."""
        self.loading_overlay.visible = show
        self.loading_indicator.visible = show
        self.loading_text.visible = show
        self.loading_text.value = message
        self.view_content.disabled = show

        # Disable buttons during loading
        if hasattr(self.login_button.content, 'disabled'):
            self.login_button.content.disabled = show
        if hasattr(self.create_button.content, 'disabled') and not show:
            # Only re-enable create button if validation passes
            self._validate_fields()
        elif hasattr(self.create_button.content, 'disabled'):
            self.create_button.content.disabled = show

        if self.page:
            self.page.update()

    def _handle_login(self, e):
        password = self.password_field.value
        if not password:
            self._show_error("Password cannot be empty")
            return

        self._show_loading(True, "Unlocking your vault...")
        # The actual on_login call is now expected to hide the loading indicator
        self.on_login(password)

    def _handle_create_vault(self, e):
        if not self.create_button.content.disabled:
            self._show_loading(True, "Creating your secure vault...")
            # The on_create_vault call is now expected to hide the loading indicator
            self.on_create_vault(self.password_field.value)

    def _show_error(self, message: str):
        """Show error message with modern styling."""
        self.password_field.error_text = message
        self.password_field.border_color = ft.Colors.RED_400
        if self.page:
            self.page.update()

    def hide_loading(self):
        """Public method to allow the controller to hide the loading indicator."""
        self._show_loading(False)

    def _validate_fields(self, e=None):
        """
        Validates the input fields for both login and create modes and updates the UI accordingly.
        This includes checking password strength and matching passwords.
        """
        # --- Create Mode Validation ---
        if self.create_button.visible:
            password = self.password_field.value
            confirm_password = self.confirm_password_field.value

            # Update strength indicator with modern styling
            strength, value, color = self.get_password_strength(password)
            self.strength_text.value = f"{strength}"
            self.strength_text.color = color
            self.strength_indicator.value = value
            self.strength_indicator.color = color

            # Check if passwords match with better UX
            if password and confirm_password:
                if password != confirm_password:
                    self.confirm_password_field.error_text = "Passwords do not match"
                    self.confirm_password_field.border_color = ft.Colors.RED_400
                else:
                    self.confirm_password_field.error_text = ""
                    self.confirm_password_field.border_color = ft.Colors.GREEN_400
            else:
                self.confirm_password_field.error_text = ""
                self.confirm_password_field.border_color = ft.Colors.with_opacity(0.2, "grey")

            # Enable/disable create button
            can_create = (
                strength != "Weak" and
                password == confirm_password and
                bool(password) and # Ensure password is not empty
                len(password) >= 8
            )
            self.create_button.content.disabled = not can_create

        # --- General Validation (clearing errors on input) ---
        if self.password_field.error_text and self.password_field.value:
            self.password_field.error_text = ""
            self.password_field.border_color = ft.Colors.with_opacity(0.2, "grey")

        if self.page:
            self.page.update()

    def get_password_strength(self, password: str) -> tuple[str, float, str]:
        """Returns a tuple of (strength_name, progress_value, color) with modern color scheme."""
        if not password:
            return "Enter password", 0.0, self.text_secondary

        length = len(password)
        score = 0

        # Check for different character types
        if re.search(r"[a-z]", password): score += 1
        if re.search(r"[A-Z]", password): score += 1
        if re.search(r"\d", password): score += 1
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): score += 1

        # Enhanced scoring logic with modern colors
        if length < 6:
            return "Too Short", 0.2, "#ef4444"  # Red-500
        elif length < 8:
            return "Weak", 0.35, "#f97316"  # Orange-500
        elif length >= 12 and score >= 4:
            return "Excellent", 1.0, "#22c55e"  # Green-500
        elif length >= 10 and score >= 3:
            return "Strong", 0.8, "#16a34a"  # Green-600
        elif length >= 8 and score >= 2:
            return "Good", 0.6, "#eab308"  # Yellow-500
        else:
            return "Fair", 0.4, "#f59e0b"  # Amber-500
