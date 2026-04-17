"""Encryption utilities for mapping payloads."""

from cryptography.fernet import Fernet

from codeabstract.config.settings import KEY_PATH


def load_or_generate_key() -> bytes:
    """Load key from disk or create one if missing."""
    if KEY_PATH.exists():
        return KEY_PATH.read_bytes()
    key = Fernet.generate_key()
    KEY_PATH.write_bytes(key)
    return key


def encrypt_mapping(payload: bytes, key: bytes) -> bytes:
    """Encrypt serialized mapping payload."""
    return Fernet(key).encrypt(payload)


def decrypt_mapping(payload: bytes, key: bytes) -> bytes:
    """Decrypt serialized mapping payload."""
    return Fernet(key).decrypt(payload)

