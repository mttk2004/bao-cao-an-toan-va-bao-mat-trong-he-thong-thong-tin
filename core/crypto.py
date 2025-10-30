# auracrypt/core/crypto.py
# This module handles all core cryptographic operations for the application.

import os
import base64
import json
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # type: ignore
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC  # type: ignore
    from cryptography.hazmat.primitives import hashes  # type: ignore
    from cryptography.hazmat.backends import default_backend  # type: ignore
    from cryptography.exceptions import InvalidKey  # type: ignore
except Exception as e:
    raise ImportError(
        "The 'cryptography' library is required but not available; install it with "
        "'pip install cryptography' and ensure your virtual environment is active. "
        f"Original error: {e}"
    )

# --- Constants ---
SALT_SIZE = 16  # Size of the salt in bytes. 16 bytes is recommended.
KEY_SIZE = 32   # Key size for AES-256. 32 bytes = 256 bits.
ITERATIONS = 480_000 # Number of iterations for PBKDF2. Higher is more secure. OWASP recommendation (2023).
AES_NONCE_SIZE = 12 # Size of the nonce for AES-GCM. 12 bytes is standard.

# Use the default cryptography backend.
backend = default_backend()

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derives a cryptographic key from a master password and a salt using PBKDF2.

    PBKDF2 (Password-Based Key Derivation Function 2) is used to "stretch" the password,
    making brute-force attacks much slower.

    Args:
        password: The user's master password.
        salt: A random salt unique to each vault.

    Returns:
        A derived key of KEY_SIZE bytes.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=ITERATIONS,
        backend=backend
    )
    # The password is encoded to UTF-8 before derivation.
    return kdf.derive(password.encode('utf-8'))

def encrypt_data(password: str, data: dict) -> tuple[bytes, bytes, bytes]:
    """
    Encrypts the vault data. This function performs the entire encryption pipeline:
    1. Generates a new random salt.
    2. Derives an encryption key from the password and salt.
    3. Generates a new random nonce (IV).
    4. Encrypts the data using AES-256-GCM.

    Args:
        password: The master password.
        data: The vault data to be encrypted (as a Python dictionary).

    Returns:
        A tuple containing the salt, nonce, and the resulting ciphertext.
    """
    # 1. Generate a cryptographically secure random salt.
    salt = os.urandom(SALT_SIZE)

    # 2. Derive the encryption key.
    key = derive_key(password, salt)

    # 3. Generate a cryptographically secure random nonce. A new nonce must be used for every encryption.
    nonce = os.urandom(AES_NONCE_SIZE)

    # 4. Encrypt using AES-GCM.
    # AES-GCM is an authenticated encryption mode. It not only provides confidentiality
    # but also provides an authentication tag that can be used to verify the integrity
    # and authenticity of the data upon decryption.
    aesgcm = AESGCM(key)

    # The data dictionary is first serialized into a JSON string, then encoded to bytes.
    plaintext = json.dumps(data).encode('utf-8')
    ciphertext = aesgcm.encrypt(nonce, plaintext, None) # No additional authenticated data (AAD)

    return salt, nonce, ciphertext

def decrypt_data(password: str, salt: bytes, nonce: bytes, ciphertext: bytes) -> dict:
    """
    Decrypts the vault data. This function reverses the encryption process:
    1. Derives the encryption key from the provided password and salt.
    2. Attempts to decrypt the ciphertext using the derived key and nonce.
    3. If decryption is successful, it deserializes the JSON data back into a Python dictionary.

    Args:
        password: The master password entered by the user.
        salt: The salt that was used during encryption (read from the vault file).
        nonce: The nonce that was used during encryption.
        ciphertext: The encrypted data.

    Returns:
        The decrypted vault data as a Python dictionary.

    Raises:
        ValueError: If decryption fails. This is critical because AES-GCM's authentication
                    check will fail if the password is wrong or the data has been tampered with.
    """
    # 1. Derive the key using the same parameters as encryption.
    key = derive_key(password, salt)

    # 2. Initialize AES-GCM for decryption.
    aesgcm = AESGCM(key)

    try:
        # 3. Attempt to decrypt. If the key is wrong or the ciphertext/tag is corrupt,
        # the cryptography library will raise an InvalidKey exception.
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)

        # 4. Deserialize the JSON data.
        return json.loads(plaintext.decode('utf-8'))

    except InvalidKey:
        # This is a critical security check. It indicates authentication failure.
        raise ValueError("Decryption failed. Master password may be incorrect or data is corrupt.")
    except Exception as e:
        # Catch other potential errors, e.g., JSON decoding.
        raise ValueError(f"An unexpected error occurred during decryption: {e}")
