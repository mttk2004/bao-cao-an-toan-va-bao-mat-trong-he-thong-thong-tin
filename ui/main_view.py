# auracrypt2/ui/main_view.py

import flet as ft
from typing import Callable, Optional, List
from core.constants import AppConstants, UIMessages
from utils.app_types import EntryData

class MainView(ft.View):
    def __init__(
        self,
        page: ft.Page,
        on_add: Callable,
        on_edit: Callable,
        on_delete: Callable,
        on_copy: Callable,
        on_lock: Callable,
        on_about: Callable,
        on_manage_categories: Optional[Callable] = None
    ):
        super().__init__(route="/main")
        self.page = page
        self.on_add = on_add
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_copy = on_copy
        self.on_lock = on_lock
        self.on_about = on_about
        # callback để chuyển tới view quản lý categories từ main view
        self.on_manage_categories = on_manage_categories

        # --- State Management ---
        self.all_entries: List[EntryData] = []
        self._selected_entry_control: Optional[ft.Control] = None
        self._selected_category = "All Items"
        self._selected_category_control: Optional[ft.Control] = None

        # --- STEP 1: DEFINE ALL UI COMPONENTS FIRST ---
        self.search_bar = ft.TextField(
            label="Search your passwords...",
            on_change=self._on_search,
            prefix_icon=ft.Icons.SEARCH,
            border_radius=AppConstants.BORDER_RADIUS,
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.05, "black"),
            border_color=ft.Colors.with_opacity(0.2, "grey"),
            focused_border_color=AppConstants.PRIMARY_COLOR,
            expand=True,
            height=50,
            text_size=14,
            label_style=ft.TextStyle(color=AppConstants.TEXT_SECONDARY),
            cursor_color=AppConstants.PRIMARY_COLOR
        )
        self.categories_list = ft.ListView(expand=True, spacing=5, padding=ft.Padding(5, 10, 5, 10))
        self.entries_list = ft.ListView(expand=True, spacing=8, padding=ft.Padding(10, 10, 10, 10))

        self.empty_state = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.TOUCH_APP_OUTLINED, size=48, color=AppConstants.TEXT_SECONDARY),
                    ft.Text("Select a password entry", size=16, color=AppConstants.TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                    ft.Text("Choose an entry from the list to view details", size=12, color=ft.Colors.with_opacity(0.7, AppConstants.TEXT_SECONDARY), text_align=ft.TextAlign.CENTER)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12
            ),
            alignment=ft.alignment.center,
            expand=True,
            padding=ft.Padding(20, 80, 20, 80)
        )
        self.details_view = ft.Column([self.empty_state], expand=True, spacing=20, scroll=ft.ScrollMode.AUTO)

        self.add_button = ft.Container(
            content=ft.ElevatedButton(
                content=ft.Row([ft.Icon(ft.Icons.ADD, size=18), ft.Text("Add New", size=14, weight=ft.FontWeight.W_600)], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                on_click=self.on_add,
                style=ft.ButtonStyle(
                    color=AppConstants.WHITE_COLOR,
                    bgcolor=AppConstants.PRIMARY_COLOR,
                    elevation={"": 2, "hovered": 4},
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=ft.Padding(16, 12, 16, 12)
                ),
                height=AppConstants.BUTTON_HEIGHT
            ),
            tooltip=UIMessages.TOOLTIP_ADD_ENTRY
        )
        self.edit_button = ft.Container(
            content=ft.ElevatedButton(
                content=ft.Row([ft.Icon(ft.Icons.EDIT, size=16), ft.Text("Edit", size=13, weight=ft.FontWeight.W_500)], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                on_click=lambda e: self.on_edit(self.get_selected_entry()),
                disabled=True,
                style=ft.ButtonStyle(
                    color=AppConstants.WHITE_COLOR,
                    bgcolor=AppConstants.WARNING_COLOR,
                    elevation={"": 1, "hovered": 2},
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding(12, 8, 12, 8)
                ),
                height=AppConstants.SMALL_BUTTON_HEIGHT
            ),
            tooltip=UIMessages.TOOLTIP_EDIT_ENTRY
        )
        self.delete_button = ft.Container(
            content=ft.ElevatedButton(
                content=ft.Row([ft.Icon(ft.Icons.DELETE, size=16), ft.Text("Delete", size=13, weight=ft.FontWeight.W_500)], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                on_click=lambda e: self.on_delete(self.get_selected_entry()),
                disabled=True,
                style=ft.ButtonStyle(
                    color=AppConstants.WHITE_COLOR,
                    bgcolor=AppConstants.DANGER_COLOR,
                    elevation={"": 1, "hovered": 2},
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding(12, 8, 12, 8)
                ),
                height=AppConstants.SMALL_BUTTON_HEIGHT
            ),
            tooltip=UIMessages.TOOLTIP_DELETE_ENTRY
        )
        self.copy_button = ft.Container(
            content=ft.ElevatedButton(
                content=ft.Row([ft.Icon(ft.Icons.COPY, size=16), ft.Text("Copy Password", size=13, weight=ft.FontWeight.W_500)], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                on_click=lambda e: self.on_copy(self.get_selected_entry()),
                disabled=True,
                style=ft.ButtonStyle(
                    color=AppConstants.WHITE_COLOR,
                    bgcolor=AppConstants.SUCCESS_COLOR,
                    elevation={"": 1, "hovered": 2},
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding(12, 8, 12, 8)
                ),
                height=AppConstants.SMALL_BUTTON_HEIGHT
            ),
            tooltip=UIMessages.TOOLTIP_COPY_PASSWORD
        )
        self.lock_button = ft.Container(
            content=ft.ElevatedButton(
                content=ft.Row([ft.Icon(ft.Icons.LOCK, size=18), ft.Text("Lock Vault", size=14, weight=ft.FontWeight.W_600)], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                on_click=self.on_lock,
                style=ft.ButtonStyle(
                    color=AppConstants.TEXT_PRIMARY,
                    bgcolor=ft.Colors.with_opacity(0.1, "grey"),
                    elevation={"": 1, "hovered": 2},
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=ft.Padding(16, 12, 16, 12)
                ),
                height=AppConstants.BUTTON_HEIGHT
            ),
            tooltip="Lock and secure vault"
        )
        self.about_button = ft.IconButton(
            icon=ft.Icons.INFO_OUTLINE,
            icon_color=AppConstants.TEXT_SECONDARY,
            on_click=self.on_about,
            tooltip="About AuraCrypt"
        )

        # --- STEP 2: BUILD THE LAYOUT USING THE COMPONENTS DEFINED ABOVE ---
        self.header = ft.Container(
            content=ft.Row(
                [
                    ft.Row([ft.Icon(ft.Icons.SECURITY, size=24, color=AppConstants.PRIMARY_COLOR), ft.Text("AuraCrypt", size=20, weight=ft.FontWeight.BOLD, color=AppConstants.PRIMARY_COLOR)], spacing=8),
                    ft.Row([self.about_button, self.add_button, self.lock_button], spacing=12)
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=ft.Padding(20, 20, 20, 10), bgcolor=ft.Colors.with_opacity(0.02, "black")
        )
        self.search_section = ft.Container(content=self.search_bar, padding=ft.Padding(20, 10, 20, 20))

        self.categories_card = ft.Container(
            content=ft.Column(
                [
                    # Thêm header với tiêu đề và nút Manage Categories
                    ft.Container(
                        content=ft.Row([
                            ft.Text("Categories", size=14, weight=ft.FontWeight.W_600, color=AppConstants.TEXT_PRIMARY),
                            # Nút quản lý categories (tương tự như trong EntryView)
                            ft.IconButton(
                                icon=ft.Icons.SETTINGS,
                                icon_color=AppConstants.TEXT_SECONDARY,
                                tooltip="Manage Categories",
                                on_click=self.on_manage_categories if self.on_manage_categories else None,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=ft.Padding(20, 15, 20, 10)
                    ),
                    ft.Container(content=self.categories_list, expand=True)
                ],
                spacing=0
            ),
            expand=1,
            bgcolor=ft.Colors.WHITE, border_radius=16,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color=ft.Colors.with_opacity(0.08, "black"), offset=ft.Offset(0, 2)),
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, "grey")), margin=ft.Margin(0, 0, 10, 0)
        )
        self.entries_card = ft.Container(
            content=ft.Column(
                [
                    ft.Container(content=ft.Text("Password Entries", size=16, weight=ft.FontWeight.W_600, color=AppConstants.TEXT_PRIMARY), padding=ft.Padding(20, 15, 20, 10)),
                    ft.Container(content=self.entries_list, expand=True)
                ],
                spacing=0
            ),
            expand=2,
            bgcolor=ft.Colors.WHITE, border_radius=16,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color=ft.Colors.with_opacity(0.08, "black"), offset=ft.Offset(0, 2)),
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, "grey")), margin=ft.Margin(0, 0, 10, 0)
        )
        self.details_card = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text("Entry Details", size=16, weight=ft.FontWeight.W_600, color=AppConstants.TEXT_PRIMARY),
                                ft.Row([self.edit_button, self.copy_button, self.delete_button], spacing=8)
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        padding=ft.Padding(20, 15, 20, 10)
                    ),
                    ft.Container(content=self.details_view, expand=True, padding=ft.Padding(20, 0, 20, 20))
                ],
                spacing=0
            ),
            expand=3,
            bgcolor=ft.Colors.WHITE, border_radius=16,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color=ft.Colors.with_opacity(0.08, "black"), offset=ft.Offset(0, 2)),
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, "grey")), margin=ft.Margin(10, 0, 0, 0)
        )

        self.background = ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center, end=ft.alignment.bottom_center,
                colors=["#f8fafc", "#f1f5f9", "#e2e8f0"]
            )
        )

        self.controls = [
            ft.Stack(
                [
                    self.background,
                    ft.Column(
                        [
                            self.header,
                            self.search_section,
                            ft.Container(
                                content=ft.Row([self.categories_card, self.entries_card, self.details_card], spacing=0),
                                expand=True,
                                padding=ft.Padding(20, 0, 20, 20)
                            )
                        ],
                        spacing=0
                    )
                ],
                expand=True
            )
        ]

    def update_entries(self, entries: List[EntryData], categories: List[str]):
        self.all_entries = sorted(entries, key=lambda e: e['service'].lower())
        self._update_categories_list(categories)
        self._on_search(None)

    def _get_entries_count_by_category(self) -> dict[str, int]:
        """Đếm số lượng entries theo từng category."""
        count = {}

        for entry in self.all_entries:
            category = entry.get('category', '').strip()
            if not category:
                category = "Uncategorized"

            count[category] = count.get(category, 0) + 1

        return count

    def _get_current_categories(self) -> list[str]:
        """Lấy danh sách categories hiện tại từ categories list."""
        categories = []
        for control in self.categories_list.controls:
            if hasattr(control, 'data') and control.data != "All Items":
                categories.append(control.data)
        return categories

    def refresh_categories_count(self):
        """Cập nhật lại số lượng entries cho categories hiện tại."""
        entries_count = self._get_entries_count_by_category()
        total_entries = len(self.all_entries)

        for control in self.categories_list.controls:
            if hasattr(control, 'data'):
                if control.data == "All Items":
                    # Cập nhật All Items
                    all_items_title = f"All Items ({total_entries})" if total_entries > 0 else "All Items"
                    control.content.title.value = all_items_title
                else:
                    # Cập nhật category cụ thể
                    category_name = control.data
                    category_count = entries_count.get(category_name, 0)

                    if category_count > 0:
                        display_name = f"{category_name} ({category_count})"
                    else:
                        display_name = category_name

                    control.content.title.value = display_name

        if self.page:
            self.page.update()

    # --- SỬA LỖI TẠI ĐÂY ---
    def _update_categories_list(self, categories: List[str]):
        self.categories_list.controls.clear()

        # Đếm số lượng entries theo category
        entries_count = self._get_entries_count_by_category()
        total_entries = len(self.all_entries)

        # All Items với số lượng tổng
        all_items_title = f"All Items ({total_entries})" if total_entries > 0 else "All Items"
        all_items_container = ft.Container(
            content=ft.ListTile(
                title=ft.Text(all_items_title, weight=ft.FontWeight.W_500, size=13),
                leading=ft.Icon(ft.Icons.ALL_INBOX, size=18),
            ),
            on_click=self._on_category_selected,
            data="All Items",
            border_radius=ft.border_radius.all(8)
        )
        self.categories_list.controls.append(all_items_container)

        if self._selected_category == "All Items":
            all_items_container.bgcolor = ft.Colors.with_opacity(0.1, AppConstants.PRIMARY_COLOR)
            self._selected_category_control = all_items_container

        for category_name in categories:
            category_count = entries_count.get(category_name, 0)

            # Chỉ hiển thị số lượng nếu > 0
            if category_count > 0:
                display_name = f"{category_name} ({category_count})"
            else:
                display_name = category_name

            category_container = ft.Container(
                content=ft.ListTile(
                    title=ft.Text(display_name, size=13),
                    leading=ft.Icon(ft.Icons.FOLDER_OUTLINED, size=18),
                ),
                on_click=self._on_category_selected,
                data=category_name,
                border_radius=ft.border_radius.all(8)
            )

            if category_name == self._selected_category:
                 category_container.bgcolor = ft.Colors.with_opacity(0.1, AppConstants.PRIMARY_COLOR)
                 self._selected_category_control = category_container

            self.categories_list.controls.append(category_container)

        if self.page: self.page.update()

    # Hàm này không cần thay đổi, vì e.control giờ là Container, đúng như ta muốn
    def _on_category_selected(self, e):
        selected_category_name = e.control.data
        if self._selected_category == selected_category_name:
            return

        if self._selected_category_control:
            self._selected_category_control.bgcolor = None

        self._selected_category = selected_category_name
        self._selected_category_control = e.control
        self._selected_category_control.bgcolor = ft.Colors.with_opacity(0.1, AppConstants.PRIMARY_COLOR)

        self._on_search(None)

    def _on_search(self, e):
        search_term = self.search_bar.value.lower() if self.search_bar.value else ""
        self.entries_list.controls.clear()

        entries_to_display = []
        if self._selected_category == "All Items":
            entries_to_display = self.all_entries
        else:
            entries_to_display = [
                entry for entry in self.all_entries
                if entry.get('category', '').strip() == self._selected_category
            ]

        filtered_entries = [
            entry for entry in entries_to_display if
            search_term in entry['service'].lower() or
            search_term in entry.get('username', '').lower() or
            search_term in entry.get('url', '').lower()
        ]

        if not filtered_entries:
            # Tạo nút Add New Entry cho empty state
            add_entry_button = ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.ADD, size=18),
                    ft.Text("Add New Entry", size=14, weight=ft.FontWeight.W_600)
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                on_click=self.on_add,
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=AppConstants.PRIMARY_COLOR,
                    elevation={"": 2, "hovered": 4},
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=ft.Padding(16, 12, 16, 12)
                ),
                height=44
            )

            # Tạo empty state với nút action
            if search_term:
                # Empty state cho search results
                empty_content = [
                    ft.Icon(ft.Icons.SEARCH_OFF, size=48, color=AppConstants.TEXT_SECONDARY),
                    ft.Text("No entries found", size=16, color=AppConstants.TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                    ft.Text(f"No results for '{search_term}'",
                           size=12, color=ft.Colors.with_opacity(0.7, AppConstants.TEXT_SECONDARY), text_align=ft.TextAlign.CENTER),
                    ft.Text("Try a different search term or add a new entry",
                           size=11, color=ft.Colors.with_opacity(0.6, AppConstants.TEXT_SECONDARY), text_align=ft.TextAlign.CENTER),
                    ft.Container(height=10),
                    add_entry_button
                ]
            else:
                # Empty state cho vault trống
                empty_content = [
                    ft.Icon(ft.Icons.LOCK_OPEN_OUTLINED, size=48, color=AppConstants.TEXT_SECONDARY),
                    ft.Text("No passwords yet", size=16, color=AppConstants.TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                    ft.Text("Start by adding your first password",
                           size=12, color=ft.Colors.with_opacity(0.7, AppConstants.TEXT_SECONDARY), text_align=ft.TextAlign.CENTER),
                    ft.Container(height=10),
                    add_entry_button
                ]

            empty_search = ft.Container(
                content=ft.Column(
                    empty_content,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12
                ),
                alignment=ft.alignment.center, padding=ft.Padding(20, 40, 20, 40)
            )
            self.entries_list.controls.append(empty_search)
        else:
            for entry in filtered_entries:
                entry_card = ft.Container(
                    content=ft.ListTile(
                        leading=ft.Container(content=ft.Icon(ft.Icons.LOCK, color=AppConstants.PRIMARY_COLOR, size=20), width=40, height=40, bgcolor=ft.Colors.with_opacity(0.1, AppConstants.PRIMARY_COLOR), border_radius=20, alignment=ft.alignment.center),
                        title=ft.Text(entry['service'], size=14, weight=ft.FontWeight.W_600, color=AppConstants.TEXT_PRIMARY),
                        subtitle=ft.Text(entry.get('username', 'No username'), size=12, color=AppConstants.TEXT_SECONDARY),
                        trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT, color=AppConstants.TEXT_SECONDARY, size=16),
                        data=entry, on_click=self._on_entry_selected
                    ),
                    bgcolor=ft.Colors.with_opacity(0.02, "black"), border_radius=12, margin=ft.Margin(5, 2, 5, 2),
                    padding=ft.Padding(5, 5, 5, 5), border=ft.border.all(1, ft.Colors.with_opacity(0.05, "grey")),
                    animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
                )
                self.entries_list.controls.append(entry_card)

        self._clear_selection()
        if self.page: self.page.update()

    def remove_entry_from_list(self, entry_id: str):
        self.all_entries = [e for e in self.all_entries if e.get('id') != entry_id]
        # Cập nhật lại số lượng categories mà không rebuild toàn bộ
        self.refresh_categories_count()
        # Sau đó cập nhật lại entries list
        self._on_search(None)

    def _on_entry_selected(self, e):
        if self._selected_entry_control:
            self._selected_entry_control.bgcolor = ft.Colors.with_opacity(0.02, "black")
            self._selected_entry_control.border = ft.border.all(1, ft.Colors.with_opacity(0.05, "grey"))
        selected_container = e.control.parent
        selected_container.bgcolor = ft.Colors.with_opacity(0.1, AppConstants.PRIMARY_COLOR)
        selected_container.border = ft.border.all(1, ft.Colors.with_opacity(0.3, AppConstants.PRIMARY_COLOR))
        self._selected_entry_control = selected_container
        self.update_details_view(e.control.data)
        self.edit_button.content.disabled = False
        self.delete_button.content.disabled = False
        self.copy_button.content.disabled = False
        if self.page: self.page.update()

    def update_details_view(self, entry: dict):
        self.details_view.controls.clear()
        if entry:
            service_header = ft.Container(
                content=ft.Row(
                    [
                        ft.Container(content=ft.Icon(ft.Icons.LOCK, color=AppConstants.PRIMARY_COLOR, size=24), width=48, height=48, bgcolor=ft.Colors.with_opacity(0.1, AppConstants.PRIMARY_COLOR), border_radius=24, alignment=ft.alignment.center),
                        ft.Column([ft.Text(entry['service'], size=18, weight=ft.FontWeight.BOLD, color=AppConstants.TEXT_PRIMARY), ft.Text("Password Entry", size=12, color=AppConstants.TEXT_SECONDARY)], spacing=2, alignment=ft.MainAxisAlignment.CENTER)
                    ],
                    spacing=12, alignment=ft.MainAxisAlignment.START
                ),
                margin=ft.Margin(0, 0, 0, 20)
            )
            username_field = self._create_detail_field("Username", entry.get('username', ''), ft.Icons.PERSON_OUTLINE, can_copy=True)
            password_field = self._create_detail_field("Password", "••••••••••••", ft.Icons.LOCK_OUTLINE, can_copy=True, is_password=True, original_value=entry.get('password'))
            url_field = self._create_detail_field("Website URL", entry.get('url', ''), ft.Icons.LINK, can_copy=True, can_open=True if entry.get('url') else False)
            notes_field = self._create_detail_field("Notes", entry.get('notes', ''), ft.Icons.NOTES, multiline=True)
            self.details_view.controls.extend([service_header, username_field, password_field, url_field, notes_field])
        else:
            self.details_view.controls.append(self.empty_state)
        if self.page: self.page.update()

    def _create_detail_field(self, label: str, value: str, icon, can_copy: bool = False, can_open: bool = False, is_password: bool = False, multiline: bool = False, original_value: str = None):
        actions = []
        copy_value = original_value if is_password else value
        if is_password:
            password_text = ft.Text("••••••••••••", size=14, color=AppConstants.TEXT_PRIMARY, weight=ft.FontWeight.W_400, selectable=True, expand=True, data={"hidden": True, "original": original_value})
            def toggle_password_visibility(e):
                is_hidden = password_text.data["hidden"]
                if is_hidden:
                    password_text.value = password_text.data["original"]
                    e.control.icon = ft.Icons.VISIBILITY_OFF
                    e.control.tooltip = "Hide password"
                else:
                    password_text.value = "••••••••••••"
                    e.control.icon = ft.Icons.VISIBILITY
                    e.control.tooltip = "Show password"
                password_text.data["hidden"] = not is_hidden
                self.page.update()
            visibility_btn = ft.IconButton(
                icon=ft.Icons.VISIBILITY, icon_size=16, tooltip="Show password",
                on_click=toggle_password_visibility,
                style=ft.ButtonStyle(color=AppConstants.TEXT_SECONDARY, bgcolor=ft.Colors.with_opacity(0.05, "grey"), shape=ft.CircleBorder())
            )
            actions.append(visibility_btn)
            display_text = password_text
        else:
            display_text = ft.Text(value if value else "Not provided", size=14, color=AppConstants.TEXT_PRIMARY if value else AppConstants.TEXT_SECONDARY, weight=ft.FontWeight.W_400, selectable=True, expand=True)
        if can_open and value:
            open_btn = ft.IconButton(
                icon=ft.Icons.OPEN_IN_NEW, icon_size=16, tooltip="Open URL", on_click=lambda e: self.page.launch_url(value),
                style=ft.ButtonStyle(color=AppConstants.PRIMARY_COLOR, bgcolor=ft.Colors.with_opacity(0.1, AppConstants.PRIMARY_COLOR), shape=ft.CircleBorder())
            )
            actions.append(open_btn)
        if can_copy and copy_value:
            copy_btn = ft.IconButton(
                icon=ft.Icons.COPY, icon_size=16, tooltip=f"Copy {label.lower()}",
                on_click=lambda e: self._copy_field_value(copy_value, label),
                style=ft.ButtonStyle(color=AppConstants.TEXT_SECONDARY, bgcolor=ft.Colors.with_opacity(0.05, "grey"), shape=ft.CircleBorder())
            )
            actions.append(copy_btn)
        field_content = ft.Container(
            content=ft.Column(
                [
                    ft.Row([ft.Icon(icon, size=16, color=AppConstants.TEXT_SECONDARY), ft.Text(label, size=12, weight=ft.FontWeight.W_500, color=AppConstants.TEXT_SECONDARY)], spacing=6),
                    ft.Container(
                        content=ft.Row(
                            [
                                display_text,
                                ft.Row(actions, spacing=4) if actions else ft.Container()
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        padding=ft.Padding(12, 10, 12, 10), bgcolor=ft.Colors.with_opacity(0.03, "black"),
                        border_radius=8, border=ft.border.all(1, ft.Colors.with_opacity(0.1, "grey"))
                    )
                ],
                spacing=6
            ),
            margin=ft.Margin(0, 0, 0, 16)
        )
        return field_content

    def _copy_field_value(self, value: str, field_name: str):
        if value:
            self.page.set_clipboard(value)
            self.page.snack_bar = ft.SnackBar(content=ft.Text(f"{field_name} copied to clipboard"), bgcolor=self.success_color, duration=2000)
            self.page.snack_bar.open = True
            self.page.update()

    def get_selected_entry(self) -> Optional[EntryData]:
        if self._selected_entry_control and self._selected_entry_control.content:
            return self._selected_entry_control.content.data
        return None

    def _clear_selection(self):
        if self._selected_entry_control:
            self._selected_entry_control.bgcolor = ft.Colors.with_opacity(0.02, "black")
            self._selected_entry_control.border = ft.border.all(1, ft.Colors.with_opacity(0.05, "grey"))
            self._selected_entry_control = None
        self.update_details_view(None)
        self.edit_button.content.disabled = True
        self.delete_button.content.disabled = True
        self.copy_button.content.disabled = True
        if self.page: self.page.update()
