# auracrypt2/utils/data_exporter.py
"""
Data export and import functionality for AuraCrypt.
Supports JSON and CSV formats with secure handling.
"""

import json
import csv
import io
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from utils.app_types import EntryData, ValidationResult
from utils.validators import EntryValidator
from core.constants import AppConstants


class DataExporter:
    """Export password entries to various formats."""

    @staticmethod
    def export_to_json(
        entries: List[EntryData],
        include_passwords: bool = False,
        include_metadata: bool = True
    ) -> str:
        """
        Export entries to JSON format.

        Args:
            entries: List of password entries
            include_passwords: Whether to include passwords in export
            include_metadata: Whether to include export metadata

        Returns:
            JSON string containing the exported data
        """
        export_data = {
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "version": AppConstants.APP_VERSION,
                "total_entries": len(entries),
                "includes_passwords": include_passwords
            } if include_metadata else {},
            "entries": []
        }

        for entry in entries:
            export_entry = {
                "service": entry.get("service", ""),
                "username": entry.get("username", ""),
                "url": entry.get("url", ""),
                "notes": entry.get("notes", ""),
                "category": entry.get("category", AppConstants.DEFAULT_CATEGORY),
                "created_date": entry.get("created_date", ""),
                "modified_date": entry.get("modified_date", "")
            }

            if include_passwords:
                export_entry["password"] = entry.get("password", "")

            export_data["entries"].append(export_entry)

        return json.dumps(export_data, indent=2, ensure_ascii=False)

    @staticmethod
    def export_to_csv(
        entries: List[EntryData],
        include_passwords: bool = False
    ) -> str:
        """
        Export entries to CSV format.

        Args:
            entries: List of password entries
            include_passwords: Whether to include passwords in export

        Returns:
            CSV string containing the exported data
        """
        output = io.StringIO()

        fieldnames = ["service", "username", "url", "notes", "category"]
        if include_passwords:
            fieldnames.insert(2, "password")

        writer = csv.DictWriter(output, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()

        for entry in entries:
            row = {
                "service": entry.get("service", ""),
                "username": entry.get("username", ""),
                "url": entry.get("url", ""),
                "notes": entry.get("notes", ""),
                "category": entry.get("category", AppConstants.DEFAULT_CATEGORY)
            }

            if include_passwords:
                row["password"] = entry.get("password", "")

            writer.writerow(row)

        return output.getvalue()

    @staticmethod
    def save_export_to_file(
        data: str,
        file_path: str,
        format_type: str = "json"
    ) -> Tuple[bool, str]:
        """
        Save exported data to file.

        Args:
            data: Exported data string
            file_path: Path to save the file
            format_type: Type of format (json/csv)

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(data)

            return True, ""
        except Exception as e:
            return False, f"Failed to save {format_type.upper()} file: {str(e)}"


class DataImporter:
    """Import password entries from various formats."""

    @staticmethod
    def import_from_json(json_data: str) -> Tuple[List[EntryData], List[str]]:
        """
        Import entries from JSON format.

        Args:
            json_data: JSON string containing the data

        Returns:
            Tuple of (imported_entries, error_messages)
        """
        try:
            data = json.loads(json_data)
            entries = []
            errors = []

            # Handle both old format (direct list) and new format (with metadata)
            if isinstance(data, list):
                entries_data = data
            elif isinstance(data, dict) and "entries" in data:
                entries_data = data["entries"]
            else:
                return [], ["Invalid JSON format: expected list of entries or object with 'entries' key"]

            for i, entry_data in enumerate(entries_data):
                try:
                    # Validate required fields
                    if not isinstance(entry_data, dict):
                        errors.append(f"Entry {i+1}: Invalid entry format")
                        continue

                    if not entry_data.get("service"):
                        errors.append(f"Entry {i+1}: Service name is required")
                        continue

                    # Create clean entry
                    clean_entry: EntryData = {
                        "service": str(entry_data.get("service", "")).strip(),
                        "username": str(entry_data.get("username", "")).strip(),
                        "password": str(entry_data.get("password", "")).strip(),
                        "url": str(entry_data.get("url", "")).strip(),
                        "notes": str(entry_data.get("notes", "")).strip(),
                        "category": str(entry_data.get("category", AppConstants.DEFAULT_CATEGORY)).strip()
                    }

                    # Validate entry data
                    validation_result = EntryValidator.validate_entry_data(clean_entry)
                    if not validation_result.is_valid:
                        errors.append(f"Entry {i+1} ({clean_entry['service']}): {validation_result.error_message}")
                        continue

                    entries.append(clean_entry)

                except Exception as e:
                    errors.append(f"Entry {i+1}: Error processing entry - {str(e)}")

            return entries, errors

        except json.JSONDecodeError as e:
            return [], [f"Invalid JSON format: {str(e)}"]
        except Exception as e:
            return [], [f"Error importing JSON: {str(e)}"]

    @staticmethod
    def import_from_csv(csv_data: str) -> Tuple[List[EntryData], List[str]]:
        """
        Import entries from CSV format.

        Args:
            csv_data: CSV string containing the data

        Returns:
            Tuple of (imported_entries, error_messages)
        """
        try:
            entries = []
            errors = []

            # Parse CSV
            csv_file = io.StringIO(csv_data)
            reader = csv.DictReader(csv_file)

            if not reader.fieldnames:
                return [], ["CSV file appears to be empty or invalid"]

            # Check for required fields
            required_field = "service"
            if required_field not in reader.fieldnames:
                return [], [f"CSV must contain '{required_field}' column"]

            for i, row in enumerate(reader, start=2):  # Start from 2 because header is row 1
                try:
                    # Skip empty rows
                    if not any(row.values()):
                        continue

                    service = str(row.get("service", "")).strip()
                    if not service:
                        errors.append(f"Row {i}: Service name is required")
                        continue

                    # Create clean entry
                    clean_entry: EntryData = {
                        "service": service,
                        "username": str(row.get("username", "")).strip(),
                        "password": str(row.get("password", "")).strip(),
                        "url": str(row.get("url", "")).strip(),
                        "notes": str(row.get("notes", "")).strip(),
                        "category": str(row.get("category", AppConstants.DEFAULT_CATEGORY)).strip()
                    }

                    # Validate entry data
                    validation_result = EntryValidator.validate_entry_data(clean_entry)
                    if not validation_result.is_valid:
                        errors.append(f"Row {i} ({clean_entry['service']}): {validation_result.error_message}")
                        continue

                    entries.append(clean_entry)

                except Exception as e:
                    errors.append(f"Row {i}: Error processing row - {str(e)}")

            return entries, errors

        except Exception as e:
            return [], [f"Error importing CSV: {str(e)}"]

    @staticmethod
    def load_file_content(file_path: str) -> Tuple[bool, str, str]:
        """
        Load content from file.

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (success, content, error_message)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return True, content, ""
        except Exception as e:
            return False, "", f"Failed to read file: {str(e)}"

    @staticmethod
    def detect_format(content: str, file_extension: str = "") -> str:
        """
        Detect the format of the content.

        Args:
            content: Content to analyze
            file_extension: File extension hint

        Returns:
            Detected format ('json', 'csv', or 'unknown')
        """
        content = content.strip()

        # Check file extension first
        if file_extension.lower() in ['.json', '.txt']:
            if content.startswith('{') or content.startswith('['):
                return 'json'
        elif file_extension.lower() == '.csv':
            return 'csv'

        # Try to detect from content
        if content.startswith('{') or content.startswith('['):
            try:
                json.loads(content)
                return 'json'
            except:
                pass

        # Check if it looks like CSV
        if ',' in content and '\n' in content:
            lines = content.split('\n')
            if len(lines) > 1:
                # Check if first line looks like headers
                first_line = lines[0].lower()
                if any(field in first_line for field in ['service', 'username', 'password', 'url']):
                    return 'csv'

        return 'unknown'


class SecureExportHandler:
    """Handle secure export operations with user warnings."""

    @staticmethod
    def get_export_warnings(include_passwords: bool, entry_count: int) -> List[str]:
        """
        Get warnings for export operation.

        Args:
            include_passwords: Whether passwords will be included
            entry_count: Number of entries being exported

        Returns:
            List of warning messages
        """
        warnings = []

        if include_passwords:
            warnings.append("⚠️ This export will include passwords in plain text")
            warnings.append("🔒 Store the exported file securely")
            warnings.append("🗑️ Delete the file after use if possible")

        warnings.append(f"📊 {entry_count} entries will be exported")

        if entry_count > 100:
            warnings.append("📈 Large export - this may take a moment")

        return warnings

    @staticmethod
    def get_import_warnings(entry_count: int, has_errors: bool) -> List[str]:
        """
        Get warnings for import operation.

        Args:
            entry_count: Number of entries being imported
            has_errors: Whether there were validation errors

        Returns:
            List of warning messages
        """
        warnings = []

        warnings.append(f"📥 {entry_count} entries ready to import")

        if has_errors:
            warnings.append("⚠️ Some entries had validation errors and were skipped")

        if entry_count > 50:
            warnings.append("📈 Large import - this may take a moment")
            warnings.append("💾 Consider creating a backup before importing")

        return warnings
