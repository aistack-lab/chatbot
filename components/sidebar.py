"""Sidebar component."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import streambricks as sb
import streamlit as st


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

    if (
        selected_model := sb.model_selector(
            value=agent.model_name,
            providers=["openrouter"],
            expanded=False,
        )
    ) and selected_model.pydantic_ai_id != selected_model:
        agent.set_model(selected_model.pydantic_ai_id)

    # Add tool selector
    render_tool_selector(agent)

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


def render_tool_selector(agent: AnyAgent[Any, Any]) -> None:
    """Render tool selection for an agent in the sidebar.

    Args:
        agent: The agent for which to configure tools
    """
    from streambricks import MultiSelectItem, multiselect

    from components.state import state
    from config import create_issue_tool, search_jira_tool, search_tool

    # Define available tools as MultiSelectItems
    available_tools = [
        MultiSelectItem(
            label="Web Search",
            value=search_tool,
            description="Search the web for information",
        ),
        MultiSelectItem(
            label="Jira Search",
            value=search_jira_tool,
            description="Search for issues in Jira",
        ),
        MultiSelectItem(
            label="Jira Create Issue",
            value=create_issue_tool,
            description="Create a new issue in Jira",
        ),
    ]
    selected_items = multiselect(
        "Available Tools",
        available_tools,
        state_key=f"tools_{agent.name}",
        help_text="Select tools the agent can use",
    )
    selected_tools = [item.value for item in selected_items]
    state.agent_tools[agent.name] = selected_tools
    agent.tools.clear()  # Remove all existing tools
    for tool in selected_tools:
        agent.tools.register_tool(tool)
