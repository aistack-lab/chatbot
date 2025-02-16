"""Chat UI component for streamlit applications."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING

import streamlit as st


if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable

    from llmling_agent import Agent
    from llmling_agent.tools import ToolCallInfo
    from streamlit.delta_generator import DeltaGenerator

Message = dict[str, str]


@dataclass
class ChatState:
    """State for a chat instance."""

    messages: list[Message]
    tool_messages: list[str]


def _get_chat_states() -> defaultdict[str, ChatState]:
    """Get or initialize the chat states dictionary."""
    if "chat_states" not in st.session_state:
        st.session_state.chat_states = defaultdict(
            lambda: ChatState(messages=[], tool_messages=[])
        )
    return st.session_state.chat_states


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


def _handle_tool_call(agent_name: str, info: ToolCallInfo) -> None:
    """Handle tool call signals from the agent."""
    chat_states = _get_chat_states()
    chat_states[agent_name].tool_messages.append(info.format())


def _display_tool_calls(agent_name: str) -> None:
    """Display tool calls in an expander."""
    chat_states = _get_chat_states()
    if chat_states[agent_name].tool_messages:
        with st.expander("🔧 Tool Aufrufe", expanded=False):
            for msg in chat_states[agent_name].tool_messages:
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
    chat_states = _get_chat_states()
    chat_states[agent.name].tool_messages = []

    # Create a bound tool handler for this agent

    tool_handler = lambda info: _handle_tool_call(agent.name, info)

    # Connect to the tool_used signal
    agent.tool_used.connect(tool_handler)

    try:
        full_response = ""
        async with agent.run_stream(prompt) as stream:
            full_response = await _stream_response(stream.stream(), placeholder)

        # Display tool calls after the response
        _display_tool_calls(agent.name)

        return full_response
    finally:
        # Cleanup: disconnect the signal
        agent.tool_used.disconnect(tool_handler)


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
    chat_states = _get_chat_states()
    chat_state = chat_states[agent.name]

    # Initialize with initial message if provided and chat is empty
    if initial_message and not chat_state.messages:
        chat_state.messages.append({"role": "assistant", "content": initial_message})

    # Display chat history
    for message in chat_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ihre Frage..."):
        # Add user message to chat history
        chat_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            # Get response from agent
            with st.chat_message("assistant"):
                msg_placeholder = st.empty()

                with st.spinner("Denke nach..."):
                    coro = _process_message(
                        agent,
                        prompt,
                        msg_placeholder,
                        preprocess_message,
                    )
                    full_response = asyncio.run(coro)

                # Add assistant response to chat history
                msg = {"role": "assistant", "content": full_response}
                chat_state.messages.append(msg)

        except Exception as e:  # noqa: BLE001
            error_msg = f"Ein Fehler ist aufgetreten: {e!s}"
            st.error(error_msg)
