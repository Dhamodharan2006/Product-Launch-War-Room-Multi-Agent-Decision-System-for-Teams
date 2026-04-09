import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.loader import load_from_tracer
from utils.state import init_state

st.set_page_config(
    page_title="War Room — Product Launch Decision",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_state()

# Auto-load tracer if exists
if not st.session_state.data_loaded:
    results = load_from_tracer("outputs/tracer.json")
    if results:
        st.session_state.results = results
        st.session_state.data_loaded = True

# Sidebar
with st.sidebar:
    st.title("War Room")
    
    if st.session_state.data_loaded:
        st.success("Data loaded")
        st.caption(f"Run: {st.session_state.results.get('run_id', 'unknown')}")
    else:
        st.warning("No data — run analysis in Settings")
    
    page = st.radio("Navigation", 
                   ["Dashboard", "Analysis", "Feedback", "Settings"],
                   key="nav")
    
    st.divider()
    st.caption("Agents Status")
    agents = ["Data Analyst", "Product Manager", "Marketing", "Risk/Critic", "Coordinator"]
    for agent in agents:
        st.markdown(f"● {agent}")

# Route to pages
if page == "Dashboard":
    import pages.dashboard as dashboard
    dashboard.show()
elif page == "Analysis":
    import pages.analysis as analysis
    analysis.show()
elif page == "Feedback":
    import pages.feedback as feedback
    feedback.show()
elif page == "Settings":
    import pages.settings as settings
    settings.show()