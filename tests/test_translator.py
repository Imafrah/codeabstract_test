from codeabstract.core.bidirectional_mapper import BidirectionalMapper
from codeabstract.core.reverse_translator import ReverseTranslator


def test_extract_symbols_and_translate():
    mapper = BidirectionalMapper()
    mapper.add_mapping(
        "FUNCTION_0",
        {
            "type": "FUNCTION",
            "name": "process_payment",
            "line_number": 10,
            "sensitivity": "FUNCTION",
            "context": {"snippet": " 10 | def process_payment(x):\n 11 |   return x"},
        },
    )
    translator = ReverseTranslator(mapper)
    assert translator.extract_abstract_symbols("Check FUNCTION_0")
    result = translator.translate("Bug in FUNCTION_0")
    assert "process_payment" in result

