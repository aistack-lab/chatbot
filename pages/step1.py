"""First step of the workflow - Information gathering."""

from __future__ import annotations

import asyncio
import io

import streamlit as st
from llmling_agent import Agent, StructuredAgent

from config import FORM_FIELDS, FormData

SYS_PROMPT = """\
Du bist ein KI-Assistent der dabei hilft,
Informationen zu strukturieren und zu analysieren.
Extrahiere die relevanten Informationen aus dem Text
und strukturiere sie entsprechend der Vorgaben.
"""


def read_text_file(file: io.BytesIO) -> str:
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


def render_sidebar() -> None:
    """Render the configuration sidebar."""
    with st.sidebar:
        st.title("Konfiguration")

        # Model selection
        if "model" not in st.session_state:
            st.session_state.model = "gpt-4-turbo-preview"

        st.session_state.model = st.text_input("Model", value=st.session_state.model)

        # System prompt
        if "system_prompt" not in st.session_state:
            st.session_state.system_prompt = SYS_PROMPT

        st.session_state.system_prompt = st.text_area(
            "System Prompt", value=st.session_state.system_prompt, height=150
        )


async def main_async() -> None:
    """Async main function for Step 1."""
    st.title("Schritt 1: Informationssammlung")

    render_sidebar()

    # Initialize form data in session state
    if "form_data" not in st.session_state:
        st.session_state.form_data = {field: "" for field in FORM_FIELDS}

    # Initialize agent
    if "structured_agent" not in st.session_state:
        st.session_state.structured_agent = Agent[None](
            model=st.session_state.model,
            system_prompt=st.session_state.system_prompt,
        ).to_structured(FormData)

    # File upload section
    uploaded_file = st.file_uploader(
        "Text-Datei hochladen",
        type=["txt"],
        help="Laden Sie eine UTF-8 kodierte Textdatei hoch",
    )

    if uploaded_file is not None:
        try:
            content = read_text_file(uploaded_file)
            with st.spinner("Verarbeite Upload..."):
                result = await process_upload(
                    st.session_state.structured_agent,
                    content,
                )
                # Update form data with results
                st.session_state.form_data = result.model_dump()
                st.success("Datei erfolgreich verarbeitet!")
        except Exception as e:
            error_msg = f"Fehler beim Verarbeiten der Datei: {str(e)}"
            st.error(error_msg)

    # Create form fields
    for field, label in FORM_FIELDS.items():
        st.session_state.form_data[field] = st.text_area(
            label, value=st.session_state.form_data[field], height=100
        )

    # Check if all fields are filled
    all_fields_filled = all(
        bool(st.session_state.form_data[field].strip()) for field in FORM_FIELDS
    )

    # Next button
    if st.button(
        "Weiter zu Schritt 2",
        disabled=not all_fields_filled,
        use_container_width=True,
    ):
        # Store the complete form data
        st.session_state.completed_form = FormData(**st.session_state.form_data)
        # Navigate to next page
        st.switch_page("pages/step2.py")


def main() -> None:
    """Main entry point for Step 1."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
