"""Second step of the workflow - Analysis and Chat."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from llmling_agent import Agent
import streamlit as st


if TYPE_CHECKING:
    from streamlit.delta_generator import DeltaGenerator

    from config import FormData


SYSTEM_PROMPT = """\
Du bist ein KI-Assistent der dabei hilft,
Informationen zu strukturieren und zu analysieren.
"""

MODEL_NAME = "gpt-4o-mini"


def render_sidebar() -> None:
    """Render the configuration sidebar."""
    with st.sidebar:
        st.title("Konfiguration")

        # Model selection
        if "model" not in st.session_state:
            st.session_state.model = MODEL_NAME

        st.session_state.model = st.text_input("Model", value=st.session_state.model)

        # System prompt
        if "system_prompt" not in st.session_state:
            st.session_state.system_prompt = SYSTEM_PROMPT

        st.session_state.system_prompt = st.text_area(
            "System Prompt",
            value=st.session_state.system_prompt,
            height=150,
        )


def format_context(form_data: FormData) -> str:
    """Format the form data into a context string."""
    return (
        "Projektinformationen:\n\n"
        f"Titel: {form_data.title}\n\n"
        f"Beschreibung:\n{form_data.description}\n\n"
        f"Anforderungen:\n{form_data.requirements}\n\n"
        f"Einschränkungen:\n{form_data.constraints}\n\n"
        f"Weitere Informationen:\n{form_data.additional_info}"
    )


async def process_chat_message(
    agent: Agent[None],
    prompt: str,
    message_placeholder: DeltaGenerator,
    is_first_message: bool = False,
) -> str:
    """Process a chat message and stream the response."""
    # Only add context for the first message
    if is_first_message:
        context = format_context(st.session_state.completed_form)
        full_prompt = f"{context}\n\nFrage: {prompt}"
    else:
        full_prompt = prompt

    response_parts: list[str] = []
    async with agent.run_stream(full_prompt) as stream:
        async for chunk in stream.stream():
            message_placeholder.markdown(chunk)
            response_parts.append(chunk)

    return "".join(response_parts)


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
        agent = Agent[None](
            model=st.session_state.model,
            system_prompt=st.session_state.system_prompt,
        )
        await agent.__aenter__()
        st.session_state.agent = agent
    else:
        agent = st.session_state.agent
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

                # Stream the response
                with st.spinner("Denke nach..."):
                    full_response = await process_chat_message(
                        st.session_state.agent,
                        prompt,
                        message_placeholder,
                        is_first_message=len(st.session_state.messages) <= 1,
                    )

                # Add assistant response to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                })

        except Exception as e:  # noqa: BLE001
            error_msg = f"Ein Fehler ist aufgetreten: {e!s}"
            st.error(error_msg)


def main() -> None:
    """Main entry point for Step 2."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
