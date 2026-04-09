import streamlit as st
import plotly.graph_objects as go
from utils.loader import extract_metrics_df

def show():
    st.title("Analysis")
    
    if not st.session_state.data_loaded:
        st.info("Run analysis first in Settings")
        return
    
    results = st.session_state.results
    df = extract_metrics_df(results)
    
    if df.empty:
        st.error("No metrics data")
        return
    
    # Metric Selector
    metric = st.selectbox("Select Metric", df.columns)
    
    # Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df[metric], mode='lines+markers', name=metric))
    
    # Highlight anomaly (max crash rate)
    if metric == "crash_rate":
        max_idx = df[metric].idxmax()
        fig.add_vline(x=max_idx, line_dash="dash", line_color="red", annotation_text="Anomaly")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistics
    st.subheader("Statistics")
    stats = {
        "Mean": df[metric].mean(),
        "Std Dev": df[metric].std(),
        "Min": df[metric].min(),
        "Max": df[metric].max(),
        "Current": df[metric].iloc[-1]
    }
    st.json(stats)
    
    # Conversation History
    st.subheader("Agent Conversation")
    for msg in results.get("conversation_history", []):
        with st.chat_message(msg.get("role", "system")):
            st.write(msg.get("content", "")[:200])