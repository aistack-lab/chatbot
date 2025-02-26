"""Configuration and constants for the Streamlit application."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class FormData(BaseModel):
    """Data structure for form inputs."""

    title: str = ""
    """Titel des Projekts"""

    description: str = ""
    """Beschreibung des Projekts"""

    requirements: str = ""
    """Anforderungen des Projekts"""

    constraints: str = ""
    """Einschränkungen des Projekts"""

    additional_info: str = ""
    """Weitere relevante Informationen"""

    model_config = ConfigDict(use_attribute_docstrings=True)


# Field descriptions for the form - matches FormData fields
FORM_FIELDS = {
    "title": "Titel des Projekts",
    "description": "Beschreibung",
    "requirements": "Anforderungen",
    "constraints": "Einschränkungen",
    "additional_info": "Weitere Informationen",
}
