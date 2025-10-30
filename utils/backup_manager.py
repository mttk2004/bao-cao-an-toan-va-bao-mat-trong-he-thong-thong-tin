# auracrypt2/utils/backup_manager.py
"""
Automatic backup management for AuraCrypt vault.
Handles backup creation, restoration, and cleanup.
"""

import os
import shutil
import glob
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
from pathlib import Path
from core.constants import AppConstants


class BackupManager:
    """Manage automatic backups of the vault file."""

    def __init__(self, vault_path: str):
        """
        Initialize backup manager.

        Args:
            vault_path: Path to the main vault file
        """
        self.vault_path = vault_path
        self.backup_dir = os.path.join(os.path.dirname(vault_path), AppConstants.BACKUP_DIR)
        self.max_backups = 10  # Keep maximum 10 backups
        self.max_age_days = 30  # Keep backups for 30 days maximum

    def create_backup(self, backup_type: str = "manual") -> Tuple[bool, str, str]:
        """
        Create a backup of the vault file.

        Args:
            backup_type: Type of backup ('manual', 'auto', 'pre_import')

        Returns:
            Tuple of (success, backup_path, error_message)
        """
        try:
            # Check if vault file exists
            if not os.path.exists(self.vault_path):
                return False, "", "Vault file not found"

            # Create backup directory if it doesn't exist
            os.makedirs(self.backup_dir, exist_ok=True)

            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"vault_backup_{backup_type}_{timestamp}.dat"
            backup_path = os.path.join(self.backup_dir, backup_filename)

            # Copy vault file to backup location
            shutil.copy2(self.vault_path, backup_path)

            # Clean up old backups
            self._cleanup_old_backups()

            return True, backup_path, ""

        except Exception as e:
            return False, "", f"Failed to create backup: {str(e)}"

    def restore_backup(self, backup_path: str) -> Tuple[bool, str]:
        """
        Restore vault from a backup file.

        Args:
            backup_path: Path to the backup file

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Check if backup file exists
            if not os.path.exists(backup_path):
                return False, "Backup file not found"

            # Create a backup of current vault before restoring
            if os.path.exists(self.vault_path):
                current_backup_success, _, _ = self.create_backup("pre_restore")
                if not current_backup_success:
                    return False, "Failed to backup current vault before restore"

            # Restore from backup
            shutil.copy2(backup_path, self.vault_path)

            return True, ""

        except Exception as e:
            return False, f"Failed to restore backup: {str(e)}"

    def list_backups(self) -> List[dict]:
        """
        List all available backups with metadata.

        Returns:
            List of backup information dictionaries
        """
        backups = []

        if not os.path.exists(self.backup_dir):
            return backups

        try:
            # Find all backup files
            backup_pattern = os.path.join(self.backup_dir, "vault_backup_*.dat")
            backup_files = glob.glob(backup_pattern)

            for backup_file in backup_files:
                try:
                    # Extract information from filename
                    filename = os.path.basename(backup_file)
                    # Format: vault_backup_{type}_{timestamp}.dat
                    parts = filename.replace("vault_backup_", "").replace(".dat", "").split("_")

                    if len(parts) >= 3:
                        backup_type = parts[0]
                        date_str = parts[1]
                        time_str = parts[2]

                        # Parse timestamp
                        timestamp_str = f"{date_str}_{time_str}"
                        backup_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")

                        # Get file size
                        file_size = os.path.getsize(backup_file)

                        # Calculate age
                        age = datetime.now() - backup_date

                        backup_info = {
                            "path": backup_file,
                            "filename": filename,
                            "type": backup_type,
                            "date": backup_date,
                            "age_days": age.days,
                            "size_bytes": file_size,
                            "size_mb": round(file_size / (1024 * 1024), 2),
                            "formatted_date": backup_date.strftime("%Y-%m-%d %H:%M:%S"),
                            "relative_time": self._format_relative_time(age)
                        }

                        backups.append(backup_info)

                except Exception:
                    # Skip files that don't match expected format
                    continue

            # Sort by date (newest first)
            backups.sort(key=lambda x: x["date"], reverse=True)

        except Exception:
            # Return empty list if there's an error
            pass

        return backups

    def delete_backup(self, backup_path: str) -> Tuple[bool, str]:
        """
        Delete a specific backup file.

        Args:
            backup_path: Path to the backup file to delete

        Returns:
            Tuple of (success, error_message)
        """
        try:
            if not os.path.exists(backup_path):
                return False, "Backup file not found"

            # Ensure the file is in the backup directory for security
            if not backup_path.startswith(self.backup_dir):
                return False, "Invalid backup path"

            os.remove(backup_path)
            return True, ""

        except Exception as e:
            return False, f"Failed to delete backup: {str(e)}"

    def _cleanup_old_backups(self):
        """Clean up old backups based on count and age limits."""
        try:
            backups = self.list_backups()

            # Remove backups older than max_age_days
            cutoff_date = datetime.now() - timedelta(days=self.max_age_days)
            for backup in backups:
                if backup["date"] < cutoff_date:
                    try:
                        os.remove(backup["path"])
                    except:
                        pass  # Ignore errors when cleaning up

            # Re-get list after age cleanup
            backups = self.list_backups()

            # Keep only the most recent max_backups
            if len(backups) > self.max_backups:
                backups_to_delete = backups[self.max_backups:]
                for backup in backups_to_delete:
                    try:
                        os.remove(backup["path"])
                    except:
                        pass  # Ignore errors when cleaning up

        except Exception:
            # Ignore cleanup errors
            pass

    def _format_relative_time(self, time_delta: timedelta) -> str:
        """
        Format time delta as relative time string.

        Args:
            time_delta: Time difference from now

        Returns:
            Formatted relative time string
        """
        total_seconds = int(time_delta.total_seconds())

        if total_seconds < 60:
            return "just now"
        elif total_seconds < 3600:  # Less than 1 hour
            minutes = total_seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif total_seconds < 86400:  # Less than 1 day
            hours = total_seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = total_seconds // 86400
            return f"{days} day{'s' if days != 1 else ''} ago"

    def get_backup_summary(self) -> dict:
        """
        Get summary of backup status.

        Returns:
            Dictionary with backup summary information
        """
        backups = self.list_backups()

        if not backups:
            return {
                "total_backups": 0,
                "latest_backup": None,
                "total_size_mb": 0,
                "oldest_backup": None,
                "backup_types": {}
            }

        # Calculate statistics
        total_size = sum(backup["size_bytes"] for backup in backups)
        backup_types = {}

        for backup in backups:
            backup_type = backup["type"]
            if backup_type not in backup_types:
                backup_types[backup_type] = 0
            backup_types[backup_type] += 1

        return {
            "total_backups": len(backups),
            "latest_backup": backups[0] if backups else None,
            "oldest_backup": backups[-1] if backups else None,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "backup_types": backup_types
        }

    def should_create_auto_backup(self, last_backup_time: Optional[datetime] = None) -> bool:
        """
        Check if an automatic backup should be created.

        Args:
            last_backup_time: Time of last backup (if known)

        Returns:
            True if auto backup should be created
        """
        # If no last backup time provided, check the most recent backup
        if last_backup_time is None:
            backups = self.list_backups()
            if not backups:
                return True  # No backups exist, should create one

            latest_backup = backups[0]
            last_backup_time = latest_backup["date"]

        # Create auto backup if last backup is older than 24 hours
        time_since_backup = datetime.now() - last_backup_time
        return time_since_backup.total_seconds() > 86400  # 24 hours in seconds
