# auracrypt2/ui/category_management_view.py

import flet as ft
from core.categories import CategoryManager

class CategoryManagementView(ft.View):
    """Giao diện quản lý categories."""

    def __init__(self, page, categories: list[str], entries_count: dict[str, int], on_add_category, on_delete_category, on_rename_category, on_close):
        super().__init__()
        self.page = page
        self.categories = categories.copy()
        self.entries_count = entries_count
        self.on_add_category = on_add_category
        self.on_delete_category = on_delete_category
        self.on_rename_category = on_rename_category
        self.on_close = on_close

        # Colors
        self.primary_color = "#6366f1"
        self.secondary_color = "#ec4899"
        self.danger_color = "#ef4444"
        self.success_color = "#22c55e"
        self.text_primary = "#1f2937"
        self.text_secondary = "#6b7280"

        # Form components
        self.new_category_field = ft.TextField(
            label="New Category Name",
            prefix_icon=ft.Icons.FOLDER_OUTLINED,
            border_radius=12,
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.05, "black"),
            border_color=ft.Colors.with_opacity(0.2, "grey"),
            focused_border_color=self.primary_color,
            height=56,
            text_size=15,
            label_style=ft.TextStyle(color=self.text_secondary),
            cursor_color=self.primary_color,
            capitalization=ft.TextCapitalization.WORDS,
            on_submit=self._on_add_category,
            expand=True
        )

        self.add_button = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.ADD, size=18),
                ft.Text("Add", size=14, weight=ft.FontWeight.W_600)
            ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
            on_click=self._on_add_category,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=self.primary_color,
                elevation={"": 2, "hovered": 4},
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.Padding(16, 12, 16, 12)
            ),
            height=56
        )

        # Categories list
        self.categories_list = ft.ListView(
            expand=True,
            spacing=8,
            padding=ft.Padding(0, 10, 0, 10)
        )

        # AppBar
        self.appbar = ft.AppBar(
            title=ft.Text("Manage Categories", color=self.text_primary, weight=ft.FontWeight.W_600),
            bgcolor=ft.Colors.WHITE,
            center_title=True,
            automatically_imply_leading=False,
            leading=ft.IconButton(
                ft.Icons.ARROW_BACK,
                on_click=self.on_close,
                tooltip="Go back"
            ),
        )

        # Build layout
        self._build_layout()
        self._refresh_categories_list()

    def _build_layout(self):
        """Xây dựng layout của view."""

        # Add category section (Left column)
        add_section = ft.Container(
            content=ft.Column([
                ft.Text("Add New Category",
                       size=18,
                       weight=ft.FontWeight.W_600,
                       color=self.text_primary),
                ft.Text("Create custom categories to organize your passwords",
                       size=14,
                       color=self.text_secondary),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                self.new_category_field,
                ft.Container(height=12),  # Spacing
                self.add_button
            ], spacing=10),
            expand=1,
            padding=ft.Padding(30, 25, 30, 25),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.08, "black"),
                offset=ft.Offset(0, 2)
            ),
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, "grey")),
            margin=ft.Margin(0, 0, 20, 0)
        )

        # Categories list section (Right column)
        list_section = ft.Container(
            content=ft.Column([
                ft.Text("Existing Categories",
                       size=18,
                       weight=ft.FontWeight.W_600,
                       color=self.text_primary),
                ft.Text("Manage your existing categories",
                       size=14,
                       color=self.text_secondary),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Container(
                    content=self.categories_list,
                    expand=True
                )
            ], spacing=10),
            expand=2,
            padding=ft.Padding(30, 25, 30, 25),
            bgcolor=ft.Colors.WHITE,
            border_radius=16,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.08, "black"),
                offset=ft.Offset(0, 2)
            ),
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, "grey"))
        )

        # Main container with two columns
        main_container = ft.Container(
            content=ft.Row([
                add_section,
                list_section
            ], spacing=0),
            padding=ft.Padding(40, 30, 40, 30),
            expand=True
        )

        self.controls = [main_container]

    def _refresh_categories_list(self):
        """Làm mới danh sách categories."""
        self.categories_list.controls.clear()

        if not self.categories:
            # Tạo nút Add New Category cho empty state
            add_category_button = ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.ADD, size=18),
                    ft.Text("Add New Category", size=14, weight=ft.FontWeight.W_600)
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                on_click=lambda e: self.new_category_field.focus(),  # Focus vào text field
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=self.primary_color,
                    elevation={"": 2, "hovered": 4},
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=ft.Padding(16, 12, 16, 12)
                ),
                height=44
            )

            empty_state = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.FOLDER_OPEN_OUTLINED, size=48, color=self.text_secondary),
                    ft.Text("No categories yet",
                           size=16,
                           color=self.text_secondary,
                           weight=ft.FontWeight.W_500),
                    ft.Text("Create your first category to organize passwords",
                           size=12,
                           color=ft.Colors.with_opacity(0.7, self.text_secondary),
                           text_align=ft.TextAlign.CENTER),
                    ft.Container(height=10),
                    add_category_button
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                alignment=ft.alignment.center,
                padding=ft.Padding(20, 40, 20, 40)
            )
            self.categories_list.controls.append(empty_state)
        else:
            for category in self.categories:
                entries_count = self.entries_count.get(category, 0)
                is_default = category == CategoryManager.DEFAULT_CATEGORY

                # Category card
                category_card = ft.Container(
                    content=ft.Row([
                        # Icon and info
                        ft.Row([
                            ft.Container(
                                content=ft.Icon(
                                    ft.Icons.FOLDER_SPECIAL if is_default else ft.Icons.FOLDER_OUTLINED,
                                    color=self.primary_color if is_default else self.text_secondary,
                                    size=20
                                ),
                                width=40,
                                height=40,
                                bgcolor=ft.Colors.with_opacity(0.1, self.primary_color if is_default else self.text_secondary),
                                border_radius=20,
                                alignment=ft.alignment.center
                            ),
                            ft.Column([
                                ft.Row([
                                    ft.Text(category,
                                           size=14,
                                           weight=ft.FontWeight.W_600,
                                           color=self.text_primary),
                                    ft.Container(
                                        content=ft.Text("DEFAULT",
                                                       size=10,
                                                       weight=ft.FontWeight.BOLD,
                                                       color=self.primary_color),
                                        padding=ft.Padding(6, 2, 6, 2),
                                        bgcolor=ft.Colors.with_opacity(0.1, self.primary_color),
                                        border_radius=4
                                    ) if is_default else ft.Container()
                                ], spacing=8),
                                ft.Text(f"{entries_count} password{'s' if entries_count != 1 else ''}",
                                       size=12,
                                       color=self.text_secondary)
                            ], spacing=2, alignment=ft.MainAxisAlignment.CENTER)
                        ], spacing=12),

                        # Action buttons
                        ft.Row([
                            # Edit button (chỉ hiện cho categories không phải default)
                            ft.IconButton(
                                icon=ft.Icons.EDIT_OUTLINED,
                                icon_color=self.primary_color,
                                tooltip="Rename category",
                                on_click=lambda e, cat=category: self._on_rename_category(cat),
                                disabled=is_default
                            ) if not is_default else ft.Container(width=40),
                            # Delete button (chỉ hiện cho categories không phải default)
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=self.danger_color,
                                tooltip=f"Delete category (move {entries_count} entries to {CategoryManager.DEFAULT_CATEGORY})",
                                on_click=lambda e, cat=category: self._on_delete_category(cat),
                                disabled=is_default
                            ) if not is_default else ft.Container(width=40)
                        ], spacing=4) if not is_default else ft.Container(width=88)

                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.Padding(15, 12, 15, 12),
                    bgcolor=ft.Colors.with_opacity(0.02, "black"),
                    border_radius=12,
                    border=ft.border.all(1, ft.Colors.with_opacity(0.1, "grey")),
                    margin=ft.Margin(0, 2, 0, 2)
                )

                self.categories_list.controls.append(category_card)

        if self.page:
            self.page.update()

    def _on_add_category(self, e):
        """Xử lý thêm category mới."""
        category_name = self.new_category_field.value.strip()

        # Clear previous errors
        self.new_category_field.error_text = None
        self.new_category_field.border_color = ft.Colors.with_opacity(0.2, "grey")

        # Validate
        is_valid, error_message = CategoryManager.validate_category_name(category_name)
        if not is_valid:
            self.new_category_field.error_text = error_message
            self.new_category_field.border_color = self.danger_color
            self.update()
            return

        # Normalize category name
        normalized_name = CategoryManager.normalize_category(category_name)

        # Check if already exists
        if normalized_name in self.categories:
            self.new_category_field.error_text = "Category already exists"
            self.new_category_field.border_color = self.danger_color
            self.update()
            return

        # Add to list and callback
        self.categories.append(normalized_name)
        self.categories.sort()
        self.entries_count[normalized_name] = 0

        # Clear field
        self.new_category_field.value = ""

        # Callback to parent
        self.on_add_category(normalized_name)

        # Refresh UI
        self._refresh_categories_list()
        self.update()

        # Show success message
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Category '{normalized_name}' added successfully"),
            bgcolor=self.success_color,
            duration=2000
        )
        self.page.snack_bar.open = True
        self.page.update()

    def _on_delete_category(self, category_name: str):
        """Xử lý xóa category."""
        entries_count = self.entries_count.get(category_name, 0)

        # Tạo dialog xác nhận
        def confirm_delete(e):
            # Remove from list
            self.categories.remove(category_name)

            # Safely remove from entries_count if exists
            if category_name in self.entries_count:
                del self.entries_count[category_name]

            # Callback to parent
            self.on_delete_category(category_name)

            # Refresh UI
            self._refresh_categories_list()
            self.update()

            # Close dialog
            dialog.open = False
            self.page.update()

            # Show success message
            move_message = f" (moved {entries_count} entries to {CategoryManager.DEFAULT_CATEGORY})" if entries_count > 0 else ""
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Category '{category_name}' deleted{move_message}"),
                bgcolor=self.success_color,
                duration=3000
            )
            self.page.snack_bar.open = True
            self.page.update()

        def cancel_delete(e):
            dialog.open = False
            self.page.update()

        # Create confirmation dialog
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Category"),
            content=ft.Column([
                ft.Text(f"Are you sure you want to delete '{category_name}'?"),
                ft.Text(f"This category contains {entries_count} password{'s' if entries_count != 1 else ''}.",
                       color=self.text_secondary, size=12) if entries_count > 0 else ft.Container(),
                ft.Text(f"All passwords will be moved to '{CategoryManager.DEFAULT_CATEGORY}'.",
                       color=self.text_secondary, size=12) if entries_count > 0 else ft.Container()
            ], tight=True, spacing=8),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_delete),
                ft.ElevatedButton(
                    "Delete",
                    on_click=confirm_delete,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=self.danger_color
                    )
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _on_rename_category(self, category_name: str):
        """Xử lý đổi tên category."""
        entries_count = self.entries_count.get(category_name, 0)

        # Text field cho tên mới
        rename_field = ft.TextField(
            label="New category name",
            value=category_name,
            border_radius=8,
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.05, "black"),
            border_color=ft.Colors.with_opacity(0.2, "grey"),
            focused_border_color=self.primary_color,
            height=50,
            text_size=14,
            label_style=ft.TextStyle(color=self.text_secondary),
            cursor_color=self.primary_color,
            capitalization=ft.TextCapitalization.WORDS,
            autofocus=True,
            expand=True
        )

        def confirm_rename(e):
            new_name = rename_field.value.strip()

            # Clear previous errors
            rename_field.error_text = None
            rename_field.border_color = ft.Colors.with_opacity(0.2, "grey")

            # Validate using CategoryManager
            is_valid, error_message = CategoryManager.validate_category_rename(
                category_name, new_name, self.categories
            )

            if not is_valid:
                rename_field.error_text = error_message
                rename_field.border_color = self.danger_color
                self.page.update()
                return

            # Normalize new name
            normalized_name = CategoryManager.normalize_category(new_name)

            # Update local list
            category_index = self.categories.index(category_name)
            self.categories[category_index] = normalized_name
            self.categories.sort()

            # Update entries count
            if category_name in self.entries_count:
                self.entries_count[normalized_name] = self.entries_count.pop(category_name)

            # Callback to parent
            self.on_rename_category(category_name, normalized_name)

            # Close dialog
            dialog.open = False
            self.page.update()

            # Refresh UI
            self._refresh_categories_list()
            self.update()

            # Show success message
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Category renamed from '{category_name}' to '{normalized_name}'"),
                bgcolor=self.success_color,
                duration=3000
            )
            self.page.snack_bar.open = True
            self.page.update()

        def cancel_rename(e):
            dialog.open = False
            self.page.update()

        def on_submit(e):
            confirm_rename(e)

        # Set submit handler for text field
        rename_field.on_submit = on_submit

        # Create rename dialog
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Rename Category"),
            content=ft.Column([
                ft.Text(f"Rename category '{category_name}'"),
                ft.Text(f"This category contains {entries_count} password{'s' if entries_count != 1 else ''}.",
                       color=self.text_secondary, size=12) if entries_count > 0 else ft.Container(),
                ft.Container(height=10),
                rename_field
            ], tight=True, spacing=8),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_rename),
                ft.ElevatedButton(
                    "Rename",
                    on_click=confirm_rename,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=self.primary_color
                    )
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def update_categories(self, categories: list[str], entries_count: dict[str, int]):
        """Cập nhật danh sách categories từ bên ngoài."""
        self.categories = categories.copy()
        self.entries_count = entries_count
        self._refresh_categories_list()
