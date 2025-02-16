"""Second step of the workflow - Analysis and Chat."""

from __future__ import annotations

import asyncio
from typing import Any

import streamlit as st
from llmling_agent import Agent  # type: ignore

from config import FormData

SYSTEM_PROMPT = """\
Du bist ein KI-Assistent der dabei hilft,
Informationen zu strukturieren und zu analysieren.
"""


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
            st.session_state.system_prompt = SYSTEM_PROMPT

        st.session_state.system_prompt = st.text_area(
            "System Prompt", value=st.session_state.system_prompt, height=150
        )


def format_context(form_data: FormData) -> str:
    """Format the form data into a context string."""
    return f"""
    Projektinformationen:

    Titel: {form_data.title}

    Beschreibung:
    {form_data.description}

    Anforderungen:
    {form_data.requirements}

    Einschränkungen:
    {form_data.constraints}

    Weitere Informationen:
    {form_data.additional_info}
    """


async def process_chat_message(
    agent: Any,
    prompt: str,
    message_placeholder: st.delta_generator.DeltaGenerator,
) -> str:
    """Process a chat message and stream the response."""
    full_response = ""
    async with agent.run_stream(prompt) as stream:
        async for chunk in stream.stream():
            full_response += chunk
            message_placeholder.markdown(full_response)
    return full_response


async def main_async() -> None:
    """Async main function for Step 2."""
    st.title("Schritt 2: Analyse und Dialog")

    # Check if we have form data
    if "completed_form" not in st.session_state:
        st.error(
            "Keine Daten von Schritt 1 vorhanden. Bitte gehen Sie zurück zu Schritt 1."
        )
        if st.button("Zurück zu Schritt 1"):
            st.switch_page("pages/step1.py")
        return

    render_sidebar()

    # Initialize agent if not already done
    if "agent" not in st.session_state:
        st.session_state.agent = Agent[None](
            model=st.session_state.model, system_prompt=st.session_state.system_prompt
        )

    # Display form data as context
    with st.expander("Kontext aus Schritt 1", expanded=True):
        st.markdown(format_context(st.session_state.completed_form))

    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ihre Frage..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            # Get response from agent
            with st.chat_message("assistant"):
                message_placeholder = st.empty()

                # Add context to the first message
                if not st.session_state.messages[:-1]:
                    context = format_context(st.session_state.completed_form)
                    prompt = f"{context}\n\nFrage: {prompt}"

                # Stream the response
                with st.spinner("Denke nach..."):
                    full_response = await process_chat_message(
                        st.session_state.agent,
                        prompt,
                        message_placeholder,
                    )

                # Add assistant response to chat history
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )

        except Exception as e:
            error_msg = f"Ein Fehler ist aufgetreten: {str(e)}"
            st.error(error_msg)


def main() -> None:
    """Main entry point for Step 2."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
