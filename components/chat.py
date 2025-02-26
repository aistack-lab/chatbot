"""Chat UI component for streamlit applications."""

from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st


if TYPE_CHECKING:
    from collections.abc import Callable

    from llmling_agent import Agent
    from streamlit.delta_generator import DeltaGenerator


Message = dict[str, str]


async def _stream_response(
    agent: Agent[None],
    prompt: str,
    placeholder: DeltaGenerator,
) -> str:
    """Stream the agent's response to a placeholder."""
    response_parts: list[str] = []
    async with agent.run_stream(prompt) as stream:
        async for chunk in stream.stream():
            placeholder.markdown(chunk)
            response_parts.append(chunk)
    return "".join(response_parts)


async def create_chat_ui(
    agent: Agent[None],
    *,
    messages_key: str = "messages",
    preprocess_first_message: Callable[[str], str] | None = None,
    placeholder_text: str = "Ihre Frage...",
    thinking_text: str = "Denke nach...",
) -> None:
    """Create a chat UI that integrates with page's session state.

    Args:
        agent: The agent to use for responses
        messages_key: Key in session state to store messages
        preprocess_first_message: Optional function to process the first message
        placeholder_text: Text to show in the input placeholder
        thinking_text: Text to show while processing
    """
    # Initialize messages in session state if not present
    if messages_key not in st.session_state:
        st.session_state[messages_key] = []

    # Display chat history
    for message in st.session_state[messages_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input(placeholder_text):
        # Add and display user message
        st.session_state[messages_key].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            # Process message through agent
            with st.chat_message("assistant"):
                message_placeholder = st.empty()

                # Preprocess first message if needed
                if (
                    not st.session_state[messages_key][:-1]
                    and preprocess_first_message is not None
                ):
                    prompt = preprocess_first_message(prompt)

                # Stream the response
                with st.spinner(thinking_text):
                    full_response = await _stream_response(
                        agent=agent,
                        prompt=prompt,
                        placeholder=message_placeholder,
                    )

                # Add assistant response to history
                st.session_state[messages_key].append({
                    "role": "assistant",
                    "content": full_response,
                })

        except Exception as e:  # noqa: BLE001
            error_msg = f"Ein Fehler ist aufgetreten: {e!s}"
            st.error(error_msg)


def clear_chat_history(messages_key: str = "messages") -> None:
    """Clear the chat history from session state.

    Args:
        messages_key: The key used to store messages in session state
    """
    if messages_key in st.session_state:
        st.session_state[messages_key] = []


if __name__ == "__main__":
    from llmling_agent import Agent

    from utils import run

    agent = Agent[None](model="gpt-4o-mini")
    coro = create_chat_ui(agent)
    run(coro)
