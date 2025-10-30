# auracrypt2/utils/file_paths.py
"""
Cross-platform file path management for AuraCrypt.
Handles application data storage according to OS conventions.
"""

import os
import sys
from pathlib import Path
from typing import Optional
from core.constants import AppConstants


class AppPaths:
    """Manages application file paths across different operating systems."""

    @staticmethod
    def get_app_data_dir() -> Path:
        """
        Get the appropriate application data directory for the current OS.

        Windows: %APPDATA%/AuraCrypt
        macOS: ~/Library/Application Support/AuraCrypt
        Linux: ~/.config/auracrypt

        Returns:
            Path to application data directory
        """
        app_name = "auracrypt"  # lowercase for Linux compatibility

        if sys.platform == "win32":
            # Windows: %APPDATA%/AuraCrypt
            base_dir = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
            return base_dir / "AuraCrypt"

        elif sys.platform == "darwin":
            # macOS: ~/Library/Application Support/AuraCrypt
            return Path.home() / "Library" / "Application Support" / "AuraCrypt"

        else:
            # Linux and other Unix-like: ~/.config/auracrypt
            config_home = os.environ.get("XDG_CONFIG_HOME")
            if config_home:
                return Path(config_home) / app_name
            else:
                return Path.home() / ".config" / app_name

    @staticmethod
    def get_vault_path() -> Path:
        """
        Get the full path to the vault file.

        Returns:
            Path to vault file
        """
        return AppPaths.get_app_data_dir() / AppConstants.VAULT_FILE

    @staticmethod
    def get_backup_dir() -> Path:
        """
        Get the backup directory path.

        Returns:
            Path to backup directory
        """
        return AppPaths.get_app_data_dir() / AppConstants.BACKUP_DIR

    @staticmethod
    def get_config_path() -> Path:
        """
        Get the configuration file path.

        Returns:
            Path to config file
        """
        return AppPaths.get_app_data_dir() / "config.json"

    @staticmethod
    def get_logs_dir() -> Path:
        """
        Get the logs directory path.

        Returns:
            Path to logs directory
        """
        return AppPaths.get_app_data_dir() / "logs"

    @staticmethod
    def ensure_app_dirs():
        """
        Ensure all necessary application directories exist.
        Creates directories if they don't exist.
        """
        directories = [
            AppPaths.get_app_data_dir(),
            AppPaths.get_backup_dir(),
            AppPaths.get_logs_dir()
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_legacy_vault_path() -> Path:
        """
        Get the legacy vault path (same directory as main.py).
        Used for migration from old installations.

        Returns:
            Path to legacy vault file
        """
        # Get the directory where the script is located
        if hasattr(sys, '_MEIPASS'):
            # Running as PyInstaller bundle
            script_dir = Path(sys.executable).parent
        else:
            # Running as script
            script_dir = Path(__file__).parent.parent

        return script_dir / AppConstants.VAULT_FILE

    @staticmethod
    def migrate_legacy_vault() -> bool:
        """
        Migrate vault from legacy location to new location.

        Returns:
            True if migration was successful or not needed, False if failed
        """
        legacy_path = AppPaths.get_legacy_vault_path()
        new_path = AppPaths.get_vault_path()

        # If new vault already exists, no migration needed
        if new_path.exists():
            return True

        # If legacy vault doesn't exist, no migration needed
        if not legacy_path.exists():
            return True

        try:
            # Ensure target directory exists
            AppPaths.ensure_app_dirs()

            # Copy legacy vault to new location
            import shutil
            shutil.copy2(legacy_path, new_path)

            # Also migrate backup directory if it exists
            legacy_backup_dir = legacy_path.parent / AppConstants.BACKUP_DIR
            if legacy_backup_dir.exists():
                new_backup_dir = AppPaths.get_backup_dir()
                # Copy all backup files
                for backup_file in legacy_backup_dir.glob("vault_backup_*.dat"):
                    shutil.copy2(backup_file, new_backup_dir / backup_file.name)

            return True

        except Exception as e:
            print(f"Failed to migrate legacy vault: {e}")
            return False

    @staticmethod
    def get_export_dir() -> Path:
        """
        Get the default export directory.
        Uses Documents folder or home directory.

        Returns:
            Path to export directory
        """
        if sys.platform == "win32":
            # Windows: Documents folder
            docs_dir = Path.home() / "Documents"
            if docs_dir.exists():
                return docs_dir / "AuraCrypt Exports"

        # Fallback to home directory
        return Path.home() / "AuraCrypt Exports"

    @staticmethod
    def get_temp_dir() -> Path:
        """
        Get temporary directory for AuraCrypt operations.

        Returns:
            Path to temp directory
        """
        import tempfile
        return Path(tempfile.gettempdir()) / "auracrypt_temp"
