# auracrypt2/ui/entry_view.py

import flet as ft
import random
import string
from typing import List, Optional, Callable
from core.categories import CategoryManager
from core.constants import AppConstants, UIMessages
from utils.smart_suggestions import SmartSuggestions
from utils.app_types import EntryData
from utils.helpers import generate_secure_password

class EntryView(ft.View):
    def __init__(
        self,
        page: ft.Page,
        on_save: Callable,
        on_cancel: Callable,
        on_manage_categories: Callable,
        available_categories: Optional[List[str]] = None
    ):
        super().__init__()
        self.page = page
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.on_manage_categories = on_manage_categories
        self.entry_data: EntryData = {}
        self.available_categories = available_categories or CategoryManager.get_predefined_categories()
        self.existing_entries: List[EntryData] = []  # For smart suggestions

        # --- Form Fields ---
        self.service_field = ft.TextField(
            label=UIMessages.LABEL_SERVICE_NAME,
            prefix_icon=ft.Icons.BUSINESS,
            border_radius=AppConstants.BORDER_RADIUS,
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.05, "black"),
            border_color=ft.Colors.with_opacity(0.2, "grey"),
            focused_border_color=AppConstants.PRIMARY_COLOR,
            height=AppConstants.TEXT_FIELD_HEIGHT,
            text_size=15,
            label_style=ft.TextStyle(color=AppConstants.TEXT_SECONDARY),
            cursor_color=AppConstants.PRIMARY_COLOR,
            on_change=self._on_service_change  # Add smart suggestions
        )

        # --- TRƯỜNG MỚI: DROPDOWN CATEGORY ---
        self.category_dropdown = ft.Dropdown(
            label=UIMessages.LABEL_CATEGORY,
            leading_icon=ft.Icons.FOLDER_OPEN_OUTLINED,
            border_radius=AppConstants.BORDER_RADIUS,
            filled=True,
            fill_color=ft.Colors.with_opacity(0.05, "black"),
            border_color=ft.Colors.with_opacity(0.2, "grey"),
            focused_border_color=AppConstants.PRIMARY_COLOR,
            text_size=15,
            label_style=ft.TextStyle(color=AppConstants.TEXT_SECONDARY),
            enable_filter=True,  # Cho phép lọc danh sách
            enable_search=True,   # Cho phép tìm kiếm
            options=[],  # Sẽ được cập nhật trong _build_category_options()
            value=AppConstants.DEFAULT_CATEGORY,  # Giá trị mặc định
            width=None  # Để tự động điều chỉnh
        )

        # Manage Categories button
        self.manage_categories_button = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.SETTINGS,
                tooltip=UIMessages.TOOLTIP_MANAGE_CATEGORIES,
                on_click=self.on_manage_categories,
                icon_color=AppConstants.WHITE_COLOR,
                bgcolor=AppConstants.TEXT_SECONDARY,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                    elevation={"": 2, "hovered": 4}
                )
            ),
            tooltip=UIMessages.TOOLTIP_MANAGE_CATEGORIES
        )

        self.username_field = ft.TextField(
            label=UIMessages.LABEL_USERNAME,
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            border_radius=AppConstants.BORDER_RADIUS,
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.05, "black"),
            border_color=ft.Colors.with_opacity(0.2, "grey"),
            focused_border_color=AppConstants.PRIMARY_COLOR,
            height=AppConstants.TEXT_FIELD_HEIGHT,
            text_size=15,
            label_style=ft.TextStyle(color=AppConstants.TEXT_SECONDARY),
            cursor_color=AppConstants.PRIMARY_COLOR
        )
        self.password_field = ft.TextField(
            label=UIMessages.LABEL_PASSWORD,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            border_radius=AppConstants.BORDER_RADIUS,
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.05, "black"),
            border_color=ft.Colors.with_opacity(0.2, "grey"),
            focused_border_color=AppConstants.PRIMARY_COLOR,
            height=AppConstants.TEXT_FIELD_HEIGHT,
            text_size=15,
            label_style=ft.TextStyle(color=AppConstants.TEXT_SECONDARY),
            cursor_color=AppConstants.PRIMARY_COLOR,
            expand=True
        )
        self.url_field = ft.TextField(
            label=UIMessages.LABEL_URL,
            prefix_icon=ft.Icons.LINK,
            border_radius=AppConstants.BORDER_RADIUS,
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.05, "black"),
            border_color=ft.Colors.with_opacity(0.2, "grey"),
            focused_border_color=AppConstants.PRIMARY_COLOR,
            height=AppConstants.TEXT_FIELD_HEIGHT,
            text_size=15,
            label_style=ft.TextStyle(color=AppConstants.TEXT_SECONDARY),
            cursor_color=AppConstants.PRIMARY_COLOR
        )
        self.notes_field = ft.TextField(
            label=UIMessages.LABEL_NOTES,
            multiline=True,
            prefix_icon=ft.Icons.NOTES,
            border_radius=AppConstants.BORDER_RADIUS,
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.05, "black"),
            border_color=ft.Colors.with_opacity(0.2, "grey"),
            focused_border_color=AppConstants.PRIMARY_COLOR,
            min_lines=5,
            max_lines=5,
            text_size=15,
            label_style=ft.TextStyle(color=AppConstants.TEXT_SECONDARY),
            cursor_color=AppConstants.PRIMARY_COLOR
        )
        self.generate_password_button = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.AUTO_AWESOME,
                tooltip=UIMessages.TOOLTIP_GENERATE_PASSWORD,
                on_click=self._toggle_generator_visibility,
                icon_color=AppConstants.WHITE_COLOR,
                bgcolor=AppConstants.SECONDARY_COLOR,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                    elevation={"": 2, "hovered": 4}
                )
            ),
            tooltip=UIMessages.TOOLTIP_GENERATE_PASSWORD
        )
        self.length_value = ft.Text("16", size=14, weight=ft.FontWeight.W_600, color=AppConstants.PRIMARY_COLOR)
        self.length_slider = ft.Slider(
            min=8, max=64, divisions=56, value=16,
            active_color=AppConstants.PRIMARY_COLOR,
            inactive_color=ft.Colors.with_opacity(0.2, "grey"),
            thumb_color=AppConstants.PRIMARY_COLOR,
            on_change=lambda e: self._on_length_change(e)
        )
        self.uppercase_check = ft.Checkbox("Uppercase (A-Z)", True, active_color=AppConstants.PRIMARY_COLOR)
        self.lowercase_check = ft.Checkbox("Lowercase (a-z)", True, active_color=AppConstants.PRIMARY_COLOR)
        self.numbers_check = ft.Checkbox("Numbers (0-9)", True, active_color=AppConstants.PRIMARY_COLOR)
        self.symbols_check = ft.Checkbox("Symbols (!@#...)", True, active_color=AppConstants.PRIMARY_COLOR)

        self.generator_container = ft.Container(
            content=ft.Column([
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row([ft.Text("Password Length:", weight=ft.FontWeight.W_500), self.length_value], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.length_slider,
                ft.Row([self.uppercase_check, self.lowercase_check]),
                ft.Row([self.numbers_check, self.symbols_check]),
                ft.ElevatedButton(
                    "Generate and Fill Password",
                    icon=ft.Icons.REFRESH,
                    on_click=self._generate_and_fill_password,
                    style=ft.ButtonStyle(
                        color=AppConstants.WHITE_COLOR,
                        bgcolor=AppConstants.PRIMARY_COLOR
                    )
                )
            ]),
            padding=ft.Padding(15, 10, 15, 15), border=ft.border.all(1, ft.Colors.with_opacity(0.2, "grey")),
            border_radius=12, bgcolor=ft.Colors.with_opacity(0.03, "black"),
            visible=False, animate_opacity=300
        )
        self.save_button = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.SAVE, size=18),
                ft.Text("Save Entry", size=15, weight=ft.FontWeight.W_600)
            ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
            on_click=self._on_save_click,
            style=ft.ButtonStyle(
                color=AppConstants.WHITE_COLOR,
                bgcolor=AppConstants.PRIMARY_COLOR,
                elevation={"": 2, "hovered": 4},
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.Padding(24, 14, 24, 14)
            ),
            height=50
        )
        self.cancel_button = ft.TextButton(
            "Cancel", on_click=self.on_cancel,
            style=ft.ButtonStyle(color=AppConstants.TEXT_SECONDARY, overlay_color=ft.Colors.with_opacity(0.1, "grey"), shape=ft.RoundedRectangleBorder(radius=8), padding=ft.Padding(20, 12, 20, 12))
        )
        self.appbar = ft.AppBar(
            title=ft.Text("Add New Entry", color=AppConstants.TEXT_PRIMARY, weight=ft.FontWeight.W_600), bgcolor=ft.Colors.WHITE,
            center_title=True, automatically_imply_leading=False,
            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=self.on_cancel, tooltip="Go back"),
        )

        # --- BỐ CỤC 2 CỘT ---
        form_layout = ft.Row(
            controls=[
                # --- Cột Trái ---
                ft.Column(
                    controls=[
                        self.service_field,
                        # --- Row chứa dropdown category và nút manage ---
                        ft.Row([
                            self.category_dropdown,
                            self.manage_categories_button
                        ], spacing=12, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        self.username_field,
                        ft.Row(
                            [self.password_field, self.generate_password_button],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            spacing=12
                        ),
                        self.generator_container,
                    ],
                    spacing=20,
                    expand=1
                ),
                # --- Cột Phải ---
                ft.Column(
                    controls=[
                        self.url_field,
                        self.notes_field,
                    ],
                    spacing=20,
                    expand=1
                ),
            ],
            spacing=30,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

        # Build category options
        self._build_category_options()

        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        form_layout,
                        ft.Row(
                            [self.cancel_button, self.save_button],
                            alignment=ft.MainAxisAlignment.END
                        )
                    ],
                    spacing=30,
                ),
                padding=ft.Padding(40, 30, 40, 30),
                margin=ft.Margin(left=60, top=30, right=60, bottom=30),
                bgcolor=ft.Colors.WHITE,
                border_radius=16,
                shadow=ft.BoxShadow(
                    spread_radius=0, blur_radius=15,
                    color=ft.Colors.with_opacity(0.08, "black"),
                    offset=ft.Offset(0, 4)
                ),
                border=ft.border.all(1, ft.Colors.with_opacity(0.1, "grey")),
            )
        ]

    def set_entry_data(self, entry_data=None):
        self.entry_data = entry_data if entry_data else {}
        is_edit_mode = entry_data is not None
        self.appbar.title.value = "Edit Entry" if is_edit_mode else "Add New Entry"
        self.service_field.value = self.entry_data.get('service', '')

        # --- Lấy dữ liệu cho dropdown category ---
        category_value = self.entry_data.get('category', '').strip()
        if not category_value:
            category_value = CategoryManager.DEFAULT_CATEGORY

        # Đảm bảo category value có trong danh sách options
        if category_value not in [opt.key for opt in self.category_dropdown.options]:
            # Nếu category không có trong danh sách, thêm vào tạm thời
            self.category_dropdown.options.append(
                ft.DropdownOption(key=category_value, text=category_value)
            )

        self.category_dropdown.value = category_value
        self.username_field.value = self.entry_data.get('username', '')
        self.password_field.value = self.entry_data.get('password', '')
        self.url_field.value = self.entry_data.get('url', '')
        self.notes_field.value = self.entry_data.get('notes', '')
        self.service_field.error_text = None
        self.password_field.error_text = None
        self.service_field.border_color = ft.Colors.with_opacity(0.2, "grey")
        self.password_field.border_color = ft.Colors.with_opacity(0.2, "grey")
        self.generator_container.visible = False

    def _on_save_click(self, e):
        # ... (phần validation không đổi)
        if not self.service_field.value.strip():
            self.service_field.error_text = UIMessages.ERROR_SERVICE_REQUIRED
            self.service_field.border_color = AppConstants.DANGER_COLOR
            self.update()
            return
        if not self.password_field.value:
            self.password_field.error_text = UIMessages.ERROR_PASSWORD_REQUIRED
            self.password_field.border_color = AppConstants.DANGER_COLOR
            self.update()
            return

        # --- Thêm trường CATEGORY từ dropdown vào dữ liệu lưu ---
        category_value = self.category_dropdown.value or CategoryManager.DEFAULT_CATEGORY
        result = {
            "service": self.service_field.value.strip(),
            "category": CategoryManager.normalize_category(category_value), # Lấy giá trị từ dropdown và chuẩn hóa
            "username": self.username_field.value.strip(),
            "password": self.password_field.value,
            "url": self.url_field.value.strip(),
            "notes": self.notes_field.value.strip(),
        }
        if 'id' in self.entry_data:
            result['id'] = self.entry_data['id']
        self.on_save(result)

    def _toggle_generator_visibility(self, e):
        self.generator_container.visible = not self.generator_container.visible
        self.update()

    def _on_length_change(self, e):
        self.length_value.value = str(int(self.length_slider.value))
        self.update()

    def _generate_and_fill_password(self, e):
        length = int(self.length_slider.value)
        chars = ""
        if self.uppercase_check.value: chars += string.ascii_uppercase
        if self.lowercase_check.value: chars += string.ascii_lowercase
        if self.numbers_check.value: chars += string.digits
        if self.symbols_check.value: chars += "!@#$%^&*()_+-=[]{}|;':,./<>?"
        if not chars: return
        password_chars = []
        if self.uppercase_check.value: password_chars.append(random.choice(string.ascii_uppercase))
        if self.lowercase_check.value: password_chars.append(random.choice(string.ascii_lowercase))
        if self.numbers_check.value: password_chars.append(random.choice(string.digits))
        if self.symbols_check.value: password_chars.append(random.choice("!@#$%^&*()_+-=[]{}|;':,./<>?"))
        remaining_length = length - len(password_chars)
        for _ in range(remaining_length):
            password_chars.append(random.choice(chars))
        random.shuffle(password_chars)
        password = "".join(password_chars)
        self.password_field.value = password
        self.update()

    def _build_category_options(self):
        """Xây dựng danh sách options cho category dropdown."""
        self.category_dropdown.options.clear()

        # Thêm tất cả categories có sẵn
        for category in self.available_categories:
            self.category_dropdown.options.append(
                ft.DropdownOption(
                    key=category,
                    text=category,
                    # Thêm icon cho default category
                    leading_icon=ft.Icons.FOLDER_SPECIAL if category == CategoryManager.DEFAULT_CATEGORY else ft.Icons.FOLDER_OUTLINED
                )
            )

    def update_available_categories(self, categories: List[str]):
        """Cập nhật danh sách categories có sẵn."""
        self.available_categories = categories.copy()
        current_value = self.category_dropdown.value

        # Rebuild options
        self._build_category_options()

        # Restore value if still valid
        if current_value and current_value in categories:
            self.category_dropdown.value = current_value
        else:
            self.category_dropdown.value = AppConstants.DEFAULT_CATEGORY

        if self.page:
            self.page.update()

    def set_existing_entries(self, entries: List[EntryData]):
        """Set existing entries for smart suggestions."""
        self.existing_entries = entries.copy()

    def _on_service_change(self, e):
        """Handle service name change to provide smart suggestions."""
        service_name = self.service_field.value.strip()
        if not service_name or len(service_name) < 2:
            return

        # Suggest category based on service name
        suggested_category = SmartSuggestions.suggest_category(
            service_name,
            self.available_categories
        )

        if suggested_category and suggested_category in self.available_categories:
            self.category_dropdown.value = suggested_category

        # Suggest username based on existing entries
        if self.existing_entries and not self.username_field.value.strip():
            suggested_username = SmartSuggestions.suggest_username(
                service_name,
                self.existing_entries
            )
            if suggested_username:
                self.username_field.value = suggested_username

        # Suggest URL based on service name
        if not self.url_field.value.strip():
            suggested_url = SmartSuggestions.suggest_url(service_name)
            if suggested_url:
                self.url_field.value = suggested_url

        self.page.update()

    def _generate_and_fill_password_smart(self, e):
        """Generate password using smart helper function."""
        password = generate_secure_password(
            length=AppConstants.PASSWORD_GENERATOR_DEFAULT_LENGTH,
            include_uppercase=True,
            include_lowercase=True,
            include_numbers=True,
            include_symbols=True
        )
        self.password_field.value = password
        self.page.update()
