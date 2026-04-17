"""Identifier sensitivity classification."""

from typing import Dict, List


class SemanticAnalyzer:
    def __init__(self) -> None:
        self.sensitivity_rules = {
            "SECRET": ["key", "token", "secret", "password", "credential"],
            "VALUE": ["rate", "fee", "price", "commission", "threshold"],
        }

    def classify(self, identifier: Dict) -> str:
        name = identifier["name"].lower()
        typ = identifier["type"]
        if typ == "FUNCTION":
            return "FUNCTION"
        if any(p in name for p in self.sensitivity_rules["SECRET"]):
            return "SECRET"
        if any(p in name for p in self.sensitivity_rules["VALUE"]):
            return "VALUE"
        return "IDENTIFIER"

    def add_rule(self, category: str, patterns: List[str]) -> None:
        self.sensitivity_rules.setdefault(category, [])
        self.sensitivity_rules[category].extend([p.lower() for p in patterns])

    def classify_batch(self, identifiers: List[Dict]) -> List[Dict]:
        out: List[Dict] = []
        for item in identifiers:
            clone = dict(item)
            clone["sensitivity"] = self.classify(item)
            out.append(clone)
        return out

