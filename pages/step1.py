from __future__ import annotations

import streamlit as st

from config import FORM_FIELDS, FormData


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
            st.session_state.system_prompt = (
                "Du bist ein KI-Assistent der dabei hilft, "
                "Informationen zu strukturieren und zu analysieren."
            )

        st.session_state.system_prompt = st.text_area(
            "System Prompt", value=st.session_state.system_prompt, height=150
        )


def main() -> None:
    """Main function for Step 1."""
    st.title("Schritt 1: Informationssammlung")

    render_sidebar()

    # Initialize form data in session state
    if "form_data" not in st.session_state:
        st.session_state.form_data = {field: "" for field in FORM_FIELDS}

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


if __name__ == "__main__":
    main()
