"""Model selector component for streamlit applications."""

from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st

from utils import run


if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from tokonomics.model_discovery import ModelInfo, ProviderType


def model_selector(
    *,
    key_prefix: str = "model_selector",
    providers: Sequence[ProviderType] | None = None,
    on_change: Callable[[ModelInfo], None] | None = None,
    initial_model: str | None = None,
) -> ModelInfo | None:
    """Render a model selector with provider and model dropdowns.

    Args:
        key_prefix: Prefix for session state keys
        providers: List of providers to show models from
        on_change: Optional callback when selection changes
        initial_model: Model ID to select initially (matches pydantic_ai_id)

    Returns:
        Selected model info or None if not selected
    """
    # Fetch models
    from tokonomics.model_discovery import get_all_models_sync

    models = get_all_models_sync(providers=providers)

    # Get unique providers from models
    available_providers = sorted({model.provider for model in models})

    # Determine initial provider based on initial_model if provided
    initial_provider = None
    if initial_model:
        initial_model_info = next(
            (m for m in models if m.pydantic_ai_id == initial_model),
            None,
        )
        if initial_model_info:
            initial_provider = initial_model_info.provider

    # Provider selection
    provider_key = f"{key_prefix}_provider"
    if len(available_providers) > 1:
        # Use initial provider if found, otherwise first provider
        default_provider_idx = (
            available_providers.index(initial_provider)
            if initial_provider in available_providers
            else 0
        )

        selected_provider = st.selectbox(
            "Provider",
            options=available_providers,
            index=default_provider_idx,
            key=provider_key,
        )
    else:
        selected_provider = available_providers[0]

    # Filter models by selected provider
    provider_models = [m for m in models if m.provider == selected_provider]
    model_names = [m.name for m in provider_models]

    # Determine initial model index
    default_model_idx = 0
    if initial_model:
        # Find model with matching pydantic_ai_id in current provider's models
        matching_model = next(
            (
                idx
                for idx, m in enumerate(provider_models)
                if m.pydantic_ai_id == initial_model
            ),
            None,
        )
        if matching_model is not None:
            default_model_idx = matching_model

    # Model selection
    model_key = f"{key_prefix}_model"
    selected_name = st.selectbox(
        "Model",
        options=model_names,
        index=default_model_idx,
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


if __name__ == "__main__":
    run(model_selector)
