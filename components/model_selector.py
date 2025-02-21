"""Model selector component for streamlit applications."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import streamlit as st
from tokonomics.model_discovery import ModelInfo, get_all_models


if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from tokonomics.model_discovery import ProviderType


def model_selector(
    *,
    key_prefix: str = "model_selector",
    providers: Sequence[ProviderType] | None = None,
    on_change: Callable[[ModelInfo], None] | None = None,
) -> ModelInfo | None:
    """Render a model selector with provider and model dropdowns.

    Args:
        key_prefix: Prefix for session state keys
        providers: List of providers to show models from
        on_change: Optional callback when selection changes

    Returns:
        Selected model info or None if not selected
    """
    # Fetch models
    models = asyncio.run(get_all_models(providers=providers))

    # Get unique providers from models
    available_providers = sorted({model.provider for model in models})

    # Provider selection
    provider_key = f"{key_prefix}_provider"
    if len(available_providers) > 1:
        selected_provider = st.selectbox(
            "Provider",
            options=available_providers,
            key=provider_key,
        )
    else:
        selected_provider = available_providers[0]

    # Filter models by selected provider
    provider_models = [m for m in models if m.provider == selected_provider]
    model_names = [m.name for m in provider_models]

    # Model selection
    model_key = f"{key_prefix}_model"
    selected_name = st.selectbox(
        "Model",
        options=model_names,
        key=model_key,
    )

    # Find selected model info
    selected_model = next(
        (m for m in provider_models if m.name == selected_name),
        None,
    )

    # Show model details in expander
    if selected_model:
        with st.expander("Model Details", expanded=True):
            st.markdown(selected_model.format())

        # Call on_change callback if provided
        if on_change:
            on_change(selected_model)

    return selected_model
