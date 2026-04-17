"""Input validation helpers."""


def validate_python_source(source_code: str) -> None:
    if not source_code or not source_code.strip():
        raise ValueError("source_code must not be empty")

