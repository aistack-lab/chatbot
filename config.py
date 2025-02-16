"""Configuration and constants for the Streamlit application."""

from __future__ import annotations

from typing import TypeAlias

from pydantic import BaseModel, Field

# Type aliases
ModelName: TypeAlias = str
SystemPrompt: TypeAlias = str

# Default values
DEFAULT_MODEL = "gpt-4-turbo-preview"
DEFAULT_SYSTEM_PROMPT = """
Du bist ein KI-Assistent der dabei hilft, Informationen zu strukturieren und zu analysieren.
Gib deine Antworten auf Deutsch.
"""


class FormData(BaseModel):
    """Data structure for form inputs."""

    title: str = Field(description="Titel des Projekts")
    description: str = Field(description="Beschreibung des Projekts")
    requirements: str = Field(description="Anforderungen des Projekts")
    constraints: str = Field(description="Einschränkungen des Projekts")
    additional_info: str = Field(description="Weitere relevante Informationen")


# Field descriptions for the form - matches FormData fields
FORM_FIELDS = {
    "title": "Titel des Projekts",
    "description": "Beschreibung",
    "requirements": "Anforderungen",
    "constraints": "Einschränkungen",
    "additional_info": "Weitere Informationen",
}
