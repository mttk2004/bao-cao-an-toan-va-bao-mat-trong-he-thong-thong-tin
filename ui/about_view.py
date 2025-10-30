# auracrypt2/ui/about_view.py

import flet as ft

class AboutView(ft.View):
    def __init__(self, page, on_back):
        super().__init__(route="/about")
        self.page = page
        self.on_back = on_back

        # --- Modern Color Scheme ---
        self.primary_color = "#6366f1"
        self.text_primary = "#1f2937"
        self.text_secondary = "#6b7280"
        self.bgcolor = "#f8fafc"

        # --- AppBar ---
        self.appbar = ft.AppBar(
            title=ft.Text("About AuraCrypt", color=self.text_primary, weight=ft.FontWeight.W_600),
            bgcolor=ft.Colors.WHITE,
            center_title=True,
            automatically_imply_leading=False,
            leading=ft.IconButton(
                ft.Icons.ARROW_BACK,
                on_click=self.on_back,
                tooltip="Go back"
            ),
        )

        # --- UI Components ---
        self.app_logo = ft.Icon(
            ft.Icons.SECURITY,
            size=64,
            color=self.primary_color
        )

        self.app_title = ft.Text(
            "AuraCrypt",
            size=40,
            weight=ft.FontWeight.BOLD,
            color=self.primary_color
        )

        self.app_version = ft.Text(
            "Phiên bản 1.0.0",
            size=16,
            color=self.text_secondary
        )

        self.app_description = ft.Text(
            "AuraCrypt là một trình quản lý mật khẩu cá nhân an toàn, được xây dựng để giúp bạn lưu trữ và quản lý thông tin đăng nhập một cách bảo mật bằng mã hóa AES-256-GCM mạnh mẽ.",
            size=14,
            color=self.text_primary,
            text_align=ft.TextAlign.CENTER,
            width=500
        )

        # --- THÔNG TIN TÁC GIẢ MỚI ---
        self.author_name = ft.Text(
            "Được phát triển bởi Mai Trần Tuấn Kiệt",
            size=15,
            weight=ft.FontWeight.W_500,
            color=self.text_primary
        )

        self.links_row = ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.CODE,
                    icon_color=self.text_secondary,
                    tooltip="GitHub Profile",
                    on_click=lambda e: self.page.launch_url("https://github.com/mttk2004")
                ),
                ft.IconButton(
                    icon=ft.Icons.LINK,
                    icon_color=self.text_secondary,
                    tooltip="Portfolio Website",
                    on_click=lambda e: self.page.launch_url("https://mttk2004.uk")
                ),
                ft.IconButton(
                    icon=ft.Icons.EMAIL_OUTLINED,
                    icon_color=self.text_secondary,
                    tooltip="Contact Email",
                    on_click=lambda e: self.page.launch_url("mailto:mttk2004@hotmail.com")
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

        self.author_section = ft.Column(
            [
                ft.Divider(height=20),
                self.author_name,
                self.links_row
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5
        )

        # --- BỐ CỤC CHÍNH ---
        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        self.app_logo,
                        self.app_title,
                        self.app_version,
                        ft.Container(height=20),
                        self.app_description,
                        ft.Container(height=30),
                        self.author_section,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=12,
                    expand=True
                ),
                expand=True,
                alignment=ft.alignment.center,
                bgcolor=self.bgcolor
            )
        ]
