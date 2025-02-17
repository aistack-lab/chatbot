"""State management for the Streamlit application."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Final, Self, TypeVar

from llmling_agent import Agent, StructuredAgent
import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

from config import DEFAULT_MODEL, DEFAULT_SYSTEM_PROMPT, FormData, ModelName, SystemPrompt


if TYPE_CHECKING:
    from components.chat import Message


@dataclass
class AppState:
    """True application-wide state, shared across all sessions."""

    form_agent: StructuredAgent[None, FormData] = field(
        default_factory=lambda: Agent[None](
            model=DEFAULT_MODEL,
            system_prompt=DEFAULT_SYSTEM_PROMPT,
        ).to_structured(FormData)
    )
    chat_agent: Agent[None] = field(
        default_factory=lambda: Agent[None](
            model=DEFAULT_MODEL,
            system_prompt=DEFAULT_SYSTEM_PROMPT,
        )
    )

    async def __aenter__(self) -> Self:
        """Initialize all agents."""
        await self.form_agent.__aenter__()
        await self.chat_agent.__aenter__()
        return self


@dataclass
class SessionState:
    """State scoped to a single session."""

    model: ModelName = DEFAULT_MODEL
    system_prompt: SystemPrompt = DEFAULT_SYSTEM_PROMPT


@dataclass
class Step1State:
    """State for step 1."""

    form_data: FormData = field(default_factory=FormData)


@dataclass
class Step2State:
    """State for step 2."""

    messages: list[Message] = field(default_factory=list)


StateT = TypeVar("StateT")


class StateManager:
    """Manages session and page-specific state."""

    SESSION_KEY: Final = "session_state"
    PAGE_KEY_PREFIX: Final = "page_state_"

    @classmethod
    @st.cache_resource
    async def get_app_state(cls) -> AppState:
        """Get the global application state."""
        state = AppState()
        return await state.__aenter__()

    @classmethod
    def get_session_state(cls) -> SessionState:
        """Get session-scoped state."""
        if cls.SESSION_KEY not in st.session_state:
            st.session_state[cls.SESSION_KEY] = SessionState()
        return st.session_state[cls.SESSION_KEY]

    @classmethod
    def get_page_state[T](cls, state_class: type[T]) -> T:
        """Get page-specific state."""
        page_id = cls._get_current_page_id()
        key = f"{cls.PAGE_KEY_PREFIX}{page_id}"

        if key not in st.session_state:
            st.session_state[key] = state_class()
        return st.session_state[key]

    @classmethod
    def _get_current_page_id(cls) -> str:
        """Get the current page identifier from Streamlit context."""
        ctx = get_script_run_ctx()
        if not ctx:
            msg = "No Streamlit context found"
            raise RuntimeError(msg)

        return Path(ctx.main_script_path).stem
