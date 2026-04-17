from codeabstract.core.ast_parser import ASTParser
from codeabstract.core.ir_generator import IRGenerator
from codeabstract.core.semantic_analyzer import SemanticAnalyzer


def test_generate_abstract_symbols():
    src = "api_key = 1\ndef process(v):\n    return v + api_key\n"
    parser = ASTParser()
    tree = parser.parse(src)
    classified = SemanticAnalyzer().classify_batch(parser.extract_identifiers(tree))
    generator = IRGenerator()
    abstract_code = generator.generate(tree, classified)
    assert "FUNCTION_" in abstract_code
    assert "SECRET_KEY_" in abstract_code or "VAR_" in abstract_code

