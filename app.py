import streamlit as st
from utils.theme import set_theme, apply_custom_css
from utils.config import DEFAULT_THEME
from tabs.deduction_splitter import deduction_splitter_tab
from tabs.invoice_extractor import invoice_extractor_tab
from tabs.settings import settings_tab
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    st.set_page_config(layout="wide", page_title="Chandra OCR App", page_icon="📄")

    # Initialize theme in session state if not present
    if "theme" not in st.session_state:
        st.session_state["theme"] = DEFAULT_THEME
    
    # Apply custom CSS and theme
    apply_custom_css()
    set_theme(st.session_state["theme"])

    st.title("Chandra OCR Document Processing")

    tab1, tab2, tab3 = st.tabs(["Deduction Form Splitter", "Invoice Extractor", "Settings"])

    with tab1:
        deduction_splitter_tab()
    with tab2:
        invoice_extractor_tab()
    with tab3:
        settings_tab()

if __name__ == "__main__":
    main()
