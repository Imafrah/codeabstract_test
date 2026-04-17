"""Encrypted bidirectional mapping storage."""

import hashlib
import json
import uuid
from typing import Dict, Optional

from codeabstract.utils.database import load_session, store_session
from codeabstract.utils.encryption import decrypt_mapping, encrypt_mapping, load_or_generate_key


class BidirectionalMapper:
    def __init__(self, session_id: Optional[str] = None, privacy_level: str = "MEDIUM") -> None:
        self.session_id = session_id or str(uuid.uuid4())
        self.privacy_level = privacy_level
        self.encryption_key = load_or_generate_key()
        self.mapping_table: Dict[str, Dict] = {}
        self.reverse_table: Dict[str, str] = {}

    def add_mapping(self, abstract_symbol: str, element: Dict) -> None:
        payload = {
            "type": element["type"],
            "original_name": element["name"],
            "line_number": element["line_number"],
            "context": element.get("context", {}),
            "sensitivity": element["sensitivity"],
        }
        self.mapping_table[abstract_symbol] = payload
        self.reverse_table[payload["original_name"]] = abstract_symbol

    def lookup(self, abstract_symbol: str) -> Optional[Dict]:
        return self.mapping_table.get(abstract_symbol)

    def reverse_lookup(self, original_name: str) -> Optional[str]:
        return self.reverse_table.get(original_name)

    def save_encrypted(self, source_code: str, metadata: Dict) -> None:
        serialized = json.dumps(self.mapping_table).encode("utf-8")
        encrypted = encrypt_mapping(serialized, self.encryption_key)
        source_hash = hashlib.sha256(source_code.encode("utf-8")).hexdigest()
        store_session(self.session_id, self.privacy_level, source_hash, encrypted, metadata)

    def load_encrypted(self) -> None:
        session = load_session(self.session_id)
        if session is None:
            raise KeyError(f"Session not found: {self.session_id}")
        decrypted = decrypt_mapping(session["encrypted_mapping"], self.encryption_key)
        self.mapping_table = json.loads(decrypted.decode("utf-8"))
        self.reverse_table = {
            element["original_name"]: abstract_symbol
            for abstract_symbol, element in self.mapping_table.items()
        }

