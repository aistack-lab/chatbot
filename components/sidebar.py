"""Sidebar component."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import streamlit as st


if TYPE_CHECKING:
    from llmling_agent import Agent
    from streamlit.delta_generator import DeltaGenerator


def render_sidebar(model_name: str, sys_prompt: str) -> None:
    """Render the configuration sidebar."""
    with st.sidebar:
        st.title("Konfiguration")

        # Model selection
        if "model" not in st.session_state:
            st.session_state.model = model_name

        st.session_state.model = st.text_input("Model", value=st.session_state.model)

        # System prompt
        if "system_prompt" not in st.session_state:
            st.session_state.system_prompt = sys_prompt

        st.session_state.system_prompt = st.text_area(
            "System Prompt",
            value=st.session_state.system_prompt,
            height=150,
        )


async def render_agent_config(
    agent: Agent[Any],
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
    state_key = f"agent_config_{agent.name}"
    if state_key not in st.session_state:
        new = await agent.sys_prompts.format_system_prompt(agent)
        st.session_state[state_key] = {"model": agent.model_name, "system_prompt": new}

    # Render configuration UI
    config = st.session_state[state_key]

    # Model selection
    new_model = st_container.text_input("Model", value=config["model"])
    if new_model != config["model"]:
        config["model"] = new_model
        agent.set_model(new_model)

    # System prompt
    new_prompt = st_container.text_area("System Prompt", value=config["system_prompt"])
    if new_prompt != config["system_prompt"]:
        config["system_prompt"] = new_prompt
        # Update system prompt correctly
        agent.sys_prompts.clear()
        agent.sys_prompts.prompts.append(new_prompt or "")


async def render_agent_sidebar(agent: Agent[Any]) -> None:
    """Render agent configuration in the sidebar.

    Args:
        agent: The agent to configure
    """
    with st.sidebar:
        st.title("Konfiguration")
        await render_agent_config(agent, st.sidebar)
