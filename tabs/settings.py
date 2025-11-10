import streamlit as st
import os
from utils.theme import set_theme
from utils.config import DEFAULT_THEME

def settings_tab():
    st.header("Settings")

    # Theme selection
    st.subheader("Theme")
    current_theme = st.session_state.get("theme", DEFAULT_THEME)
    
    theme_option = st.radio(
        "Choose your theme:",
        ("Dark", "Light"),
        index=0 if current_theme == "dark" else 1,
        key="theme_radio"
    )
    
    new_theme = theme_option.lower()
    if new_theme != current_theme:
        st.session_state["theme"] = new_theme
        set_theme(new_theme)
        st.experimental_rerun() # Rerun to apply theme immediately

    st.write(f"Current theme: {st.session_state.get('theme', DEFAULT_THEME).capitalize()}")

    # OCR Method Selection (Placeholder as per requirements)
    st.subheader("OCR Method")
    st.write("Current OCR Method: HuggingFace Local (Chandra OCR)")
    st.info("Advanced OCR method selection will be implemented in future updates.")

    # GPU Memory Settings (Placeholder)
    st.subheader("GPU Memory Settings")
    st.slider("Allocate GPU Memory (GB)", 1, 16, 8, step=1, key="gpu_memory_slider", disabled=True)
    st.info("GPU memory allocation is currently managed automatically by the system.")

    # Batch Size Configuration (Placeholder)
    st.subheader("Batch Size Configuration")
    st.slider("OCR Batch Size", 1, 8, 1, step=1, key="batch_size_slider", disabled=True)
    st.info("Batch size configuration is currently fixed for optimal performance.")

    # Processing Logs Viewer
    st.subheader("Processing Logs")
    log_file_path = "app.log" # Assuming logs are written to app.log in the root
    if os.path.exists(log_file_path):
        with open(log_file_path, "r") as f:
            logs = f.read()
        st.text_area("Application Logs", logs, height=300)
    else:
        st.info("No application logs found yet.")
