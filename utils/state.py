import streamlit as st

def init_state():
    """Initialize session state variables."""
    defaults = {
        "results": None,
        "data_loaded": False,
        "current_page": "Dashboard",
        "run_in_progress": False
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val