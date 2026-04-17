"""IR generation by AST transformation."""

import ast
from typing import Dict, List

import astor


class IdentifierTransformer(ast.NodeTransformer):
    def __init__(self, symbol_map: Dict[str, str]) -> None:
        self.symbol_map = symbol_map

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        if node.name in self.symbol_map:
            node.name = self.symbol_map[node.name]
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        if node.name in self.symbol_map:
            node.name = self.symbol_map[node.name]
        self.generic_visit(node)
        return node

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id in self.symbol_map:
            node.id = self.symbol_map[node.id]
        return node

    def visit_arg(self, node: ast.arg) -> ast.AST:
        if node.arg in self.symbol_map:
            node.arg = self.symbol_map[node.arg]
        return node


class IRGenerator:
    def __init__(self) -> None:
        self.symbol_counters = {"SECRET": 0, "VALUE": 0, "FUNCTION": 0, "IDENTIFIER": 0}
        self.symbol_map: Dict[str, str] = {}

    def generate(self, ast_tree: ast.AST, classified_elements: List[Dict]) -> str:
        # Deterministic mapping: assign abstract symbols in a stable order
        # so that translating from `source_code` works reliably across calls.
        ordered = sorted(
            classified_elements,
            key=lambda e: (
                e.get("line_number", 0),
                e.get("sensitivity", "IDENTIFIER"),
                e.get("type", ""),
                e.get("name", ""),
            ),
        )
        for element in ordered:
            original = element["name"]
            if original not in self.symbol_map:
                self.symbol_map[original] = self.create_abstract_symbol(element)
        transformed = self.transform_ast(ast_tree)
        return self.unparse_ast(transformed)

    def create_abstract_symbol(self, element: Dict) -> str:
        sensitivity = element["sensitivity"]
        idx = self.symbol_counters[sensitivity]
        self.symbol_counters[sensitivity] += 1
        if sensitivity == "SECRET":
            return f"SECRET_KEY_{idx}"
        if sensitivity == "VALUE":
            return f"VALUE_{idx}"
        if sensitivity == "FUNCTION":
            return f"FUNCTION_{idx}"
        return f"VAR_{idx}"

    def transform_ast(self, ast_tree: ast.AST) -> ast.AST:
        return IdentifierTransformer(self.symbol_map).visit(ast_tree)

    def unparse_ast(self, ast_tree: ast.AST) -> str:
        return astor.to_source(ast.fix_missing_locations(ast_tree))

