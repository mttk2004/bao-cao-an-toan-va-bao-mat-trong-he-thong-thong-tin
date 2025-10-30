# auracrypt/core/vault.py
# This module manages the storage of the encrypted vault file ("vault.dat").

import os
import base64
import json
import shutil
from pathlib import Path
from . import crypto
from utils.file_paths import AppPaths

# Initialize AppPaths instance
app_paths = AppPaths()

def _get_active_vault_path() -> Path:
    """
    Returns the path to the active vault file, handling migration if needed.
    """
    new_vault_path = app_paths.get_vault_path()
    legacy_vault_path = app_paths.get_legacy_vault_path()

    # If new location exists, use it
    if new_vault_path.exists():
        return new_vault_path

    # If legacy location exists, migrate it
    if legacy_vault_path.exists():
        # Ensure the new directory exists
        new_vault_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy the file to the new location
        shutil.copy2(legacy_vault_path, new_vault_path)

        # Return the new path
        return new_vault_path

    # Neither exists, return new path for creation
    return new_vault_path

def vault_exists() -> bool:
    """Checks if the vault file exists in the appropriate directory."""
    # Check new location first
    if app_paths.get_vault_path().exists():
        return True

    # Check legacy location for backward compatibility
    return app_paths.get_legacy_vault_path().exists()

def create_vault(master_password: str, initial_data: dict = None):
    """
    Creates a new, encrypted vault file.

    This function takes the master password, encrypts the initial data,
    and stores it in the `vault.dat` file in a JSON format. The salt, nonce,
    and ciphertext are Base64 encoded for safe storage in the JSON file.

    Args:
        master_password: The password to protect the vault.
        initial_data: The initial data to store. If None, an empty list of entries is created.
    """
    if initial_data is None:
        initial_data = {"entries": []}

    # Ensure app directories exist
    app_paths.ensure_app_dirs()

    # Encrypt the data using the crypto module.
    salt, nonce, ciphertext = crypto.encrypt_data(master_password, initial_data)

    # Prepare the content for the JSON file. Binary data is encoded in Base64.
    vault_content = {
        "salt": base64.b64encode(salt).decode('utf-8'),
        "nonce": base64.b64encode(nonce).decode('utf-8'),
        "ciphertext": base64.b64encode(ciphertext).decode('utf-8')
    }

    # Write the JSON structure to the vault file.
    vault_path = app_paths.get_vault_path()
    with open(vault_path, 'w') as f:
        json.dump(vault_content, f, indent=2)

def save_vault(master_password: str, data: dict):
    """
    Saves the entire vault data by re-encrypting it with a new salt and nonce.

    For security, every save operation re-encrypts the data completely, which
    generates a new salt and nonce. This is more secure than reusing them.
    This function essentially overwrites the old vault file with the newly encrypted data.

    Args:
        master_password: The master password for encryption.
        data: The full, unencrypted vault data to save.
    """
    # Re-encrypting is the same process as creating a new vault with the new data.
    create_vault(master_password, data)

def load_vault(master_password: str) -> dict:
    """
    Loads and decrypts the vault data from the `vault.dat` file.

    It reads the Base64 encoded salt, nonce, and ciphertext, decodes them,
    and then passes them to the crypto module for decryption.

    Args:
        master_password: The master password to try and decrypt the vault with.

    Returns:
        The decrypted vault data as a dictionary.

    Raises:
        FileNotFoundError: If the vault file does not exist.
        ValueError: If the file is corrupt or if decryption fails (e.g., wrong password).
    """
    if not vault_exists():
        raise FileNotFoundError("Vault file not found.")

    # Determine which vault file to use (migrate if needed)
    vault_path = _get_active_vault_path()

    try:
        # Read the JSON content from the vault file.
        with open(vault_path, 'r') as f:
            vault_content = json.load(f)

        # Decode the Base64 data back into bytes.
        salt = base64.b64decode(vault_content['salt'])
        nonce = base64.b64decode(vault_content['nonce'])
        ciphertext = base64.b64decode(vault_content['ciphertext'])

        # Attempt to decrypt the data.
        return crypto.decrypt_data(master_password, salt, nonce, ciphertext)

    except (json.JSONDecodeError, KeyError) as e:
        # This block catches errors related to a malformed or corrupt vault file.
        # e.g., not valid JSON, or missing 'salt', 'nonce', 'ciphertext' keys.
        handle_corrupted_vault(vault_path)
        corrupted_file = str(vault_path) + ".corrupted"
        raise ValueError(f"Vault file is corrupt and has been renamed to '{corrupted_file}'.") from e

    except ValueError as e:
        # This propagates decryption errors from crypto.decrypt_data (e.g., wrong password).
        # We also check if the error message implies corruption to rename the file.
        if "corrupt" in str(e).lower():
             handle_corrupted_vault(vault_path)
        raise e # Re-raise the original, more specific error.

def handle_corrupted_vault(vault_path: Path = None):
    """
    Renames a corrupted vault file to `vault.dat.corrupted` for safety.
    This prevents the application from trying to read a known-bad file again
    and preserves it for potential manual recovery.

    Args:
        vault_path: The path to the corrupted vault file. If None, uses active vault path.
    """
    if vault_path is None:
        vault_path = _get_active_vault_path()

    corrupted_path = Path(str(vault_path) + ".corrupted")

    if vault_path.exists():
        if corrupted_path.exists():
             corrupted_path.unlink() # Remove old corrupted file before renaming
        vault_path.rename(corrupted_path)
