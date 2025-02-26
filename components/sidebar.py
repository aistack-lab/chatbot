"""Sidebar component."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import streamlit as st

from components.model_selector import model_selector


if TYPE_CHECKING:
    from llmling_agent import AnyAgent
    from streamlit.delta_generator import DeltaGenerator
    from tokonomics.model_discovery import ModelInfo


def render_agent_config(
    agent: AnyAgent[Any, Any],
    container: DeltaGenerator | None = None,
) -> None:
    """Render agent configuration in any container.

    Args:
        agent: The agent to configure
        container: Optional container to render in (defaults to st)
    """
    # Use provided container or default to st
    st_container = container or st

    # Get or initialize config from session state
    def on_model_change(model: ModelInfo) -> None:
        """Handle model selection changes."""
        agent.set_model(model.pydantic_ai_id)

    _selected = model_selector(
        key_prefix="example",
        providers=["openrouter"],
        on_change=on_model_change,
        initial_model=agent.model_name,
    )

    # System prompt
    sys_prompt = agent.sys_prompts.prompts[0] if agent.sys_prompts.prompts else ""
    new_prompt = st_container.text_area("System Prompt", value=str(sys_prompt))
    if new_prompt != sys_prompt:
        sys_prompt = new_prompt
        # Update system prompt correctly
        agent.sys_prompts.prompts.clear()
        agent.sys_prompts.prompts.append(new_prompt or "")


def render_agent_sidebar(agent: AnyAgent[Any, Any]) -> None:
    """Render agent configuration in the sidebar.

    Args:
        agent: The agent to configure
    """
    with st.sidebar:
        st.title("Konfiguration")
        render_agent_config(agent, st.sidebar)
