"""Pydantic API models."""

from typing import Dict

from pydantic import BaseModel


class AbstractRequest(BaseModel):
    source_code: str
    privacy_level: str = "MEDIUM"


class AbstractResponse(BaseModel):
    session_id: str
    abstract_code: str
    metadata: Dict


class TranslateRequest(BaseModel):
    session_id: str
    llm_response: str


class TranslateResponse(BaseModel):
    translated_response: str
    symbols_replaced: int


class TranslateFromOriginalRequest(BaseModel):
    source_code: str
    llm_response: str
    privacy_level: str = "MEDIUM"

