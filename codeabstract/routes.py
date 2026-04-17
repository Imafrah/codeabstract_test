"""FastAPI route handlers."""

from fastapi import APIRouter, HTTPException

from codeabstract.core.ast_parser import ASTParser
from codeabstract.core.bidirectional_mapper import BidirectionalMapper
from codeabstract.core.ir_generator import IRGenerator
from codeabstract.core.reverse_translator import ReverseTranslator
from codeabstract.core.semantic_analyzer import SemanticAnalyzer
from codeabstract.models import (
    AbstractRequest,
    AbstractResponse,
    TranslateRequest,
    TranslateFromOriginalRequest,
    TranslateResponse,
)
from codeabstract.utils.database import init_db, load_session
from codeabstract.utils.validation import validate_python_source

router = APIRouter()
init_db()


@router.post("/api/v1/abstract", response_model=AbstractResponse)
async def abstract_code(request: AbstractRequest) -> AbstractResponse:
    try:
        validate_python_source(request.source_code)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    parser = ASTParser()
    analyzer = SemanticAnalyzer()
    generator = IRGenerator()
    mapper = BidirectionalMapper(privacy_level=request.privacy_level)

    tree = parser.parse(request.source_code)
    identifiers = parser.extract_identifiers(tree)
    classified = analyzer.classify_batch(identifiers)
    for item in classified:
        item["context"] = parser.get_context(request.source_code, item["line_number"])

    abstract_code_value = generator.generate(tree, classified)
    for item in classified:
        symbol = generator.symbol_map.get(item["name"])
        if symbol:
            mapper.add_mapping(symbol, item)

    metadata = {"identifier_count": len(classified), "symbol_count": len(mapper.mapping_table)}
    mapper.save_encrypted(request.source_code, metadata)
    return AbstractResponse(
        session_id=mapper.session_id,
        abstract_code=abstract_code_value,
        metadata=metadata,
    )


@router.post("/api/v1/translate", response_model=TranslateResponse)
async def translate_response(request: TranslateRequest) -> TranslateResponse:
    mapper = BidirectionalMapper(session_id=request.session_id)
    try:
        mapper.load_encrypted()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="session not found") from exc

    translator = ReverseTranslator(mapper)
    symbols = translator.extract_abstract_symbols(request.llm_response)
    translated = translator.translate(request.llm_response)
    return TranslateResponse(translated_response=translated, symbols_replaced=len(symbols))


@router.post("/api/v1/translate-from-original", response_model=TranslateResponse)
async def translate_from_original(request: TranslateFromOriginalRequest) -> TranslateResponse:
    """
    Translate an LLM response back to the original source code
    without requiring the client to manage `session_id`.
    """
    try:
        validate_python_source(request.source_code)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    parser = ASTParser()
    analyzer = SemanticAnalyzer()
    generator = IRGenerator()
    mapper = BidirectionalMapper(privacy_level=request.privacy_level)
    tree = parser.parse(request.source_code)
    identifiers = parser.extract_identifiers(tree)
    classified = analyzer.classify_batch(identifiers)
    for item in classified:
        item["context"] = parser.get_context(request.source_code, item["line_number"])

    # Build mappings exactly as the LLM-side abstraction would.
    generator.generate(tree, classified)
    for item in classified:
        symbol = generator.symbol_map.get(item["name"])
        if symbol:
            mapper.add_mapping(symbol, item)

    metadata = {"identifier_count": len(classified), "symbol_count": len(mapper.mapping_table)}
    mapper.save_encrypted(request.source_code, metadata)

    translator = ReverseTranslator(mapper)
    symbols = translator.extract_abstract_symbols(request.llm_response)
    translated = translator.translate(request.llm_response)
    # Keep response model minimal for backward compatibility.
    return TranslateResponse(translated_response=translated, symbols_replaced=len(symbols))


@router.get("/api/v1/session/{session_id}")
async def get_session(session_id: str):
    session = load_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session not found")
    return {
        "session_id": session["session_id"],
        "created_at": session["created_at"],
        "privacy_level": session["privacy_level"],
        "metadata": session["metadata"],
    }


@router.get("/health")
async def health_check():
    return {"status": "healthy"}

