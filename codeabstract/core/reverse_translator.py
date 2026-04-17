"""Reverse-translate abstract LLM responses into original context."""

import re
from typing import Dict, List

from codeabstract.core.bidirectional_mapper import BidirectionalMapper


class ReverseTranslator:
    def __init__(self, mapper: BidirectionalMapper):
        self.mapper = mapper

    def extract_abstract_symbols(self, text: str) -> List[str]:
        """Find abstract symbols like FUNCTION_0, VAR_1, SECRET_KEY_2."""
        pattern = r"\b(?:SECRET_KEY|VALUE|FUNCTION|VAR)_\d+\b"
        return sorted(set(re.findall(pattern, text)))

    def create_context_block(self, symbol: str, element: Dict) -> str:
        """Create a formatted context block for one symbol."""
        line = element["line_number"]
        snippet = element.get("context", {}).get("snippet", "")
        header = f"- **{element['original_name']} (line {line})**  "
        return f"{header}\n{snippet}"

    def translate(self, llm_response: str) -> str:
        """
        Replace abstract symbols with original names in the free text
        and append formatted context blocks for each symbol.
        """
        translated = llm_response
        symbols = self.extract_abstract_symbols(llm_response)
        context_blocks: List[str] = []

        for symbol in symbols:
            element = self.mapper.lookup(symbol)
            if not element:
                continue
            # Replace symbol occurrences with original identifier name
            translated = translated.replace(symbol, element["original_name"])
            context_blocks.append(self.create_context_block(symbol, element))

        if context_blocks:
            translated = translated.rstrip() + "\n\n\nAffected code:\n" + "\n\n".join(
                context_blocks
            )
        return translated

