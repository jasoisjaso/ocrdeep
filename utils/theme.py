import streamlit as st

def set_theme(theme_name):
    """
    Sets the Streamlit theme (dark/light) using custom CSS.
    """
    if theme_name == "dark":
        st.markdown(
            """
            <style>
            .stApp {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
                color: #FFFFFF;
            }
            .stTabs [data-baseweb="tab-list"] button {
                background-color: #333333;
                color: #FFFFFF;
            }
            .stTabs [data-baseweb="tab-list"] button:hover {
                background-color: #555555;
            }
            .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
                background-color: #007BFF;
                color: #FFFFFF;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else: # light theme
        st.markdown(
            """
            <style>
            .stApp {
                background-color: #FFFFFF;
                color: #333333;
            }
            .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
                color: #333333;
            }
            .stTabs [data-baseweb="tab-list"] button {
                background-color: #F0F2F6;
                color: #333333;
            }
            .stTabs [data-baseweb="tab-list"] button:hover {
                background-color: #CCCCCC;
            }
            .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
                background-color: #007BFF;
                color: #FFFFFF;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

def apply_custom_css():
    """
    Applies general custom CSS for a modern look and feel.
    """
    st.markdown(
        """
        <style>
        /* General styling */
        body {
            font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        }
        .reportview-container {
            background: #f0f2f6; /* Light theme default */
        }
        .main .block-container {
            padding-top: 2rem;
            padding-right: 2rem;
            padding-left: 2rem;
            padding-bottom: 2rem;
        }
        /* Header styling */
        h1, h2, h3, h4, h5, h6 {
            color: #007BFF;
        }
        /* Button styling */
        .stButton>button {
            background-color: #007BFF;
            color: white;
            border-radius: 5px;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .stButton>button:hover {
            background-color: #0056b3;
        }
        /* File uploader styling */
        .stFileUploader {
            border: 2px dashed #007BFF;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }
        /* Progress bar styling */
        .stProgress > div > div > div > div {
            background-color: #007BFF;
        }
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #f0f2f6;
            color: #007BFF;
            border-radius: 5px;
            padding: 10px;
            margin-top: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
