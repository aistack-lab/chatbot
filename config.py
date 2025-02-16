"""Configuration and constants for the Streamlit application."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

# Type aliases
ModelName: TypeAlias = str
SystemPrompt: TypeAlias = str

# Default values
DEFAULT_MODEL = "gpt-4-turbo-preview"
DEFAULT_SYSTEM_PROMPT = """
Du bist ein KI-Assistent der dabei hilft, Informationen zu strukturieren und zu analysieren.
Gib deine Antworten auf Deutsch.
"""


@dataclass
class FormData:
    """Data structure for form inputs."""

    title: str
    description: str
    requirements: str
    constraints: str
    additional_info: str


# Field descriptions for the form
FORM_FIELDS = {
    "title": "Titel des Projekts",
    "description": "Beschreibung",
    "requirements": "Anforderungen",
    "constraints": "Einschränkungen",
    "additional_info": "Weitere Informationen",
}
