from codeabstract.core.ast_parser import ASTParser


SAMPLE = """
API_KEY = "x"
commission_rate = 0.2

def calc(amount):
    return amount * commission_rate
"""


def test_parse_valid_code():
    parser = ASTParser()
    tree = parser.parse(SAMPLE)
    assert tree is not None


def test_extract_functions_variables():
    parser = ASTParser()
    identifiers = parser.extract_identifiers(parser.parse(SAMPLE))
    names = {item["name"] for item in identifiers}
    assert "calc" in names
    assert "commission_rate" in names


def test_get_context_snippet():
    parser = ASTParser()
    ctx = parser.get_context(SAMPLE, 5)
    assert "calc" in ctx["snippet"]

