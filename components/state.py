from dataclasses import dataclass, field
from typing import Final

from llmling_agent import Agent, StructuredAgent

from components.chat import Message
from config import FormData


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


class StateManager:
    """Manages both global and page-specific state."""

    GLOBAL_KEY: Final = "global_state"
    PAGE_KEY_PREFIX: Final = "page_state_"

    @classmethod
    def get_page_state[T](cls, state_class: type[T]) -> T:
        """Get page-specific state."""
        page_id = cls._get_current_page_id()
        key = f"{cls.PAGE_KEY_PREFIX}{page_id}"

        if key not in st.session_state:
            st.session_state[key] = state_class()
        return st.session_state[key]
