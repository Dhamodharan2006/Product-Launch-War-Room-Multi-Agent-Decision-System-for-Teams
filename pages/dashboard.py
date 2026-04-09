import streamlit as st
from components.decision_banner import show as show_decision
from utils.loader import extract_metrics_df

def show():
    st.title("Dashboard")
    
    if not st.session_state.data_loaded:
        st.info("No analysis data found. Go to Settings and run the analysis first.")
        if st.button("Go to Settings"):
            st.session_state.current_page = "Settings"
            st.rerun()
        return
    
    results = st.session_state.results
    
    # Metrics Row
    df = extract_metrics_df(results)
    if not df.empty:
        cols = st.columns(4)
        metrics = ["crash_rate", "payment_success_rate", "d1_retention", "feature_adoption"]
        for i, metric in enumerate(metrics):
            if metric in df.columns:
                latest = df[metric].iloc[-1]
                delta = latest - df[metric].iloc[0] if len(df) > 1 else 0
                cols[i].metric(metric.replace("_", " ").title(), 
                              f"{latest:.2f}", 
                              f"{delta:+.2f}")
    
    # Decision Banner
    show_decision(results.get("final_decision", {}))
    
    # Agent Cards
    st.subheader("Agent Findings")
    cols = st.columns(4)
    
    agents = [
        ("Data Analyst", results.get("data_analysis", {})),
        ("Product Manager", results.get("pm_analysis", {})),
        ("Marketing", results.get("marketing_analysis", {})),
        ("Risk/Critic", results.get("risk_analysis", {}))
    ]
    
    for i, (name, data) in enumerate(agents):
        with cols[i]:
            st.caption(name)
            if data:
                st.markdown(f"**{data.get('agent_role', name)}**")
                st.markdown(data.get('summary', '')[:100] + "...")
                risk = data.get('risk_score', 0)
                st.progress(risk, text=f"Risk: {risk:.2f}")
            else:
                st.text("No data")
    
    # Action Plan
    st.subheader("Action Plan (24-48h)")
    action_plan = results.get("final_decision", {}).get("action_plan", {}).get("next_24_48_hours", [])
    for action in action_plan:
        st.checkbox(f"{action.get('action')} (Owner: {action.get('owner')}, Due: {action.get('due_hours')}h)", 
                   key=f"action_{action.get('action')[:20]}")
    
    # Communication Plan
    st.subheader("Communications")
    comms = results.get("final_decision", {}).get("communication_plan", {})
    col1, col2 = st.columns(2)
    col1.info(f"**Internal:** {comms.get('internal', 'N/A')}")
    col2.warning(f"**External:** {comms.get('external', 'N/A')}")