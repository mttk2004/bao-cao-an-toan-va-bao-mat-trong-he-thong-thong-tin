# utils/shortcut_manager.py
# Module để quản lý việc tạo desktop shortcut cho Windows

import os
import sys
import platform
import traceback
from pathlib import Path
from typing import Optional

try:
    import winshell
    from win32com.client import Dispatch
    # --- PHẦN SỬA LỖI QUAN TRỌNG ---
    import pythoncom
    # --- KẾT THÚC SỬA LỖI ---
    WINSHELL_AVAILABLE = True
except ImportError:
    winshell = None
    Dispatch = None
    pythoncom = None # Thêm dòng này để an toàn
    WINSHELL_AVAILABLE = False

try:
    from .file_paths import AppPaths
except ImportError:
    # Fallback for standalone execution
    from file_paths import AppPaths


class ShortcutManager:
    """
    Quản lý việc tạo và kiểm tra desktop shortcut cho AuraCrypt.
    Chỉ hoạt động trên Windows và khi winshell được cài đặt.
    """

    FIRST_RUN_MARKER = ".firstrun_complete"
    SHORTCUT_NAME = "AuraCrypt.lnk"
    LOG_FILE_NAME = "debug_log.txt"

    def __init__(self):
        self.app_paths = AppPaths()
        try:
            self.app_paths.ensure_app_dirs()
        except Exception:
            pass

        self.is_windows = platform.system().lower() == "windows"
        self.can_create_shortcuts = self.is_windows and WINSHELL_AVAILABLE
        self.log_path = self.app_paths.get_app_data_dir() / self.LOG_FILE_NAME

    def _log(self, message: str):
        """Ghi thông báo vào file log."""
        try:
            with open(self.log_path, 'a', encoding='utf-8') as f:
                from datetime import datetime
                f.write(f"[{datetime.now().isoformat()}] {message}\n")
        except Exception:
            pass

    def get_first_run_marker_path(self) -> Path:
        """Trả về đường dẫn đến file đánh dấu lần chạy đầu tiên."""
        return self.app_paths.get_app_data_dir() / self.FIRST_RUN_MARKER

    def is_first_run(self) -> bool:
        """Kiểm tra xem đây có phải là lần chạy đầu tiên không."""
        return not self.get_first_run_marker_path().exists()

    def mark_first_run_complete(self) -> None:
        """Tạo file đánh dấu để báo hiệu lần chạy đầu tiên đã hoàn thành."""
        try:
            marker_path = self.get_first_run_marker_path()
            marker_path.parent.mkdir(parents=True, exist_ok=True)
            with open(marker_path, 'w', encoding='utf-8') as f:
                f.write("Completed")
            self._log("Successfully created first-run marker.")
        except Exception as e:
            self._log(f"ERROR: Could not create first run marker: {e}")
            self._log(traceback.format_exc())

    def get_executable_path(self) -> Optional[str]:
        """Lấy đường dẫn đến file executable hiện tại."""
        try:
            if getattr(sys, 'frozen', False):
                self._log(f"Running as frozen executable. Path: {sys.executable}")
                return sys.executable
            else:
                main_script_path = Path(__file__).parent.parent / "main.py"
                self._log(f"Running as script. Main script path: {main_script_path}")
                return str(main_script_path.resolve())
        except Exception as e:
            self._log(f"ERROR: Could not get executable path: {e}")
            self._log(traceback.format_exc())
            return None

    def get_desktop_path(self) -> Optional[Path]:
        """Lấy đường dẫn đến Desktop của user."""
        if not self.can_create_shortcuts:
            self._log("Cannot get desktop path: winshell is not available.")
            return None
        try:
            desktop = winshell.desktop()
            self._log(f"Successfully found desktop path: {desktop}")
            return Path(desktop)
        except Exception as e:
            self._log(f"ERROR: Could not get desktop path using winshell: {e}")
            self._log(traceback.format_exc())
            return None

    def create_desktop_shortcut(self) -> bool:
        """Tạo desktop shortcut cho AuraCrypt."""
        self._log("--- Starting shortcut creation process ---")
        if not self.can_create_shortcuts:
            self._log("Aborting: Cannot create shortcuts (not Windows or winshell/pywin32 missing).")
            return False

        # --- PHẦN SỬA LỖI QUAN TRỌNG ---
        # "Chào hỏi" hệ thống COM của Windows trước khi sử dụng
        pythoncom.CoInitialize()
        try:
            executable_path = self.get_executable_path()
            desktop_path = self.get_desktop_path()

            if not executable_path or not desktop_path:
                self._log("Aborting: Could not determine executable or desktop path.")
                return False

            shortcut_path = desktop_path / self.SHORTCUT_NAME
            self._log(f"Shortcut will be created at: {shortcut_path}")

            if shortcut_path.exists():
                self._log("Shortcut already exists. Process successful.")
                return True

            self._log("Dispatching 'WScript.Shell' COM object...")
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(str(shortcut_path))
            self._log("COM object created successfully.")

            shortcut.Targetpath = executable_path
            shortcut.WorkingDirectory = str(Path(executable_path).parent)
            shortcut.Description = "AuraCrypt - Secure Password Manager"

            # --- PHẦN SỬA LỖI TẠI ĐÂY ---
            # Thay vì tìm icon_path là file riêng, chúng ta sẽ chỉ dẫn nó đến icon
            # đã được nhúng trong chính tệp .exe.
            # Index 0 thường là icon chính của tệp .exe
            shortcut.IconLocation = executable_path + ",0"
            self._log(f"Icon location set to use executable's embedded icon: {executable_path},0")
            # --- KẾT THÚC SỬA LỖI ---

            self._log("Saving shortcut file...")
            shortcut.save()
            self._log("✅ Desktop shortcut created successfully.")
            return True

        except Exception as e:
            self._log(f"FATAL ERROR during shortcut creation: {e}")
            self._log(f"Full traceback:\n{traceback.format_exc()}")
            return False
        finally:
            # "Tạm biệt" hệ thống COM để dọn dẹp
            pythoncom.CoUninitialize()
        # --- KẾT THÚC SỬA LỖI ---


    def handle_first_run_setup(self):
        """Xử lý setup cho lần chạy đầu tiên, bao gồm tạo shortcut."""
        self._log("Handling first run setup...")
        if self.create_desktop_shortcut():
            self._log("Shortcut creation step successful.")
        else:
            self._log("Shortcut creation step failed.")

        self.mark_first_run_complete()
        self._log("First run setup process finished.")
