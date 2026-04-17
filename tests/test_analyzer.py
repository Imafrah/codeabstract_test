from codeabstract.core.semantic_analyzer import SemanticAnalyzer


def test_classify_secret():
    analyzer = SemanticAnalyzer()
    assert analyzer.classify({"name": "STRIPE_API_KEY", "type": "VARIABLE"}) == "SECRET"


def test_classify_value():
    analyzer = SemanticAnalyzer()
    assert analyzer.classify({"name": "commission_rate", "type": "VARIABLE"}) == "VALUE"


def test_classify_function():
    analyzer = SemanticAnalyzer()
    assert analyzer.classify({"name": "process", "type": "FUNCTION"}) == "FUNCTION"

