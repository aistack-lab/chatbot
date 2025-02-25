"""Sidebar component."""

from __future__ import annotations

import streamlit as st


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
