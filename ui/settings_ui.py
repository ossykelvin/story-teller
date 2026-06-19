import streamlit as st
from core.config import env, MODEL_KEYS, DEFAULT_PROVIDER, FALLBACK_PROVIDER
from agents.settings_agent import PROVIDER_OPTIONS


def render_settings():
    st.subheader("Settings")
    st.info("This MVP reads settings from `.env.local`. Edit that file to persist changes. Runtime selections below apply to the current session.")
    st.session_state.provider = st.selectbox("Provider", PROVIDER_OPTIONS, index=PROVIDER_OPTIONS.index(st.session_state.get("provider", DEFAULT_PROVIDER)))
    st.session_state.fallback_provider = st.selectbox("Fallback provider", PROVIDER_OPTIONS, index=PROVIDER_OPTIONS.index(st.session_state.get("fallback_provider", FALLBACK_PROVIDER)))
    st.write("### Current model values from `.env.local`")
    rows = []
    for purpose in MODEL_KEYS:
        rows.append({
            "purpose": purpose,
            "openrouter": env(f"OPENROUTER_{purpose.upper()}_MODEL", ""),
            "gemini": env(f"GEMINI_{purpose.upper()}_MODEL", ""),
        })
    st.dataframe(rows, use_container_width=True)
    st.write("### Storage")
    st.code("LOCAL_STORAGE_PATH, EXPORT_STORAGE_PATH and CUSTOM_STYLE_PATH are controlled in .env.local")
