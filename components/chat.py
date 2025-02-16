"""Chat UI component for streamlit applications."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, AsyncIterator, Callable

import streamlit as st
from llmling_agent import Agent
from llmling_agent.models.tools import ToolCallInfo

if TYPE_CHECKING:
    from streamlit.delta_generator import DeltaGenerator

Message = dict[str, str]


async def _stream_response(
    stream: AsyncIterator[str],
    placeholder: DeltaGenerator,
) -> str:
    """Stream a response to a placeholder."""
    full_response = ""
    async for chunk in stream:
        full_response += chunk
        placeholder.markdown(full_response)
    return full_response


def _handle_tool_call(info: ToolCallInfo) -> None:
    """Handle tool call signals from the agent."""
    if "tool_messages" not in st.session_state:
        st.session_state.tool_messages = []

    st.session_state.tool_messages.append(info.format())


def _display_tool_calls() -> None:
    """Display tool calls in an expander."""
    if "tool_messages" in st.session_state and st.session_state.tool_messages:
        with st.expander("🔧 Tool Aufrufe", expanded=False):
            for msg in st.session_state.tool_messages:
                st.text(msg)


async def _process_message(
    agent: Agent[None],
    prompt: str,
    placeholder: DeltaGenerator,
    preprocess_message: Callable[[str], str] | None = None,
) -> str:
    """Process a chat message and stream the response."""
    if preprocess_message:
        prompt = preprocess_message(prompt)

    # Reset tool messages for this interaction
    st.session_state.tool_messages = []

    # Connect to the tool_used signal
    agent.tool_used.connect(_handle_tool_call)

    try:
        full_response = ""
        async with agent.run_stream(prompt) as stream:
            full_response = await _stream_response(stream.stream(), placeholder)

        # Display tool calls after the response
        _display_tool_calls()

        return full_response
    finally:
        # Cleanup: disconnect the signal
        agent.tool_used.disconnect(_handle_tool_call)


def create_chat_ui(
    agent: Agent[None],
    initial_message: str | None = None,
    preprocess_message: Callable[[str], str] | None = None,
) -> None:
    """Create a chat UI with message history and input field.

    Args:
        agent: The agent to use for chat responses
        initial_message: Optional initial message to display
        preprocess_message: Optional function to preprocess messages before sending
    """
    # Initialize message history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        if initial_message:
            st.session_state.messages.append(
                {"role": "assistant", "content": initial_message}
            )

    # Initialize tool messages if not exists
    if "tool_messages" not in st.session_state:
        st.session_state.tool_messages = []

    # Display chat history with associated tool calls
    for i, message in enumerate(st.session_state.messages):
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

                with st.spinner("Denke nach..."):
                    full_response = asyncio.run(
                        _process_message(
                            agent,
                            prompt,
                            message_placeholder,
                            preprocess_message,
                        )
                    )

                # Add assistant response to chat history
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )

        except Exception as e:
            error_msg = f"Ein Fehler ist aufgetreten: {str(e)}"
            st.error(error_msg)
