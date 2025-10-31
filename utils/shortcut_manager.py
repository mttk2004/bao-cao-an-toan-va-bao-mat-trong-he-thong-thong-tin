# utils/shortcut_manager.py
# Module to manage creation of desktop shortcuts for Windows

import os
import sys
import platform
import traceback
from pathlib import Path
from typing import Optional

try:
    import winshell
    from win32com.client import Dispatch
    import pythoncom
    WINSHELL_AVAILABLE = True
except ImportError:
    winshell = None
    Dispatch = None
    pythoncom = None
    WINSHELL_AVAILABLE = False

try:
    from .file_paths import AppPaths
except ImportError:
    # Fallback for standalone execution
    from file_paths import AppPaths


class ShortcutManager:
    """
    Manage creation and verification of a desktop shortcut for AuraCrypt.
    Operates only on Windows and when winshell/pywin32 are available.
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
        """Write a message to the debug log file."""
        try:
            with open(self.log_path, 'a', encoding='utf-8') as f:
                from datetime import datetime
                f.write(f"[{datetime.now().isoformat()}] {message}\n")
        except Exception:
            pass

    def get_first_run_marker_path(self) -> Path:
        """Return the path to the first-run marker file."""
        return self.app_paths.get_app_data_dir() / self.FIRST_RUN_MARKER

    def is_first_run(self) -> bool:
        """Check whether this is the application's first run.

        Returns:
            True if this is the first run (marker file missing), False otherwise.
        """
        return not self.get_first_run_marker_path().exists()

    def mark_first_run_complete(self) -> None:
        """Create the marker file indicating first-run setup has completed."""
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
        """Return the path to the current executable or main script.

        If running as a frozen executable (PyInstaller/Flet), returns sys.executable.
        Otherwise returns the resolved path to the project's main.py script.
        """
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
        """Return the current user's Desktop path.

        Uses winshell when available; falls back to ~/Desktop if needed.
        """
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
        """Create a desktop shortcut for AuraCrypt.

        Returns True on success, False on failure.
        """
        self._log("--- Starting shortcut creation process ---")
        if not self.can_create_shortcuts:
            self._log("Aborting: Cannot create shortcuts (not Windows or winshell/pywin32 missing).")
            return False

        # Initialize the Windows COM subsystem before use
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

            # Use the executable's embedded icon (index 0) instead of a separate icon file.
            shortcut.IconLocation = executable_path + ",0"
            self._log(f"Icon location set to use executable's embedded icon: {executable_path},0")

            self._log("Saving shortcut file...")
            shortcut.save()
            self._log("✅ Desktop shortcut created successfully.")
            return True

        except Exception as e:
            self._log(f"FATAL ERROR during shortcut creation: {e}")
            self._log(f"Full traceback:\n{traceback.format_exc()}")
            return False
        finally:
            # Uninitialize the COM subsystem to clean up
            pythoncom.CoUninitialize()

    def handle_first_run_setup(self):
        """Perform first-run setup, including shortcut creation.

        This will attempt to create the desktop shortcut and then write the
        first-run marker file regardless of the shortcut outcome.
        """
        self._log("Handling first run setup...")
        if self.create_desktop_shortcut():
            self._log("Shortcut creation step successful.")
        else:
            self._log("Shortcut creation step failed.")

        # Always mark first-run complete to avoid repeated attempts
        self.mark_first_run_complete()
        self._log("First run setup process finished.")
