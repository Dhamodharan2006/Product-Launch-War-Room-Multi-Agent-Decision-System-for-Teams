import streamlit as st

def show(decision_data):
    """Display decision banner with appropriate styling."""
    if not decision_data:
        return
        
    decision = decision_data.get("decision", "Unknown")
    confidence = decision_data.get("confidence_score", 0)
    rationale = decision_data.get("rationale", {})
    
    if decision == "Proceed":
        st.success(f"## Decision: {decision}")
    elif decision == "Pause":
        st.warning(f"## Decision: {decision}")
    elif decision == "Roll Back":
        st.error(f"## Decision: {decision}")
    else:
        st.info(f"## Decision: {decision}")
    
    st.metric("Confidence", f"{confidence:.0%}")
    
    with st.expander("Rationale"):
        for driver in rationale.get("key_drivers", []):
            st.markdown(f"• {driver}")