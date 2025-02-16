"""State management for the Streamlit application."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Final, TypeVar

import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

from config import DEFAULT_MODEL, DEFAULT_SYSTEM_PROMPT, FormData, ModelName, SystemPrompt


if TYPE_CHECKING:
    from llmling_agent import Agent, StructuredAgent

    from components.chat import Message


@dataclass
class GlobalState:
    """Application-wide state."""

    model: ModelName = DEFAULT_MODEL
    system_prompt: SystemPrompt = DEFAULT_SYSTEM_PROMPT


@dataclass
class Step1State:
    """State for step 1."""

    form_data: FormData = field(default_factory=FormData)
    structured_agent: StructuredAgent[None, FormData] | None = None


@dataclass
class Step2State:
    """State for step 2."""

    messages: list[Message] = field(default_factory=list)
    agent: Agent[None] | None = None


StateT = TypeVar("StateT")


class StateManager:
    """Manages both global and page-specific state."""

    GLOBAL_KEY: Final = "global_state"
    PAGE_KEY_PREFIX: Final = "page_state_"

    @classmethod
    def _get_current_page_id(cls) -> str:
        """Get the current page identifier from Streamlit context."""
        ctx = get_script_run_ctx()
        if not ctx:
            raise RuntimeError("No Streamlit context found")

        return Path(ctx.main_script_path).stem

    @classmethod
    def get_global_state(cls) -> GlobalState:
        """Get application-wide state."""
        if cls.GLOBAL_KEY not in st.session_state:
            st.session_state[cls.GLOBAL_KEY] = GlobalState()
        return st.session_state[cls.GLOBAL_KEY]

    @classmethod
    def get_page_state[T](cls, state_class: type[T]) -> T:
        """Get page-specific state."""
        page_id = cls._get_current_page_id()
        key = f"{cls.PAGE_KEY_PREFIX}{page_id}"

        if key not in st.session_state:
            st.session_state[key] = state_class()
        return st.session_state[key]

    @classmethod
    def update_global_state(cls, state: GlobalState) -> None:
        """Update the global state."""
        st.session_state[cls.GLOBAL_KEY] = state

    @classmethod
    def update_page_state[T](cls, state: T) -> None:
        """Update the current page's state."""
        page_id = cls._get_current_page_id()
        key = f"{cls.PAGE_KEY_PREFIX}{page_id}"
        st.session_state[key] = state

    @classmethod
    def clear_page_state(cls) -> None:
        """Clear the current page's state."""
        page_id = cls._get_current_page_id()
        key = f"{cls.PAGE_KEY_PREFIX}{page_id}"
        if key in st.session_state:
            del st.session_state[key]
