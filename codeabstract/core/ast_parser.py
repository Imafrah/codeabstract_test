"""AST parsing and identifier extraction."""

import ast
from typing import Any, Dict, List


class ASTParser:
    """Parse code and extract symbols with metadata."""

    def parse(self, source_code: str) -> ast.AST:
        return ast.parse(source_code)

    def extract_identifiers(self, ast_tree: ast.AST) -> List[Dict[str, Any]]:
        identifiers: List[Dict[str, Any]] = []
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.FunctionDef):
                identifiers.append(
                    self._mk("FUNCTION", node.name, node.lineno, type(node).__name__, node)
                )
                for arg in node.args.args:
                    identifiers.append(self._mk("VARIABLE", arg.arg, node.lineno, "arg", arg))
            elif isinstance(node, ast.ClassDef):
                identifiers.append(
                    self._mk("CLASS", node.name, node.lineno, type(node).__name__, node)
                )
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        kind = "CONSTANT" if target.id.isupper() else "VARIABLE"
                        identifiers.append(
                            self._mk(kind, target.id, target.lineno, type(target).__name__, target)
                        )
        return identifiers

    def get_context(self, source_code: str, line_number: int, window: int = 3) -> Dict[str, Any]:
        lines = source_code.splitlines()
        start = max(1, line_number - window)
        end = min(len(lines), line_number + window)
        snippet = "\n".join(
            f"{idx:>3} | {lines[idx - 1]}" for idx in range(start, end + 1)
        )
        return {
            "snippet": snippet,
            "start_line": start,
            "end_line": end,
            "target_line": line_number,
        }

    @staticmethod
    def _mk(
        typ: str, name: str, line_number: int, ast_node_type: str, node: ast.AST
    ) -> Dict[str, Any]:
        return {
            "type": typ,
            "name": name,
            "line_number": line_number,
            "ast_node_type": ast_node_type,
            "node": node,
        }

