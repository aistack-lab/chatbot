"""State management for the Streamlit application."""

from __future__ import annotations

from typing import Any

from crewai_tools import SerperDevTool
from llmling_agent import Agent, AnyAgent, ChatMessage, StructuredAgent, Tool
import streamlit as st

from config import FormData


SYS_PROMPT_STEP1 = """\
Du bist ein KI-Assistent der dabei hilft,
Informationen zu strukturieren und zu analysieren.
Extrahiere die relevanten Informationen aus dem Text
und strukturiere sie entsprechend der Vorgaben.
"""

SYS_PROMPT_STEP2 = """\
Du bist ein KI-Assistent der dabei hilft,
Informationen zu strukturieren und zu analysieren.
"""

MODEL_NAME = "gpt-4o-mini"
CHAT_AGENT_NAME = "Dieter"
FORM_AGENT_NAME = "Uschi"


class State:
    """Session state management."""

    async def initialize(self) -> None:
        """Initialize all agents."""
        if "agents" not in st.session_state:
            # Initialize form agent
            form_agent = Agent[None](
                name=FORM_AGENT_NAME,
                model=MODEL_NAME,
                system_prompt=SYS_PROMPT_STEP1,
            ).to_structured(FormData)
            await form_agent.__aenter__()

            # Initialize chat agent
            chat_agent = Agent[None](
                name=CHAT_AGENT_NAME,
                model=MODEL_NAME,
                system_prompt=SYS_PROMPT_STEP2,
            )
            search_tool = SerperDevTool()
            chat_agent.tools.register_tool(Tool.from_crewai_tool(search_tool))
            await chat_agent.__aenter__()

            st.session_state.agents = {
                form_agent.name: form_agent,
                chat_agent.name: chat_agent,
            }

        if "form_data" not in st.session_state:
            st.session_state.form_data = {field: "" for field in FormData.model_fields}

        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []

    @property
    def agents(self) -> dict[str, AnyAgent[Any, Any]]:
        """Get the agents dictionary, keyed by agent name."""
        return st.session_state.agents

    @property
    def form_agent(self) -> StructuredAgent[None, FormData]:
        """Get the session's form processing agent."""
        return st.session_state.agents[FORM_AGENT_NAME]

    @property
    def chat_agent(self) -> Agent[None]:
        """Get the session's chat agent."""
        return st.session_state.agents[CHAT_AGENT_NAME]

    @property
    def form_data(self) -> dict[str, str]:
        """Get the current form data."""
        return st.session_state.form_data

    @form_data.setter
    def form_data(self, value: dict[str, str]) -> None:
        """Set the current form data."""
        st.session_state.form_data = value

    @property
    def chat_messages(self) -> list[ChatMessage[Any]]:
        """Get the chat message history."""
        return st.session_state.chat_messages

    @property
    def completed_form(self) -> FormData:
        """Get the completed form data."""
        return st.session_state.completed_form


state = State()
