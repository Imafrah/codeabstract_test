from codeabstract.core.bidirectional_mapper import BidirectionalMapper


def test_add_lookup_reverse_lookup():
    mapper = BidirectionalMapper()
    mapper.add_mapping(
        "FUNCTION_0",
        {"type": "FUNCTION", "name": "process", "line_number": 3, "sensitivity": "FUNCTION"},
    )
    assert mapper.lookup("FUNCTION_0")["original_name"] == "process"
    assert mapper.reverse_lookup("process") == "FUNCTION_0"

