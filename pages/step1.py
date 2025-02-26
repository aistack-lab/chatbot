"""First step of the workflow - Information gathering."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import streamlit as st

from components.sidebar import render_sidebar
from components.state import state
from config import FORM_FIELDS, FormData


if TYPE_CHECKING:
    from llmling_agent import StructuredAgent
    from streamlit.runtime.uploaded_file_manager import UploadedFile


SYS_PROMPT = """\
Du bist ein KI-Assistent der dabei hilft,
Informationen zu strukturieren und zu analysieren.
Extrahiere die relevanten Informationen aus dem Text
und strukturiere sie entsprechend der Vorgaben.
"""

MODEL_NAME = "gpt-4o-mini"


def read_text_file(file: UploadedFile) -> str:
    """Read text content from uploaded file."""
    try:
        return file.read().decode("utf-8")
    except UnicodeDecodeError as e:
        error_msg = "Datei konnte nicht als UTF-8 Text gelesen werden."
        raise ValueError(error_msg) from e


async def process_upload(
    agent: StructuredAgent[None, FormData],
    content: str,
) -> FormData:
    """Process uploaded content through the agent."""
    result = await agent.run(content)
    return result.content


async def main_async() -> None:
    """Async main function for Step 1."""
    # Initialize form data in session state
    await state.initialize()
    agent = state.form_agent
    st.title("Schritt 1: Informationssammlung")
    render_sidebar(model_name=MODEL_NAME, sys_prompt=SYS_PROMPT)
    # File upload section
    help_text = "Laden Sie eine UTF-8 kodierte Textdatei hoch"
    uploaded_file = st.file_uploader("Text-Datei hochladen", type=["txt"], help=help_text)

    if uploaded_file is not None:
        try:
            content = read_text_file(uploaded_file)
            with st.spinner("Verarbeite Upload..."):
                result = await process_upload(agent, content)
                # Update form data with results
                state.form_data = result.model_dump()
                st.success("Datei erfolgreich verarbeitet!")
        except Exception as e:  # noqa: BLE001
            error_msg = f"Fehler beim Verarbeiten der Datei: {e!s}"
            st.error(error_msg)

    # Create form fields
    for field, label in FORM_FIELDS.items():
        state.form_data[field] = st.text_area(
            label, value=state.form_data[field], height=100
        )

    # Check if all fields are filled
    all_filled = all(bool(state.form_data[f].strip()) for f in FORM_FIELDS)

    # Next button
    label = "Weiter zu Schritt 2"
    if st.button(label, disabled=not all_filled, use_container_width=True):
        # Store the complete form data
        st.session_state.completed_form = FormData(**state.form_data)
        # Navigate to next page
        st.switch_page("pages/step2.py")


def main() -> None:
    """Main entry point for Step 1."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
